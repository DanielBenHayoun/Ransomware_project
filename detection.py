
import yagmail
from .entropy import shannon_entropy as calc_entropy
from .tables import insert_new_file_to_db, is_honeypot, set_file_entropy_in_db,delete_file_from_db, is_file_in_db, get_file_entropy_from_db, get_user_microsoft_id, get_user_acces_token
from .graph_helper import get_file_content,get_user_email
from .__init__ import DEBUG
from . import extensions
import logging

def calculate_buffers(extension_buffer , content_buffer, entropy_buffer ,files_num):
	res=(extension_buffer+content_buffer+entropy_buffer)/files_num
	logging.info(f'calculate_buffer {res}')
	return res


def get_changed_entropy(user_id, file_id):
	old_entropy = get_file_entropy_from_db(user_id, file_id)
	print(f"old entropy = {old_entropy}")
	file_content = get_file_content(user_id, file_id)
	new_entropy = calc_entropy(file_content)
	print(f"new entropy = {new_entropy}")
	print (f"changed entropy = {abs(new_entropy - old_entropy)}")

	return abs(new_entropy - old_entropy)

def remove_deleted_files_from_changed_list(user_id,changed_list):
	i = 0
	indices_to_remove = []
	# list of files contains tuples of file id & deleted state (true/false)
	for tup in changed_list:
		file_id = tup[0]
		deleted = tup[1]
		if deleted == True:
			delete_file_from_db(file_id, str(user_id))
			indices_to_remove.append(i)
		i+=1

	for idx in indices_to_remove:
		changed_list.pop(idx)


def get_list_of_changed_updated_files(changed_list):
	new_list = []
	for tup in changed_list:
		new_list.append(tup[0])
	return new_list


def send_email_to_user(email):
	username = 'bhkshield@gmail.com'
	password = 'qtfrlvvbuksljubh'
	receiver = email
	yagmail.SMTP(username, password).send(receiver, 'Ransomware Project: Security warning!','A suspicion to a ransomware has been detected in your OneDrive.')


def check_files_blacklisted_per_user(user_id, list_changed_file_ids):
	logging.info('entered check_files_blacklisted_per_user')
	under_attack = False
	extention_buffer=0
	entropy_buffer=0
	content_buffer=0

	potential_dangerous_files = 0

	if (len(list_changed_file_ids) == 0):
		logging.info('no changed files')
		return False
	logging.info(f'there is {len((list_changed_file_ids))} changed files')
	for file_id in list_changed_file_ids:
		file_inspected = False

		# if file is honeypot, we are under attack
		if (is_honeypot(user_id,file_id) == True):
			logging.info('honeypot changed')
			return True

		#if file content is dangerous, we are under attack
		if (extensions.is_file_content_dangerous(user_id,file_id)):
			logging.info('file content is dangerous')
			content_buffer+=5
			#return True

		if (is_file_in_db(file_id,user_id) == False):
			logging.info('new file')
			# file was not in db before, new to drive
			content = get_file_content(user_id,file_id)
			file_entropy = calc_entropy(content)
			file_extension = extensions.get_file_extension(user_id,file_id)
			insert_new_file_to_db(file_id,user_id,file_entropy,file_extension)
			if(extensions.is_file_blacklisted(user_id,file_id)):
				logging.info('new file has bad extension')
				extention_buffer+=5
		else:
			# file was already in drive
			# derive information from extensions
			logging.info('updated file')
			current_extension = extensions.get_file_extension(user_id,file_id)
			extension_changed = extensions.is_file_extension_changed(user_id,file_id,current_extension) #bool
			extension_blacklisted = extensions.is_file_blacklisted(user_id,file_id) #bool
			temp_entropy=get_changed_entropy(user_id, file_id)
			# check if current file's extension is blacklisted
			if (extension_changed and extension_blacklisted):
				logging.info('updated file has bad extension')
				potential_dangerous_files += 1
				file_inspected = True
				under_attack = True
				extention_buffer+=2
			#Deniel change: we will accumulate the entropy anyway
			#if (temp_entropy > 0.01):
				#under_attack = True
			logging.info(f'updated file has a entropy {temp_entropy}')
			entropy_buffer+=temp_entropy
			if (file_inspected == False):
				potential_dangerous_files += 1
			# else:
			# 	#update entropy in database
			# 	set_file_entropy_in_db(user_id,file_id,calc_entropy(get_file_content(user_id,file_id)))
				set_file_entropy_in_db(user_id, file_id, calc_entropy(get_file_content(user_id, file_id)))

	# if (potential_dangerous_files > 5):
	# 	return True
	logging.info(f'extension buffer = {extention_buffer}')
	logging.info(f'content buffer = {content_buffer}')
	logging.info(f'entropy buffer = {entropy_buffer}')
	logging.info(f'potential dangerous files = {potential_dangerous_files}')
	if (potential_dangerous_files == 0):
		return False
	if (calculate_buffers(extention_buffer,content_buffer,entropy_buffer,potential_dangerous_files) > 0.7):
		return True
	return False

def detect(users_to_changed_files_map):

	#pass on each user and analyze his/her changed files
	for user_id in users_to_changed_files_map:
		list_of_files = users_to_changed_files_map[user_id]
		remove_deleted_files_from_changed_list(user_id,list_of_files)
		list_of_file_ids = get_list_of_changed_updated_files(list_of_files)
		print (list_of_file_ids)

		if (len(list_of_file_ids) == 0):
			print("EVERYTHING IS OKAY")
			continue

		# list of files contains tuples of file id & deleted state (true/false)

		under_attack = check_files_blacklisted_per_user(user_id,list_of_file_ids)
		if (under_attack):
			token = None
			if (DEBUG):
				token = "EwBwA8l6BAAURSN/FHlDW5xN74t6GzbtsBBeBUYAAfcRRYowDdVZ+3RiJHJwa+1Qpe3LJl0pELVeUDTlZhM5s3iaH1iictPsAr/YIwt0xQLPA+qDE+hvsjdfmJYwR6uQmZQ9EONzgrydh6FNtWmEYIN0C58WgPq97VCQvTAu+7ngaqjWrEzYMCccBhOaVy3Wem/hZCmQ9nQUctkF+jvR4Z1yx6T+SDWcvWUugOv4or5ZmePytBOJHAvjPzK+XWHc4boXb7FHYykoNCXQ6PrF0H74RvJ5DOikMb95euaURYqoIGglpbmfXyygaxNDlXhHwyPxF7oBkDkURydXLrGvowPi/1npG2+btOzf2wv48Z8SuUJ3YhpeLH4UnXlxM5ADZgAACDXeEO29FmmYQAKfut0CDEmX3Ive2OOZ2cu7bqCwgGUcGHcHYB7o6tGx4Ioj2FX+Jysoz2mc5Eiwqp9kWtHiHFPjzCnkRzv6DdKNSZKtKcWDdHN57NYPCVbDIYsm7nKom5wosV5UjZgALDVsM4EX3oAjsWackLOExhdYIuvealic+B/8OLcQnLl8TWPL6uMtdbXC0LWsVcq0OXeQSB8msG2S0KL7fF1QITHWorFHEAxaI1ScvZnHATOFTQmUfx1yq9zAxankW0mlOyHFxr+zHRkFu9Dg0jL66YyjWlBPrtN6zlK3fRsdUX3+2R8n6Mr//HSflrtshDFT0tQZNhW0fCY4o0mxuHvtIcrIytozqjayTGDcV3cM0nGrk6fZDi0UkIZ98R3dTbxqdx6H+pYp4OPNyMiwqfWyraumRLLlbGKxofrOQSPuDkZ7DgzbHpr0GgX3ct/+jaSvS3R0P4cHlcyY4aOtGf0eHmQvb/qYVviBzimdGYm6hDw/nk95aq5ard10zfY6rsy7AB9YG26TS0lZyHhT0vshOVOGc5DIkE32OREmbvpP3ZdmAfRQOmoHpjSdgHjNJAya2WNJ6j9vuK0Y2rblOfe/WI03deLtnx6OU7g04HaK/n06FGA6UIAYUfm/gOmO1zu5dWWVPvSZkYbt/V63RDFtAdmy3sLQ4w+Gk+q4wzh/L/mOWOwWWxsGPrpZdIeDkJa1RfCYIWyOq1r+7hIbyi1Su46/fdnpIPdh9BkreEOE+hldUYxaHDbuk+97cufp2MJ49NWPAg=="
			else:
				token = get_user_acces_token(user_id)
			# send_email to user
			user_email = get_user_email(user_id,token)
			send_email_to_user(user_email)
			print("RANSOMWARE DETECTED!!!")
		else:
			print("EVERYTHING IS OKAY")
