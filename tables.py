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
def insert_new_file_to_db(file_id, user_id, entropy,extension):
    """ insert a new file into the files table """
    # connect to the PostgreSQL server

    if (is_honeypot(user_id, file_id) == True):
        return

    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    command = f'INSERT INTO files_table (file_id,user_id,entropy,extension) VALUES (\'{file_id}\',\'{user_id}\',\'{entropy}\',\'{extension}\');'

    # execute the INSERT statement
    cur.execute(command)

    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()

    if conn is not None:
        conn.close()

def is_file_in_db(file_id,user_id):
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cmd = f'SELECT file_id FROM files_table WHERE file_id LIKE \'{file_id}\' AND user_id LIKE \'{user_id}\';'

    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(cmd)

    found = False

    if (cur.fetchone() != None):
        found =True

    # close communication with the database
    cur.close()

    if conn is not None:
        conn.close()

    return found

def delete_file_from_db(file_id,user_id):
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cmd = f'DELETE FROM files_table WHERE file_id LIKE \'{file_id}\' AND user_id LIKE \'{user_id}\';'

    cur=conn.cursor()
    # execute the INSERT statement
    cur.execute(cmd)

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
    fetch = cur.fetchone()
    entropy = 0
    if (fetch):
        entropy=fetch[0]
    
    cur.close()
    if conn is not None:
        conn.close()

    return entropy

def set_file_entropy_in_db(user_id,file_id,entropy):
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cmd = f'UPDATE files_table SET entropy = {entropy} WHERE file_id LIKE \'{file_id}\' AND user_id LIKE \'{user_id}\';'

    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(cmd)

    conn.commit()

    cur.close()
    if conn is not None:
        conn.close()


def get_file_extension_from_db(user_id, file_id):
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cmd = f'SELECT extension FROM files_table WHERE file_id LIKE \'{file_id}\' AND user_id LIKE \'{user_id}\';'

    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(cmd)
    ext = ''
    fetch = cur.fetchone()

    if (fetch):
        ext = fetch[0]

    cur.close()
    if conn is not None:
        conn.close()

    return ext

def get_user_microsoft_id(subscription_id):
    # connect to the PostgreSQL server
    conn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    #get user id from db
    command = f'SELECT user_id FROM users_table WHERE sub_id LIKE \'{subscription_id}\';'
    cur.execute(command)
    userMicrosoftId = ''
    fetch = cur.fetchone()
    if (fetch != None):
        userMicrosoftId = fetch[0]

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
    fetch = cur.fetchone()
    if (fetch):
        userToken = fetch[0]

    # close the communication with the PostgreSQL
    cur.close()
    if conn is not None:
        conn.close()

    return userToken

def get_user_delta_link_from_db(user_id):
    # connect to the SQL server
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    #get user id from db
    command = f'SELECT delta_link FROM users_table WHERE user_id LIKE \'{user_id}\';'
    cur.execute(command)
    userToken = None
    fetch = cur.fetchone()
    if (fetch):
         userToken = fetch[0]

    # close the communication with the PostgreSQL
    cur.close()
    if conn is not None:
        conn.close()

    return userToken

def set_user_delta_link(user_id,delta_link):
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cmd = f'UPDATE users_table SET delta_link = \'{delta_link}\' WHERE user_id LIKE \'{user_id}\';'

    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(cmd)

    conn.commit()

    cur.close()
    if conn is not None:
        conn.close()

###getting access token , return value -> new access token
###updating users table with new token
def refresh_access_token(access_token):
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

    aad_auth = OAuth2Session(settings['app_id'],
                             token=refresh_token_from_table,
                             scope=settings['scopes'],
                             redirect_uri=settings['redirect'])

    refresh_params = {
        'client_id': settings['app_id'],
        'client_secret': settings['app_secret'],
    }
    new_token = aad_auth.refresh_token(token_url, refresh_token_from_table, **refresh_params)
    new_access_token=new_token['access_token']
    cmd=f'Update users_table SET token =\'{new_access_token}\' WHERE token LIKE \'{access_token}\';'
    cur.execute(cmd)
    cur.commit()
    # close the communication with the MySQL
    cur.close()
    if conn is not None:
        conn.close()
    return new_access_token


def is_honeypot(user_id, DriveItem):
    # connect to the SQL server
    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # create a cursor
    cur = conn.cursor()

    # get refresh_token from db
    cmd = f'SELECT * FROM honeypot_table WHERE user_id LIKE \'{user_id}\' AND file_id LIKE \'{DriveItem}\';'
    cur.execute(cmd)
    a = cur.fetchone()
    if (a != None):
        return True
    return False
