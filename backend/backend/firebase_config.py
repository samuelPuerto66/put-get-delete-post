import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv


def get_firestore_client():

    if not firebase_admin._apps:

        base_dir = os.path.dirname(os.path.abspath(__file__))
        cert_path = os.path.join(base_dir, "serviceAccountKey.json")

        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred)

    return firestore.client()