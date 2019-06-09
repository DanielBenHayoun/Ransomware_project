import requests


def refresh_token(user_id):
    pass

def refresh_subscription(subscription_id):
    pass


def get_file_content(user_id,file_id,access_token):
    headers = {
        "Authorization": 'Bearer ' + access_token,
        "Host": "graph.microsoft.com",
        "Content-Type": "application/json"
    }
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/items/{file_id}/content"
    r = requests.get(url=url,headers=headers)

    if r.status_code == 200:
        file = r.json() #check if this is correct
        return file
    return None


def get_user_email(user_id,access_token):
    headers = {
        "Authorization": 'Bearer ' + access_token,
        "Content-Type": "application/json"
    }

    url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
    r = requests.get(url = url, headers = headers)
    if r.status_code == 200:
        return r.json()["mail"]
    return None