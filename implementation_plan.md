# Plan de Implementación: Fase 5 (Documentación Interactiva)

Este plan abarca la configuración para exponer una interfaz visual e interactiva de pruebas de la API (Swagger UI / ReDoc) generada mediante OpenAPI.

## User Review Required

> [!WARNING]
> **drf-spectacular vs drf-yasg:** En las instrucciones mencionas ambas librerías. Para este proyecto propongo firmemente utilizar **`drf-spectacular`**. Es la librería oficialmente recomendada por Django REST Framework para generar esquemas modernos (OpenAPI 3.0), mientras que `drf-yasg` se basa en la versión anterior (Swagger 2.0) y puede presentar incompatibilidades con las versiones más recientes de Django y DRF. 

## Proposed Changes

### 1. Entorno y Dependencias
- Se instalará el paquete mediante el comando: `pip install drf-spectacular`.

### 2. Configuración Base (`gestion_citas/settings.py`)
AUTH_USER_MODEL='citas.usuario'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
- Se añadirá `'drf_spectacular'` a la lista de `INSTALLED_APPS`.
- Se configurará la clase de esquema global por defecto de DRF:
  ```python
  REST_FRAMEWORK = {
      'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
  }
  ```
- Se añadirán metadatos base para Swagger mediante la variable `SPECTACULAR_SETTINGS`.

### 3. Rutas de Documentación (`gestion_citas/urls.py`)
- Se importarán las vistas de documentación desde `drf_spectacular.views` (`SpectacularAPIView`, `SpectacularSwaggerView`, `SpectacularRedocView`).
- Se añadirán las siguientes rutas al `urlpatterns` principal:
  - `path('api/schema/', SpectacularAPIView.as_view(), name='schema')` -> Retorna el YAML/JSON del esquema.
  - `path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')` -> Interfaz interactiva de Swagger.
  - `path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')` -> Interfaz de documentación pura (ReDoc).

## Verification Plan

### Automated Tests
1. Ejecutar instalación de pip verificando su conclusión sin errores de compilación.
2. Ejecutar `python manage.py check` para garantizar que la variable de schema y las rutas son sintácticamente válidas.
3. El usuario podrá navegar en su localhost al puerto `/api/docs/` y visualizar de forma automática todos los endpoints de Autenticación, Citas y Disponibilidad.
