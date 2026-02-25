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
    #traemos nuestro guarda de seguridad
    authentication_classes=[FirebaseAuthentication]
    permission_classes=[IsAuthenticated]
    """
    Endpoint para alistar todas las tareas (GET) y crear una nueva tarea (POST)
    """
    
    def get(self, request, tarea_id=None):
        """
        GET trae todas las tareas del usuario
        """
        uid_usuario = request.user.uid

        try:
            db = get_firestore_client()
            #Traer todos los datos de la coleccion de firestore
            docs = db.collection('api1').where('usuario_uid', '==', request.user.uid).stream()
            tareas = []
            for doc in docs:
                tarea_data = doc.to_dict()
                tarea_data['id'] = doc.id
                tareas.append(tarea_data)
                
            return Response({"mensaje": "Exito", "datos": tareas}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def post(self, request):
        # 1. Pasar el JSON al serializador para que valide los campos
        serializer = TareasSerializer(data=request.data)
        
        #2. Si el JSON cumple las reglas:
        if serializer.is_valid():
            datos_validados = serializer.validated_data
            datos_validados['usuario_uid'] = request.user.uid
            datos_validados['fecha_creacion'] = firestore.SERVER_TIMESTAMP
            
            try : 
                db = get_firestore_client()
                #3. Guardamos los datos en firestore
                nuevo_doc = db.collection('api1').add(datos_validados)
                # Obtener el id generado
                id_generado = nuevo_doc[1].id
                
                # Subir imagen si existe
                imagen_url = None
                if 'imagen' in request.FILES:
                    bucket = storage.bucket()
                    imagen = request.FILES['imagen']
                    blob = bucket.blob(f'tareas/{request.user.uid}/{id_generado}_{imagen.name}')
                    blob.upload_from_file(imagen, content_type=imagen.content_type)
                    blob.make_public()  # Hacer público
                    imagen_url = blob.public_url
                
                # Actualizar documento con imagen_url si existe
                if imagen_url:
                    db.collection('api1').document(id_generado).update({'imagen_url': imagen_url})
                
                return Response({
                    "mensaje": "Tarea creada correctamente",
                    "id": id_generado,
                    "imagen_url": imagen_url
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, tarea_id=None):

        """PUT actualiza una tarea existente. El ID de la tarea a actualizar se recibe por URL
        """

        if not tarea_id:
            return Response({"error": "ID requerido"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            db = get_firestore_client()
            tarea_ref = db.collection('api1').document(tarea_id)

            doc = tarea_ref.get()
            if not doc.exists:
                return Response({"error": "No encontrado"},
                                status=status.HTTP_404_NOT_FOUND)
            
            tarea_data = doc.to_dict()
            
            if tarea_data.get('usuario_uid') != request.user.uid:
                return Response(
                    {"error": "No tienes permiso para modificar esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                    )

            #1. Validamos los datos nuevos con el Serializador

            serializer = TareasSerializer(data=request.data, partial=True)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            #2. Guardamos los cambios en Firestore
            datos_actualizados = serializer.validated_data
            
            # Subir nueva imagen si existe
            if 'imagen' in request.FILES:
                bucket = storage.bucket()
                imagen = request.FILES['imagen']
                blob = bucket.blob(f'tareas/{request.user.uid}/{tarea_id}_{imagen.name}')
                blob.upload_from_file(imagen, content_type=imagen.content_type)
                blob.make_public()
                datos_actualizados['imagen_url'] = blob.public_url

            tarea_ref.update(datos_actualizados)

            return Response({
                "mensaje": f"Tarea {tarea_id} actualizada",
                "datos": datos_actualizados
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, tarea_id):
        """
        DELETE: Eliminar una tarea especifica por id. El id viene de la url
        """
        if not tarea_id:
            return Response({"Error": "Se requiere el id de alguna tarea"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            db = get_firestore_client()
            # Referencia al documento
            tarea_ref = db.collection('api1').document(tarea_id)

            # Verificar que el doc existe antes de borrarlo
            if not tarea_ref.get().exists:
                return Response({"error": "No encontrado"},
                                status=status.HTTP_404_NOT_FOUND)
            doc = tarea_ref.get()
            tarea_data = doc.to_dict()
            
            if tarea_data.get('usuario_uid') != request.user.uid:
                return Response(
                    {"error": "No tienes permiso para modificar esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                    )
            tarea_ref.delete()
            return Response(
                {"mensaje": f"Tarea {tarea_id} se ha eliminado correctamente"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )