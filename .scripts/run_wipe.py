"""
Runner para limpiar todos los datos de prueba (mantiene admin y config base).
Ejecutar desde la raíz del proyecto:
    python run_wipe.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_citas.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from citas.models import (
    usuario, medicos, pacientes, horarios, citas,
    historial_clinico, notificaciones, auditoria_citas,
    medico_especialidad
)

print('Eliminando datos de prueba...')
notificaciones.objects.all().delete()
auditoria_citas.objects.all().delete()
historial_clinico.objects.all().delete()
citas.objects.all().delete()
horarios.objects.all().delete()
medico_especialidad.objects.all().delete()
medicos.objects.all().delete()
pacientes.objects.all().delete()
usuario.objects.exclude(correo='admin@medicita.com').delete()
print('Listo. Solo queda el usuario admin.')
