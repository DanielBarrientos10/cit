# Documentación de API - Sistema de Gestión de Citas Médicas

## Autenticación

La API usa JWT (JSON Web Tokens). Para autenticarse:
1. Obtener token via `POST /api/auth/login/`
2. Incluir en el header: `Authorization: Bearer <token>`

---

## Endpoints de Autenticación

### POST /api/auth/register/
Registrar un nuevo paciente.
- **Permiso:** AllowAny
- **Body:**
```json
{
  "correo": "paciente@medicita.com",
  "password": "Paciente123!",
  "nombre_completo": "Juan Pérez",
  "documento": "12345678",
  "telefono": "3001234567"
}
```
- **Respuesta (201):** Usuario creado

### POST /api/auth/login/
Iniciar sesión.
- **Permiso:** AllowAny
- **Body:**
```json
{
  "correo": "paciente@medicita.com",
  "password": "Paciente123!"
}
```
- **Respuesta (200):** `{ "access": "<token>", "refresh": "<token>" }`
- **Nota:** Bloquea la cuenta por 15 minutos tras 3 intentos fallidos

### POST /api/auth/token/refresh/
Refrescar token JWT.
- **Body:** `{ "refresh": "<refresh_token>" }`

### POST /api/auth/forgot-password/
Solicitar recuperación de contraseña.
- **Body:** `{ "correo": "paciente@email.com" }`

### POST /api/auth/reset-password/
Restablecer contraseña con token.
- **Body:**
```json
{
  "token": "<token_recibido>",
  "password": "NuevaPass1!"
}
```

---

## Endpoints de Usuarios

### GET /api/users/
Listar todos los usuarios (solo admin).
- **Permiso:** IsAdmin

### GET /api/users/{id}/
Consultar perfil de usuario.

### PUT /api/users/{id}/
Actualizar datos de usuario.
- **Body (parcial):** `{ "nombre_completo": "...", "telefono": "..." }`

### DELETE /api/users/{id}/
Desactivar usuario (solo admin).

---

## Endpoints de Médicos

### GET /api/medicos/
Listar todos los médicos.
- **Permiso:** IsAuthenticated

### GET /api/medicos/{id}/
Consultar información de un médico.

### POST /api/medicos/
Registrar un médico (solo admin).
- **Body:** Datos del médico + `{ "usuario": { ...datos del usuario... } }`

### PUT /api/medicos/{id}/
Actualizar médico (solo admin).

### DELETE /api/medicos/{id}/
Eliminar médico (solo admin).

### GET /api/medicos/{id}/especialidades/
Listar especialidades de un médico.

### POST /api/medicos/{id}/especialidades/
Asignar especialidad a médico.
- **Body:** `{ "id_especialidad": 1 }`

### DELETE /api/medicos/{id}/especialidades/
Remover especialidad de médico.
- **Body:** `{ "id_especialidad": 1 }`

### GET /api/medicos/{id}/disponibilidad/
Ver horarios disponibles de un médico.

### POST /api/medicos/{id}/disponibilidad/
(Usar POST /api/horarios/ en su lugar)

---

## Endpoints de Especialidades

### GET /api/especialidades/
Listar especialidades médicas.

### POST /api/especialidades/
Crear especialidad (solo admin).
- **Body:** `{ "nombre": "Cardiología" }`

### PUT /api/especialidades/{id}/
Editar especialidad (solo admin).

### DELETE /api/especialidades/{id}/
Eliminar especialidad (solo admin).

---

## Endpoints de Horarios (Disponibilidad)

### GET /api/horarios/
Listar horarios (filtrable por `?id_medico=N&fecha=YYYY-MM-DD&disponible=true`).

### POST /api/horarios/
Crear un horario.
- **Body:**
```json
{
  "id_medico": 1,
  "fecha": "2026-07-01",
  "hora_inicio": "09:00",
  "hora_fin": "09:30"
}
```

### PUT /api/horarios/{id}/
Modificar un horario.

### DELETE /api/horarios/{id}/
Eliminar un horario.

### POST /api/horarios/crear-slots/
Crear múltiples slots automáticamente.
- **Body:**
```json
{
  "id_medico": 1,
  "fecha": "2026-07-01",
  "hora_inicio": "09:00",
  "hora_fin": "12:00",
  "duracion_minutos": 30
}
```

---

## Endpoints de Citas

### GET /api/citas/
Listar citas. Para pacientes: solo sus citas. Para médicos: citas asignadas. Para admin: todas.

### POST /api/citas/
Crear una cita (solo paciente).
- **Body:**
```json
{
  "id_horario": 1,
  "motivo": "Consulta general"
}
```

### GET /api/citas/{id}/
Consultar detalle de una cita.

### PUT /api/citas/{id}/
Reprogramar o modificar cita.

### DELETE /api/citas/{id}/
Eliminar cita.

### PUT /api/citas/{id}/cancelar/
Cancelar cita (regla: máximo 24h antes, admin puede forzar).
- **Permiso:** IsPaciente (24h) o IsAdmin (sin restricción)

### PUT /api/citas/{id}/realizada/
Marcar cita como realizada (solo médico/admin).

### PUT /api/citas/{id}/no-asistio/
Marcar cita como no asistió (solo médico/admin).

---

## Endpoints de Historial Clínico

### GET /api/historial/?paciente=N
Consultar historial de un paciente.

### POST /api/historial/
Agregar registro médico (solo médico/admin).
- **Body:**
```json
{
  "id_paciente": 1,
  "id_medico": 1,
  "fecha": "2026-07-01",
  "diagnostico": "...",
  "tratamiento": "...",
  "notas": "..."
}
```

### PUT /api/historial/{id}/
Actualizar registro.

### DELETE /api/historial/{id}/
Eliminar registro.

---

## Endpoints de Notificaciones

### GET /api/notificaciones/?usuario=N
Listar notificaciones.

### POST /api/notificaciones/
Crear notificación (solo admin).
- **Body:** `{ "id_usuario": 1, "mensaje": "Recordatorio de cita" }`

### PUT /api/notificaciones/{id}/
Actualizar notificación.

### DELETE /api/notificaciones/{id}/
Eliminar notificación.

### PUT /api/notificaciones/{id}/leer/
Marcar notificación como leída.

---

## Endpoints de Administración

### PUT /api/admin/usuarios/{id}/bloquear/
Activar o bloquear un usuario (toggle).
- **Permiso:** IsAdmin

### GET /api/admin/reportes/?tipo=cancelaciones
Reporte de cancelaciones.
- **Parámetros:** `tipo` = `cancelaciones` | `no-asistencia-por-medico`

---

## Endpoints de Búsqueda

### GET /api/buscar/disponibilidad/?especialidad=N&medico=N
Buscar horarios disponibles filtrados por especialidad y/o médico.

---

## Reglas de Negocio

1. **Contraseña:** Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 carácter especial
2. **Bloqueo de cuenta:** 3 intentos fallidos → bloqueo por 15 minutos
3. **Cancelación:** Hasta 24 horas antes de la cita (admin puede forzar)
4. **Horario único:** CHECK(hora_fin > hora_inicio)
5. **Cita única por horario:** UNIQUE(id_horario)
6. **Transacciones:** Crear/cancelar cita usa transacción atómica
7. **Estados de cita:** pendiente → realizada | cancelada | no_asistio
