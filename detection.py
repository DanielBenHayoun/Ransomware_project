import psycopg2
import yagmail
from .entropy import shannon_entropy as calc_entropy
import azure.functions as func
from .tables import insert_new_file_to_db, delete_file_from_db, get_file_entropy_from_db, get_user_microsoft_id, get_user_acces_token
from .graph_helper import get_file_content,get_user_email
from .__init__ import DEBUG


def detect(users_to_changed_files_map):
	if (len(users_to_changed_files_map) == 0):
		return

	#pass on each user and analyze his/her changed files
	for user_id in users_to_changed_files_map:
		list_of_files = users_to_changed_files_map[user_id]
		if (DEBUG):
			token = "EwBwA8l6BAAURSN/FHlDW5xN74t6GzbtsBBeBUYAAfcRRYowDdVZ+3RiJHJwa+1Qpe3LJl0pELVeUDTlZhM5s3iaH1iictPsAr/YIwt0xQLPA+qDE+hvsjdfmJYwR6uQmZQ9EONzgrydh6FNtWmEYIN0C58WgPq97VCQvTAu+7ngaqjWrEzYMCccBhOaVy3Wem/hZCmQ9nQUctkF+jvR4Z1yx6T+SDWcvWUugOv4or5ZmePytBOJHAvjPzK+XWHc4boXb7FHYykoNCXQ6PrF0H74RvJ5DOikMb95euaURYqoIGglpbmfXyygaxNDlXhHwyPxF7oBkDkURydXLrGvowPi/1npG2+btOzf2wv48Z8SuUJ3YhpeLH4UnXlxM5ADZgAACDXeEO29FmmYQAKfut0CDEmX3Ive2OOZ2cu7bqCwgGUcGHcHYB7o6tGx4Ioj2FX+Jysoz2mc5Eiwqp9kWtHiHFPjzCnkRzv6DdKNSZKtKcWDdHN57NYPCVbDIYsm7nKom5wosV5UjZgALDVsM4EX3oAjsWackLOExhdYIuvealic+B/8OLcQnLl8TWPL6uMtdbXC0LWsVcq0OXeQSB8msG2S0KL7fF1QITHWorFHEAxaI1ScvZnHATOFTQmUfx1yq9zAxankW0mlOyHFxr+zHRkFu9Dg0jL66YyjWlBPrtN6zlK3fRsdUX3+2R8n6Mr//HSflrtshDFT0tQZNhW0fCY4o0mxuHvtIcrIytozqjayTGDcV3cM0nGrk6fZDi0UkIZ98R3dTbxqdx6H+pYp4OPNyMiwqfWyraumRLLlbGKxofrOQSPuDkZ7DgzbHpr0GgX3ct/+jaSvS3R0P4cHlcyY4aOtGf0eHmQvb/qYVviBzimdGYm6hDw/nk95aq5ard10zfY6rsy7AB9YG26TS0lZyHhT0vshOVOGc5DIkE32OREmbvpP3ZdmAfRQOmoHpjSdgHjNJAya2WNJ6j9vuK0Y2rblOfe/WI03deLtnx6OU7g04HaK/n06FGA6UIAYUfm/gOmO1zu5dWWVPvSZkYbt/V63RDFtAdmy3sLQ4w+Gk+q4wzh/L/mOWOwWWxsGPrpZdIeDkJa1RfCYIWyOq1r+7hIbyi1Su46/fdnpIPdh9BkreEOE+hldUYxaHDbuk+97cufp2MJ49NWPAg=="
		else:
			token = get_user_acces_token(user_id)

		for tup in list_of_files:
			file_id = tup[0]
			deleted = tup[1]
			if deleted == True:
				delete_file_from_db(file_id, str(user_id))
				continue

			if (DEBUG):
				old_entropy = 10
				new_entropy = 11

			else:
				old_entropy = get_file_entropy_from_db(user_id,file_id)

				file_content = get_file_content(user_id, file_id, token)
				new_entropy = calc_entropy(file_content)

			if (abs(new_entropy - old_entropy) > 0.01):
				# send email of ransomware
				if (DEBUG):
					user_email = "kidneythief14@gmail.com"
				else:
					user_email = get_user_email(user_id,token)
				#send_email(user_email)
				print("Entropy changed")



def send_email(email):
	username = 'bhkshield@gmail.com'
	password = 'qtfrlvvbuksljubh'
	receiver = email
	yagmail.SMTP(username, password).send(receiver, 'Security warning!','A suspicion to a ransomware has been detected in your OneDrive.')



