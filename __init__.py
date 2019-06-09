import logging
import azure.functions as func
from . import detection
import requests
from .tables import get_user_microsoft_id, get_user_acces_token, refresh_token
from requests_oauthlib import OAuth2Session


#debugging global variable
DEBUG = True

def get_subscription_ids_from_json(notification_json):
    sub_list = []

    # Set fields:
    # subscription_id , change_type , file_id
    for notification in notification_json["value"]:
        if (notification["subscriptionId"] in sub_list):
            continue
        sub_list.append(notification["subscriptionId"])

    return sub_list


def get_changed_files_ids(delta_json):
    changed_files = []

    for entry in delta_json["value"]:
        if "folder" in entry:
            continue
        file_id = entry["id"]
        deleted = False
        if "deleted" in entry:
            deleted = True
        changed_files.append((file_id,deleted))

    return changed_files



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    validation_string = req.params.get('validationToken')

    if validation_string:
        return func.HttpResponse(validation_string,status_code=200)
    else:
        # return func.HttpResponse(
        #      "Could not retrieve token",
        #      status_code=400
        # )

        #logging.info(f'json: {req.get_json()}')
        notification_json = req.get_json()
        subscription_ids_in_notification = []

        # get all the subscription ids that got notified in the json file
        if notification_json:
            subscription_ids_in_notification = get_subscription_ids_from_json(notification_json)

        # mapping user_id to a list of changed files in this user's OneDrive
        users_to_changed_files_map = {}

        for i in range(len(subscription_ids_in_notification)):
            subscription_id = subscription_ids_in_notification[i]
            logging.info(f'{subscription_id}')

            if (DEBUG):
                #sub_id = '436a2f68-b47d-4e95-963e-987039bae319'
                user_id = '3e3995e55bfc680d' #ayelet
                access_token = 'EwB4A8l6BAAURSN/FHlDW5xN74t6GzbtsBBeBUYAAdlLl0zOH6MslxmsnsCoCGHTUQ9dYgv26PUqMtRKyXVJzAtA79n1rAJOUBW6Xgl3xcrT3Mr/DrGeoYD6czPA6hOfcvR4aMIoYsHD6V9vQEM5Bk8Wgl+RW4u56rrqMJcTikKyNpHKuyM5qRQWXgMM8Lb9PRLJa2KYw0Whz434Tdp5Bp1DjjUhyXAbeeSmjvyzwcrkv1ak0cjjk4PG6HXhZqYpx4f+7yt0K2gDdONd7fzTu4mxPNrmeAeRnNfxgNeSYak1yYnqTmtsmrSDZjvgnyMwIC3emlPtk74Xi0Iqd8/q627AeF9vhJIZei3TLK0+N8ET0Gs26XJByxnFBSFfRkUDZgAACCtr7BwfoGQDSAISllSx3CObYYMR4PPw3OsQre6nt/Bz/9elKPHNjsDMcksKF3bMLdjK71NeVVJNNTJ1Fh+1oQ+V93kUcF98fjHapwlQfr0hOkTVaArGaF4Xq6MDQ/B0NZeB5mgNwHgdC02YfT/AZs8QLLXiByvAgKT8urwA4Rm9b5mnmrGMwX57lnfVCHub0sp6MyL55ZVlhGgxxzWXbrMEIzunaP1P4J4+GxfxptZZhhHW8MbtxVaySKFQISTmcMYXH0+XcuYu/FM2mP5RLJC9nqEqrbnlsQWVuBHMAwZzopUZcKUfykhTSDZGvttklHR9ddKNFE+aE7TEcIgk2Yy6F0RDT3Io7PrpleYtZv7gVoBTn0uDN8B3H778v0B2Wz6GJVzk/ZqwjIebxApNA0l7pollVlrxk3dsFbzwltycx5C/uLL576Pk7cFG+fpZbvTNhhox1fr4kEf+I3CLXkPAj1yTR7AjGy9bk9/SNbAweJI1RRdr8fftEks+GwEpUMfS8DBVvvdknMdCPSopdxqP+JSQvOd7BqiHFea9sJ57okxo2FZT5mxnu+iiChUyPIx6gFrON2BGmqNZlZnFXtxjZay0+XgXI8z5HOWYxuwZ85anIqjqfr2crGTWZU00NJ70BvFIAF9nE2zSqvRqnuSuDZVL3bgX20nITGZkxoVfKM4nAagl7d+8/rS7/B0uNOSmDBXrYbjwtS6ZTALkA0onOSFK39plXR45yrCh3xNA9KG+5SZ8HojZt+6w4s754w9LVhvois4Zfibd6tXIqvFoQ5QC'
                # user_id = "d4df054768f9d1d7"
                #access_token = "EwBwA8l6BAAURSN/FHlDW5xN74t6GzbtsBBeBUYAAfcRRYowDdVZ+3RiJHJwa+1Qpe3LJl0pELVeUDTlZhM5s3iaH1iictPsAr/YIwt0xQLPA+qDE+hvsjdfmJYwR6uQmZQ9EONzgrydh6FNtWmEYIN0C58WgPq97VCQvTAu+7ngaqjWrEzYMCccBhOaVy3Wem/hZCmQ9nQUctkF+jvR4Z1yx6T+SDWcvWUugOv4or5ZmePytBOJHAvjPzK+XWHc4boXb7FHYykoNCXQ6PrF0H74RvJ5DOikMb95euaURYqoIGglpbmfXyygaxNDlXhHwyPxF7oBkDkURydXLrGvowPi/1npG2+btOzf2wv48Z8SuUJ3YhpeLH4UnXlxM5ADZgAACDXeEO29FmmYQAKfut0CDEmX3Ive2OOZ2cu7bqCwgGUcGHcHYB7o6tGx4Ioj2FX+Jysoz2mc5Eiwqp9kWtHiHFPjzCnkRzv6DdKNSZKtKcWDdHN57NYPCVbDIYsm7nKom5wosV5UjZgALDVsM4EX3oAjsWackLOExhdYIuvealic+B/8OLcQnLl8TWPL6uMtdbXC0LWsVcq0OXeQSB8msG2S0KL7fF1QITHWorFHEAxaI1ScvZnHATOFTQmUfx1yq9zAxankW0mlOyHFxr+zHRkFu9Dg0jL66YyjWlBPrtN6zlK3fRsdUX3+2R8n6Mr//HSflrtshDFT0tQZNhW0fCY4o0mxuHvtIcrIytozqjayTGDcV3cM0nGrk6fZDi0UkIZ98R3dTbxqdx6H+pYp4OPNyMiwqfWyraumRLLlbGKxofrOQSPuDkZ7DgzbHpr0GgX3ct/+jaSvS3R0P4cHlcyY4aOtGf0eHmQvb/qYVviBzimdGYm6hDw/nk95aq5ard10zfY6rsy7AB9YG26TS0lZyHhT0vshOVOGc5DIkE32OREmbvpP3ZdmAfRQOmoHpjSdgHjNJAya2WNJ6j9vuK0Y2rblOfe/WI03deLtnx6OU7g04HaK/n06FGA6UIAYUfm/gOmO1zu5dWWVPvSZkYbt/V63RDFtAdmy3sLQ4w+Gk+q4wzh/L/mOWOwWWxsGPrpZdIeDkJa1RfCYIWyOq1r+7hIbyi1Su46/fdnpIPdh9BkreEOE+hldUYxaHDbuk+97cufp2MJ49NWPAg=="
            else:
                user_id = get_user_microsoft_id(subscription_id)
                access_token = get_user_acces_token(user_id)

            # logging.info(f'{user_id}')
            # logging.info(f'{access_token}')
            headers = {
                "Authorization" : "Bearer " + access_token,
                "Content-type" : "application/json"
            }
            r = requests.get(url = f'https://graph.microsoft.com/v1.0/users/{user_id}/drive/root/delta', headers=headers)
            logging.info(r.status_code)
            if (r.status_code != 200):
                changed_files = get_changed_files_ids(r.json())
                users_to_changed_files_map[user_id] = changed_files
                print(users_to_changed_files_map)
            else:
                logging.info(f'GET delta failed: Recieved status code is {r.status_code}')
                ###
                # Daniel added this section:
                # 1. if error code in response than
                #  refresh token and try again
                #
                #  if there is another error then log it and get out
                #

                logging.info('SECOND CHANCE')
                refresh_token(access_token)
                r = requests.get(
                    url=f'https://graph.microsoft.com/v1.0/users/{user_id}/drive/root/delta',
                    headers=headers)
                # shouldn't get inside if statemnet
                if (r.status_code != 200):
                    logging.info(r.status_code)
                changed_files = get_changed_files_ids(r.json())
                users_to_changed_files_map[user_id] = changed_files

            detection.detect(users_to_changed_files_map)
            return func.HttpResponse(status_code=202)




