from django.contrib import admin
from .models import (
    rol, usuario, pacientes, medicos, especialidades,
    medico_especialidad, horarios, estados_cita, citas,
    auditoria_citas, tokens_recuperacion, historial_clinico, notificaciones
)

admin.site.register(rol)
admin.site.register(usuario)
admin.site.register(pacientes)
admin.site.register(medicos)
admin.site.register(especialidades)
admin.site.register(medico_especialidad)
admin.site.register(horarios)
admin.site.register(estados_cita)
admin.site.register(citas)
admin.site.register(auditoria_citas)
admin.site.register(tokens_recuperacion)
admin.site.register(historial_clinico)
admin.site.register(notificaciones)
