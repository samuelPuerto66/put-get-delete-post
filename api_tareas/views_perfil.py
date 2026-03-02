import cloudinary
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .authentication import FirebaseAuthentication
from backend.backend.firebase_config import get_firestore_client

db = get_firestore_client()

class PerfilImagenAPIView(APIView):
    authetication_classes = [FirebaseAuthentication]
    Permission_classes = [IsAuthenticated]
    perser_classes = (MultiPartParser,FormParser)

    def post(self, request):
        file_to_upload = request.FILES.get('imagen')

        if not file_to_upload:
            return Response ({"error": "No se envio ninguna imagen"}, status.HTTP_400_BAD_REQUEST)

            try: 
                uid = request.user.uid

                #subir cloudinary
                #folder nos va a organizar las fotos

                upload_result = cloudinary.uploader.upload(
                    file_to_upload,
                    folder=f"adso/perfiles/{uid}/",
                    public_id= "foto_principal",
                    overwrite= True
                )

                #obtener la url optimizada
                #cloudinary nos da una url segura https

                url_imagen = upload_result.get('secure_url')

                # guardar la url en firestore
                db.collection('perfiles').document(uid).update({
                     'foto_url':url_imagen

                })

                return Response({
                    "mensaje":"foto de perfil actualizada",
                    "url":url_imagen

                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)