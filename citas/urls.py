from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, ForgotPasswordView, ResetPasswordView,
    UserProfileView, UserListView,
    MedicoViewSet, EspecialidadViewSet, HorarioViewSet,
    CitaViewSet, HistorialViewSet, NotificacionViewSet,
    AdminBloquearUsuarioView, AdminReportesView, BuscarMedicoDisponibilidadView
)

router = DefaultRouter()
router.register(r'medicos', MedicoViewSet)
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'citas', CitaViewSet)
router.register(r'historial', HistorialViewSet)
router.register(r'notificaciones', NotificacionViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserProfileView.as_view(), name='user_detail'),

    path('buscar/disponibilidad/', BuscarMedicoDisponibilidadView.as_view(), name='buscar_disponibilidad'),

    path('admin/usuarios/<int:pk>/bloquear/', AdminBloquearUsuarioView.as_view(), name='admin_bloquear'),
    path('admin/reportes/', AdminReportesView.as_view(), name='admin_reportes'),

    path('', include(router.urls)),
]
