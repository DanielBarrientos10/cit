# urls for the citas app

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import RegisterView, LoginView, CitaCreateView, CitaCancelView, MedicoDisponibilidadView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('citas/', CitaCreateView.as_view(), name='crear_cita'),
    path('citas/<int:pk>/cancelar/', CitaCancelView.as_view(), name='cancelar_cita'),
    path('medicos/<int:medico_id>/disponibilidad/', MedicoDisponibilidadView.as_view(), name='disponibilidad_medico'),
]
