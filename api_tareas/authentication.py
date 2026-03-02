from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from backend.backend.firebase_config import get_firestore_client

db = get_firestore_client()

class FirebaseAuthentication(BaseAuthentication):

    def authenticate(self, request):

        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')

        if not auth_header:
            return None

        partes = auth_header.split()

        if len(partes) != 2 or partes[0].lower() != 'bearer':
            return None

        token = partes[1]

        try:
            decoded_token = auth.verify_id_token(token)

            uid = decoded_token.get('uid')
            email = decoded_token.get('email')

            user_profile = db.collection('perfiles').document(uid).get()
            rol = user_profile.to_dict().get('rol', 'aprendiz') if user_profile.exists else 'aprendiz'

            class FirebaseUser:
                is_authenticated = True

                def __init__(self, uid, email, rol):
                    self.uid = uid
                    self.email = email
                    self.rol = rol
                    self.is_authenticated = True

            return (FirebaseUser(uid, email, rol), decoded_token)

        except Exception as e:
            raise AuthenticationFailed(f"Token no es valido o esta expirado: {str(e)}")