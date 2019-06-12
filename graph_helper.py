import requests
from .tables import get_user_acces_token
from .__init__ import DEBUG


def refresh_subscription(subscription_id):
    pass

def get_file_content(user_id,file_id):
    print("entered get file content")
    if (DEBUG):
        access_token = 'EwB4A8l6BAAURSN/FHlDW5xN74t6GzbtsBBeBUYAAdCHU9DkbQgaXfqgVeoudCRe2yIIJJsieEtX2nxd7KHbiNmZVVPvMX+hrPoiDhxhZZhShqA/D3NcR4X+Aypp4UgTnHuLpuDUObh1/uwzfZAeQ5g7583DE8CKj4aLfeI/EyGfWmnegGT23qF+AjRdrA13sILt0OtAuyZmoC4SsLLPbeRsEPO7vaGOVWhxBxjKeSJlKW6FJw4JVKSuTFOylIViXDOmO8s2mYKI36T4sFFJU0lZfKy20x4oW/BR/yXsFhvzg9x1zXGUFhZrAOk9J2JTboyboIen3GW6WMAEspxZWHPGoGjmfKmgWn6UEYdaai9QCuWKr4pNtOn//Rl3PYEDZgAACLxG/pShEOcPSAK0GnDBW64PfgEjKRMsPv7KeRWEp9IguaNegjC/h8wEQTP2h1JUYCWXow3xyqsAeh+ngJ99nxApCzgeUv8o2mLbyB7R1ByC3BE92rKpwUq5Cp+6i44QmDrpR4Lx7ySZOtBamhNYsMQsdb1ONiEbM2lvwD0Eg+hvyrK/GvqU61fjp2k4ojxesxOguPkmp2MFvkqa6GunZsRGT0UmbtaWqk6EA8bqKju3V9PaVeld79QDafs0gPjlztLaZoRh8ZVwTfeNtjtNFQ+ZuGY89ePPQFGvc6ea7ChKDgDgiwR2uXWXAMG5qYdbmhwJ2iJCDZTqQXZdOhYPMQfNPSJXSUs3eGcRSjudeU6Cu1/cioaSquB0Rk6teO8vqa1cVxJXSHsM3uljjgrDG5pM/mtrP4SahYm0Q9jCO2EKhVdmeB0vAcE+im561izSKKJrkclJJSsBfBc98+u7hVK3FyRzMT9ByNEkubcSxCfXRRk4/x/LlTEEv1bQ1d6Cx0X0VoLohtwkmZJy3tVgBuyql59y0GiFwUpTDgaW7tNz3tBOiKpqpXq/fZgZ35mRpucj9ZzUqReYLgWy5x9Ow/FfqQjlUZMTCHVD55iv0MyuTWc0lwvEWLleGqtlCSlny85qW68VtFt5eCoBu/Oi6g4QZE/TSIB9NlmGuNoqnJYn4HB09prr0gwJa8NpweFe7CIZ0SCdYVHsuz9z3BQJV+C6GFX+ooxL0YxyyD7p+xtd9JTmHZz204BQO+Ql+y/gCRx9HEsAI3ZyEbc0hXfggdzBxJQC'
        headers = {
            "Authorization": 'Bearer ' + access_token,
            # "Host": "graph.microsoft.com",
            # "Content-Type": "application/octet-stream"
        }
    else:
        headers = {
            "Authorization": 'Bearer ' + get_user_acces_token(user_id),
            #"Content-Type": "text/plain"
        }
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/items/{file_id}/content"
    r = requests.get(url=url,headers=headers)
    if r.status_code == 200:
        file = r.content #check if this is correct
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
