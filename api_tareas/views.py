from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TareasSerializer
from backend.backend.firebase_config import get_firestore_client
from firebase_admin import firestore


class TareasAPIView(APIView):
    """
    Endpoint para:
    GET  -> listar o probar API
    POST -> crear tarea
    PUT  -> actualizar tarea por ID
    """

    def get(self, request, id=None):
        try:
            db = get_firestore_client()

            # Si viene un ID → traer una tarea
            if id:
                doc = db.collection('api_tareas').document(id).get()

                if not doc.exists:
                    return Response({"error": "Tarea no encontrada"}, status=404)

                data = doc.to_dict()
                data["id"] = doc.id
                return Response(data, status=200)

            # Si NO viene ID → endpoint de prueba
            return Response({
                "mensaje": "API funcionando correctamente",
                "nota": "Endpoint de prueba - Firebase conectado"
            }, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "error": "Error al obtener las tareas",
                "detalle": str(e),
                "tipo": type(e).__name__
            }, status=500)

    def post(self, request):

        serializer = TareasSerializer(data=request.data)

        if serializer.is_valid():
            datos_validados = serializer.validated_data
            datos_validados['fecha_creacion'] = firestore.SERVER_TIMESTAMP

            try:
                db = get_firestore_client()
                nuevo_doc = db.collection('api_tareas').add(datos_validados)
                id_generado = nuevo_doc[1].id

                return Response({
                    "mensaje": "Tarea creada correctamente",
                    "id": id_generado
                }, status=201)

            except Exception as e:
                return Response({"Error": str(e)}, status=500)

        return Response(serializer.errors, status=400)

    # ✅ PUT → actualizar tarea
    def put(self, request, id=None):

        if not id:
            return Response({"error": "Debe enviar el ID"}, status=400)

        serializer = TareasSerializer(data=request.data)

        if serializer.is_valid():
            try:
                db = get_firestore_client()
                ref = db.collection('api_tareas').document(id)

                if not ref.get().exists:
                    return Response({"error": "Tarea no encontrada"}, status=404)

                ref.update(serializer.validated_data)

                return Response({
                    "mensaje": "Tarea actualizada correctamente",
                    "id": id
                }, status=200)

            except Exception as e:
                return Response({"error": str(e)}, status=500)

        return Response(serializer.errors, status=400)
    
    # ✅ DELETE → eliminar tarea por ID
    def delete(self, request, id=None):
        """
        Eliminar una tarea específica por ID
        """
        if not id:
            return Response({"error": "Se requiere el ID de la tarea"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Referencia al documento
            db = get_firestore_client()
            tarea_ref = db.collection('api_tareas').document(id)

            # Verificar que el documento existe antes de borrarlo
            if not tarea_ref.get().exists:
                return Response({"error": "Tarea no encontrada"}, status=status.HTTP_404_NOT_FOUND)
            
            # Eliminar el documento
            tarea_ref.delete()
            
            return Response({
                "mensaje": f"Tarea {id} se ha eliminado correctamente"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
