import logging
import azure.functions as func
from . import detection
import requests
from .tables import get_user_microsoft_id, get_user_acces_token , refresh_token
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
                access_token = 'EwB4A8l6BAAURSN/FHlDW5xN74t6GzbtsBBeBUYAAenlZHPx2gdbFpfmhtlkvjw8iBCe8yYGL8yoK1cOFc0Cuoib3NLrzeDZix12yM3eVok74MqO1N/NxEIEESHz+UPUwutXT0igEhsDG3ilw4wwUnzw+syMRTCTevZbTty94Ee53KhM1ipgg8sNpAcSPJ44cky+k2IDkNzf4JO18Zo5gYxTbfyIELb0SbgCzmzMH16KGS+Oij30fWephL8oNJOjJTLqLoj9+7m8xVoWQWygdNm7orh6nYXcbbuFZM8wkoNw7lDeqYeYNC0sdxQnBjMoGQVBA7n9tlRAKi07jzEG0c6f3Oxd8cROeQnVloxJhG2TwdvzTzgt48uDqNr4VBADZgAACP+dPRU6Qra1SAI88vMEFy0RTJ2i37XCZh4GUr1QaHYEs26eEtiLhcqy9JK2BMklRktjUbz3GWtrfj/KoZVOnmC9oVFZKiEaXvA8zZT9y23J+VNDZJrTTowUF0u5IMgRAspJQ9SR3wdVBz0tCcmIBxauwkDKweblx+4MVXHKrt7fooI+G09LQA1wQELrVkQsAMb1nIfZI5vsftTPB0f/MSNkAPIjX5v4Hb95d53WZZ0tZGoA8XMKiwgDw+DGd4faYHL0RLR3Ot+ND4moeZowSBHB7gqoLdjqochRuWcoEpNZ0nrRsP7G8E+VX2e7F/r/3h1p1fwVpmP5X9d0Ki0hX/CPuYanM2Bc7t6XYqB9QtzHkriKyOhcVm9lP+IqY7sMR8Ihy84WpDwR6vFX+hOzztrJ8m5TxdvUHo9RSLg0kFqzcGwvddEx4FjMTo/exG8TvKLNReVdAD7RdPAaiY4oPjLrK/B7Eq/KHnbkszBvSyW9xkKGrWf1N3qLK+G3/c6og/4dsOn4NvLOd01/dDQVm6Ozc38kj8cg5XEAY3Gtj+GuC2gExtS7CVXUPkTmFAyjcli4I4qI0v6U6PFiX2HZsUXjfXsIVgbtHWAWx3L5vzUt9FjasASr65GvznEHjha5K8EVBO10a/SYP7ahr7TPGC8dYmoSQuf3BY+OCzKE/azZwwmDqJQtPfnVdsrjtwNxJkLzzCHKWtg1tzOm4itVA+ZuDQh28NDTFwfbpt5YpssWJJRV6z6lGjQpMI0bOremSVGO9g5cWy0p8h6p0YYUoHgiiJQC'
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




