import requests
from .tables import get_user_acces_token, get_file_extension_from_db
from .graph_helper import get_file_content

ransomware_extension_blacklist = [".ecc", ".ezz", ".exx", ".zzz", ".xyz",
                                  ".aaa", ".abc", ".ccc", ".vvv", ".xxx",
                                  ".ttt", ".micro", ".encrypted",
                                  ".locked", ".crypto", "_crypt", ".crinf",
                                  ".r5a", ".XRNT", ".XTBL", ".crypt",
                                  ".R16M01D05",
                                  ".pzdc", ".good", ".LOL!", ".OMG!",
                                  ".RDM", ".RRK", ".encryptedRSA",
                                  ".crjoker",
                                  ".EnCiPhErEd", ".LeChiffre",
                                  ".keybtc@inbox_com", ".0x0", ".bleep",
                                  ".1999", ".vault",
                                  ".HA3", ".toxcrypt", ".magic",
                                  ".SUPERCRYPT", ".CTBL", ".CTB2",
                                  ".locky", ".spartan", ".fang", ".gpg"]

ransomware_files = ["RECOVERY_KEY.txt", "HELP_RESTORE_FILES.txt",
                    "HELP_RECOVER_FILES.txt", "HELP_TO_SAVE_FILES.txt",
                    "DecryptAllFiles.txt",
                    "DECRYPT_INSTRUCTIONS.TXT",
                    "INSTRUCCIONES_DESCIFRADO.TXT",
                    "How_To_Recover_Files.txt",
                    "YOUR_FILES.HTML", "YOUR_FILES.url",
                    "encryptor_raas_readme_liesmich.txt",
                    "Help_Decrypt.txt", "DECRYPT_INSTRUCTION.TXT",
                    "HOW_TO_DECRYPT_FILES.TXT",
                    "ReadDecryptFilesHere.txt", "Coin.Locker.txt",
                    "secret_code.txt", "About_Files.txt",
                    "DECRYPT_ReadMe.TXT", " DecryptAllFiles.txt",
                    "FILESAREGONE.TXT", "IAMREADYTOPAY.TXT",
                    "HELLOTHERE.TXT", "READTHISNOW!!!.TXT",
                    "SECRETIDHERE.KEY",
                    "IHAVEYOURSECRET.KEY", "SECRET.KEY",
                    "HELP_DECYPRT_YOUR_FILES.HTML",
                    "help_decrypt_your_files.html",
                    "HELP_TO_SAVE_FILES.txt", "RECOVERY_FILES.txt",
                    "RECOVERY_FILE.TXT", "RECOVERY_FILE_",
                    "Howto_RESTORE_FILES_.txt", "Howto_Restore_FILES.txt",
                    "howto_recover_file_.txt", "restore_files_.txt",
                    "how_recover.txt", "recovery_file_.txt",
                    "recover_file_.txt", "recovery_file",
                    "Howto_Restore_FILES.TXT", "help_recover_instructions",
                    "_Locky_recover_instructions.txt", "HELP_DECRYPT.TXT",
                    "HELP_YOUR_FILES.TXT",
                    "HELP_TO_DECRYPT_YOUR_FILES.txt"]

compressed_file_extensions = [".arc", ".arj", ".bz", ".gz", ".iso", ".pak",
                              ".rar",
                              ".tar.gz", ".tgz", ".z", ".zip", ".zipx",
                              ".zoo"]


def get_extension_from_name(file_name):
    if ('.' not in file_name):
        return None
    file_name_length = len(file_name)
    i = file_name_length - 1
    ext = ''
    while (file_name[i] != '.'):
        ext = file_name[i] + ext
        i -= 1
    return ext

def get_file_extension(user_id,file_id):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/drive/items/{file_id}'
    headers = {
        "Authorization": 'Bearer ' + get_user_acces_token(user_id),
        "Content-Type": "application/json"
    }
    r = requests.get(url=url, headers=headers)
    if (r.status_code == 200):
        file_name = r.json()["name"]
        return get_extension_from_name(file_name)



def is_file_blacklisted(user_id, file_id):
    return get_file_extension(user_id,file_id) in ransomware_extension_blacklist



def is_file_ransomware_file(user_id, file_id):
    return get_file_extension(user_id,file_id) in ransomware_files



def is_file_compressed(user_id, file_id):
    return get_file_extension(user_id,file_id) in compressed_file_extensions



def is_file_content_dangerous(user_id, file_id):
    #not sure about this if, may need to delete
    if (is_file_ransomware_file(user_id, file_id)):
        file_content = get_file_content(user_id, file_id)
        file_content = file_content.lower()
        if ("encrypt" in file_content or "decrypt" in file_content or "mining" in file_content or "rsa" in file_content or "aes" in file_content or "pk" in file_content):
            return True
    return False


def is_file_extension_changed(user_id,file_id,new_ext):
    old_ext = get_file_extension_from_db(user_id,file_id)
    if (old_ext == new_ext):
        return False
    return True
