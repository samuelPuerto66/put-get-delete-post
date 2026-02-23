from django.urls import path
from .views import TareasAPIView

urlpatterns = [
    path('tareas/', TareasAPIView.as_view()),
    path('tareas/<str:id>/', TareasAPIView.as_view()),
]
