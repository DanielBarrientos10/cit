from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ─── Información de la API para Swagger ──────────────────
api_info = openapi.Info(
    title='Sistema de Gestión de Citas Médicas',
    default_version='v1',
    description=(
        'API REST para el Sistema de Gestión de Citas Médicas Online. '
        'Permite registrar pacientes, gestionar médicos, agendar y cancelar citas, '
        'administrar horarios y consultar historial clínico.\n\n'
        '## Autenticación\n'
        'Usa JWT. Obtén tu token en `POST /api/auth/login/` e inclúyelo como:\n'
        '`Authorization: Bearer <token>`'
    ),
    contact=openapi.Contact(email='admin@medicita.com'),
    license=openapi.License(name='MIT License'),
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('citas.urls')),

    # ─── Swagger / ReDoc ─────────────────────────────────
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('', RedirectView.as_view(url='/static/landing.html', permanent=False)),
    path('dashboard/', RedirectView.as_view(url='/static/dashboard.html', permanent=False)),
]
