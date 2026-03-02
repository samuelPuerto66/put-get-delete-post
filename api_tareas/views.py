from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TareasSerializer
from backend.backend.firebase_config import get_firestore_client
from firebase_admin import firestore, storage
from rest_framework.permissions import IsAuthenticated
from .authentication import FirebaseAuthentication

db = get_firestore_client()


class TareasAPIView(APIView):

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    """
    Endpoint para listar todas las tareas (GET)
    y crear una nueva tarea (POST)
    """

    def get(self, request, tarea_id=None):
        """
        GET trae todas las tareas del usuario
        """

        uid_usuario = request.user.uid
        rol_usuario = request.user.rol

        try:
            # Si es instructor ve todas
            if rol_usuario == "instructor":
                docs = db.collection('api_tareas').stream()
            else:
                # Si es aprendiz solo ve las suyas
                docs = db.collection('api_tareas') \
                         .where('usuarios_id', '==', uid_usuario) \
                         .stream()

            tareas = []

            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                tareas.append(data)

            return Response(
                {
                    "mensaje": f"Listando como rol {rol_usuario}",
                    "datos": tareas
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):

        serializer = TareasSerializer(data=request.data)

        if serializer.is_valid():

            datos_validados = serializer.validated_data
            datos_validados['usuario_uid'] = request.user.uid
            datos_validados['fecha_creacion'] = firestore.SERVER_TIMESTAMP

            try:
                nuevo_doc = db.collection('api1').add(datos_validados)
                id_generado = nuevo_doc[1].id

                imagen_url = None

                if 'imagen' in request.FILES:
                    bucket = storage.bucket()
                    imagen = request.FILES['imagen']
                    blob = bucket.blob(
                        f'tareas/{request.user.uid}/{id_generado}_{imagen.name}'
                    )
                    blob.upload_from_file(
                        imagen,
                        content_type=imagen.content_type
                    )
                    blob.make_public()
                    imagen_url = blob.public_url

                if imagen_url:
                    db.collection('api1') \
                      .document(id_generado) \
                      .update({'imagen_url': imagen_url})

                return Response(
                    {
                        "mensaje": "Tarea creada correctamente",
                        "id": id_generado,
                        "imagen_url": imagen_url
                    },
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, tarea_id=None):

        if not tarea_id:
            return Response(
                {"error": "ID requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tarea_ref = db.collection('api1').document(tarea_id)
            doc = tarea_ref.get()

            if not doc.exists:
                return Response(
                    {"error": "No encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            tarea_data = doc.to_dict()

            if tarea_data.get('usuario_uid') != request.user.uid:
                return Response(
                    {"error": "No tienes permiso para modificar esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = TareasSerializer(
                data=request.data,
                partial=True
            )

            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            datos_actualizados = serializer.validated_data

            if 'imagen' in request.FILES:
                bucket = storage.bucket()
                imagen = request.FILES['imagen']
                blob = bucket.blob(
                    f'tareas/{request.user.uid}/{tarea_id}_{imagen.name}'
                )
                blob.upload_from_file(
                    imagen,
                    content_type=imagen.content_type
                )
                blob.make_public()
                datos_actualizados['imagen_url'] = blob.public_url

            tarea_ref.update(datos_actualizados)

            return Response(
                {
                    "mensaje": f"Tarea {tarea_id} actualizada",
                    "datos": datos_actualizados
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, tarea_id):

        if not tarea_id:
            return Response(
                {"error": "Se requiere el id de alguna tarea"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tarea_ref = db.collection('api1').document(tarea_id)

            doc = tarea_ref.get()

            if not doc.exists:
                return Response(
                    {"error": "No encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            tarea_data = doc.to_dict()

            if tarea_data.get('usuario_uid') != request.user.uid:
                return Response(
                    {"error": "No tienes permiso para eliminar esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                )

            tarea_ref.delete()

            return Response(
                {"mensaje": f"Tarea {tarea_id} eliminada correctamente"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )