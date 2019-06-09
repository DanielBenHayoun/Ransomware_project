import pyodbc
from requests_oauthlib import OAuth2Session

server = 'bhkshield.database.windows.net'
database = 'bhkshield'
username = 'daniel'
password = 'BHKshield1!'
driver= '{ODBC Driver 17 for SQL Server}'


settings= {
    'app_id' : 'ba355e66-6eda-4ca0-b961-c2e546631a6e',
   # 'scopes' : 'openid profile Offline_Access User.Read Files.Read.All Files.ReadWrite Files.ReadWrite.All',
    'scopes' : 'openid profile User.Read Files.Read.All Files.ReadWrite Files.ReadWrite.All',
    'redirect' : 'http://localhost:8000/callback',
    'authority': 'https://login.microsoftonline.com/common',
    'token_endpoint' : '/oauth2/v2.0/token' ,
    'app_secret' : 'txODRBG1815+-[ngajsVS5{'

}

graph_url = 'https://graph.microsoft.com/v1.0'

token_url = '{0}{1}'.format(settings['authority'],
                            settings['token_endpoint'])

"""need to add also a result if the insert did not succeed"""
def insert_new_file_to_db(file_id, user_id, entropy):
    """ insert a new file into the files table """
    # connect to the PostgreSQL server
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    command = f'INSERT INTO files_table (file_id,user_id,entropy) VALUES (\'{file_id}\',\'{user_id}\',\'{entropy}\');'

    # execute the INSERT statement
    cur.execute(command)

    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()

    if conn is not None:
        conn.close()


def delete_file_from_db(file_id,user_id):
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cmd = f'DELETE FROM files_table WHERE file_id LIKE \'{file_id}\' AND user_id LIKE \'{user_id}\';'

    cur=conn.cursor()
    # execute the INSERT statement
    cur.execute(cmd, (user_id, entropy, file_id))

    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()

    if conn is not None:
        conn.close()

def get_file_entropy_from_db(user_id,file_id):

    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cmd = f'SELECT entropy FROM files_table WHERE file_id LIKE \'{file_id}\' AND user_id LIKE \'{user_id}\';'

    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(cmd)

    entropy=cur.fetchone()[0]
    
    cur.close()
    if conn is not None:
        conn.close()

    return entropy

def get_user_microsoft_id(subscription_id):
    # connect to the PostgreSQL server
    conn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    #get user id from db
    command = f'SELECT user_id FROM users_table WHERE sub_id LIKE \'{subscription_id}\';'
    cur.execute(command)
    userMicrosoftId = ''
    if (cur.fetchone() != None):
        userMicrosoftId = cur.fetchone()[0]

    # close the communication with the MySQL
    cur.close()
    if conn is not None:
        conn.close()

    return userMicrosoftId

def get_user_acces_token(user_id):
    # connect to the PostgreSQL server
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    #get user id from db
    command = f'SELECT token FROM users_table WHERE user_id LIKE \'{user_id}\';'
    cur.execute(command)
    userToken = ''
    if (cur.fetchone()):
        userToken = cur.fetchone()[0]

    # close the communication with the PostgreSQL
    cur.close()
    if conn is not None:
        conn.close()

    return userToken


def refresh_token(access_token):
    # connect to the PostgreSQL server
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    # get refresh_token from db
    cmd =f'SELECT refresh_token FROM users_table WHERE token LIKE \'{access_token}\';'
    cur.execute(cmd)
    refresh_token_from_table = ''
    a=cur.fetchone()
    if (a != None):
        refresh_token_from_table= a[0]

    # close the communication with the MySQL
    cur.close()
    if conn is not None:
        conn.close()

    aad_auth = OAuth2Session(settings['app_id'],
                                     token=refresh_token_from_table,
                                     scope=settings['scopes'],
                                     redirect_uri=settings['redirect'])


    refresh_params = {
                'client_id': settings['app_id'],
                'client_secret': settings['app_secret'],
            }
    new_token = aad_auth.refresh_token(token_url, refresh_token_from_table,**refresh_params)
    return new_token