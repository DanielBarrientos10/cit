# Casos de Uso - MediCita

## 1. Paciente

### CU-01: Registro de paciente
- **Actor:** Usuario nuevo
- **Precondición:** No tener cuenta
- **Flujo:**
  1. Ingresa a `/login.html?mode=register`
  2. Completa: nombre, correo, documento, teléfono, contraseña
  3. Sistema valida contraseña (8+ chars, mayúscula, número, especial)
  4. Sistema crea cuenta con rol "paciente"
  5. Redirige al dashboard
- **Postcondición:** Cuenta creada, sesión activa

### CU-02: Inicio de sesión
- **Actor:** Paciente registrado
- **Flujo:**
  1. Ingresa correo y contraseña
  2. Sistema valida credenciales
  3. Si son correctas: retorna JWT, redirige a dashboard
  4. Si falla: incrementa intentos (máx 3 → bloqueo 15 min)
- **Excepción:** Cuenta bloqueada → mensaje de espera

### CU-03: Agendar cita
- **Actor:** Paciente autenticado
- **Precondición:** Tener sesión activa
- **Flujo:**
  1. Selecciona especialidad
  2. Sistema muestra médicos disponibles
  3. Selecciona médico
  4. Sistema muestra horarios disponibles (14 días)
  5. Selecciona fecha y hora
  6. Ingresa motivo de la cita
  7. Confirma → sistema crea cita con estado "pendiente"
  8. Reserva el horario (transacción atómica)
- **Postcondición:** Cita creada, horario bloqueado

### CU-04: Cancelar cita
- **Actor:** Paciente autenticado
- **Precondición:** Tener cita pendiente/confirmada
- **Flujo:**
  1. Ve lista de "Mis Citas"
  2. Selecciona cita a cancelar
  3. Confirma cancelación
  4. Sistema valida regla de 24h
  5. Si cumple: cambia estado a "cancelada", libera horario
  6. Si no cumple: rechaza con mensaje
- **Excepción:** Cita en menos de 24h → solo admin puede cancelar

### CU-05: Ver historial clínico
- **Actor:** Paciente autenticado
- **Flujo:**
  1. Navega a "Mi Historial"
  2. Sistema muestra registros ordenados por fecha
  3. Cada registro: fecha, médico, diagnóstico, tratamiento, notas

### CU-06: Ver notificaciones
- **Actor:** Paciente autenticado
- **Flujo:**
  1. Navega a "Notificaciones"
  2. Sistema muestra lista con indicador de leída/no leída
  3. Al abrir: marca como leída

### CU-07: Editar perfil
- **Actor:** Paciente autenticado
- **Flujo:**
  1. Navega a "Mi Perfil"
  2. Modifica datos (nombre, teléfono, etc.)
  3. Guarda cambios
- **Restricción:** No puede cambiar correo ni documento

### CU-08: Recuperar contraseña
- **Actor:** Usuario con cuenta
- **Flujo:**
  1. En login, hace clic en "¿Olvidaste tu contraseña?"
  2. Ingresa correo
  3. Sistema genera token de recuperación
  4. (Simulado) Muestra token en pantalla
  5. Ingresa token + nueva contraseña
  6. Sistema actualiza contraseña

---

## 2. Médico

### CU-09: Ver citas recibidas
- **Actor:** Médico autenticado
- **Flujo:**
  1. Navega a "Citas Recibidas"
  2. Sistema muestra citas del médico con: paciente, fecha, motivo, estado
  3. Filtra por estado (pendiente, confirmada, realizada, etc.)

### CU-10: Marcar cita como realizada
- **Actor:** Médico autenticado
- **Precondición:** Cita en estado pendiente/confirmada
- **Flujo:**
  1. Selecciona la cita
  2. Opcionalmente agrega diagnóstico, tratamiento, notas
  3. Marca como "realizada"
  4. Sistema actualiza estado y crea registro en historial clínico

### CU-11: Marcar inasistencia
- **Actor:** Médico autenticado
- **Flujo:**
  1. Selecciona cita donde el paciente no se presentó
  2. Marca como "no_asistio"
  3. Sistema actualiza estado

### CU-12: Gestionar horarios
- **Actor:** Médico autenticado
- **Flujo:**
  1. Navega a "Mis Horarios"
  2. Ve calendario de slots existentes
  3. Crea nuevos slots: fecha, hora inicio, hora fin
  4. Puede crear múltiples slots en lote
  5. Slots quedan disponibles para pacientes

### CU-13: Ver especialidades
- **Actor:** Médico autenticado
- **Flujo:**
  1. Navega a "Mis Especialidades"
  2. Sistema muestra especialidades asignadas

---

## 3. Administrador

### CU-14: Dashboard principal
- **Actor:** Admin autenticado
- **Flujo:**
  1. Ingresa al sistema
  2. Ve estadísticas: total médicos, pacientes, citas, especialidades
  3. Ve citas próximas
  4. Ve distribución por estado

### CU-15: Gestión de usuarios
- **Actor:** Admin autenticado
- **Flujo:**
  1. Navega a "Usuarios"
  2. Ve lista paginada con búsqueda
  3. Puede activar/desactivar usuarios
  4. Ve detalle: nombre, correo, rol, estado

### CU-16: Registrar médico
- **Actor:** Admin autenticado
- **Flujo:**
  1. Navega a "Médicos"
  2. Clic en "Registrar Médico"
  3. Completa: nombre, correo, documento, teléfono, registro profesional, consultorio
  4. Sistema crea usuario + perfil médico
  5. Contraseña inicial: `Medico123!`

### CU-17: Gestión de especialidades
- **Actor:** Admin autenticado
- **Flujo:**
  1. Navega a "Especialidades"
  2. Ve lista de especialidades existentes
  3. Puede crear nuevas especialidades
  4. Puede eliminar (si no tiene médicos asociados)

### CU-18: Ver reportes
- **Actor:** Admin autenticado
- **Flujo:**
  1. Navega a "Reportes"
  2. Ve gráficas: citas por estado, citas por mes, distribución por especialidad
  3. Usa Chart.js para visualización

---

## 4. Casos transversales

### CU-19: Cierre de sesión
- **Actor:** Cualquier usuario autenticado
- **Flujo:**
  1. Clic en "Cerrar Sesión"
  2. Sistema elimina token JWT del cliente
  3. Redirige a landing page

### CU-20: Protección de rutas
- **Actor:** Sistema
- **Flujo:**
  1. Si usuario no autenticado accede a `/dashboard/`
  2. Redirige a `/login.html`
  3. Sidebar oculto hasta autenticación válida

### CU-21: Bloqueo por intentos fallidos
- **Actor:** Sistema
- **Flujo:**
  1. Usuario falla login → incrementa `intentos_fallidos`
  2. Al 3er fallo: `bloqueado_hasta = now + 15 min`
  3. Mientras esté bloqueado: rechaza cualquier intento
  4. Después de 15 min: resetea contadores
