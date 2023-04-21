import pyrebase
import pickle
import os
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials


cred = credentials.Certificate("serviceAccount.json")

firebase_admin.initialize_app(cred)

firebaseConfig = {
    'apiKey': "AIzaSyA8gTf61ob6mBMY9Tqje16vcitYpsXIOGw",
    'authDomain': "flet-course.firebaseapp.com",
    'databaseURL': "https://flet-course-default-rtdb.firebaseio.com",
    'projectId': "flet-course",
    'storageBucket': "flet-course.appspot.com",
    'messagingSenderId': "663795272566",
    'appId': "1:663795272566:web:2747bde2bee7ef7a1e8857"
}


firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


def create_user(name, email, password):
    try:
        user = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=name)
        return user.uid
    except:
        return None


def reset_password(email):
    try:
        auth.send_password_reset_email(email)
        return not None
    except:
        return None


def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user['idToken']
    except:
        return None


def store_session(token):
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
    with open('token.pickle', 'wb') as f:
        pickle.dump(token, f)


def load_token():
    try:
        with open('token.pickle', 'rb') as f:
            token = pickle.load(f)
        return token
    except:
        return None


def authenticate_token(token):
    try:
        result = firebase_auth.verify_id_token(token)

        return result['user_id']
    except:
        return None


def get_name(token):
    try:
        result = firebase_auth.verify_id_token(token)

        return result['name']
    except:
        return None


def revoke_token(token):
    result = firebase_auth.revoke_refresh_tokens(authenticate_token(token))
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
