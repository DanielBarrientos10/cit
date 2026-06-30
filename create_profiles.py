import os
# pyrefly: ignore [missing-import]
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_citas.settings')
django.setup()

from citas.models import usuario, rol, medicos, pacientes, especialidades, medico_especialidad
from datetime import date

# Obtenemos los roles
rol_medico = rol.objects.get(nombre='medico')
rol_paciente = rol.objects.get(nombre='paciente')

# --- Crear un Médico de prueba ---
try:
    u_medico = usuario.objects.create_user(
        correo='medico@medicita.com',
        documento='123456789',
        nombre_completo='Dr. Juan Perez',
        telefono='3001112233',
        password='Medico123!'
    )
    u_medico.id_rol = rol_medico
    u_medico.save()

    med = medicos.objects.create(
        id_medico=u_medico,
        registro_profesional='MED-12345',
        consultorio='101A'
    )
    
    # Asignarle la primera especialidad disponible
    esp = especialidades.objects.first()
    if esp:
        medico_especialidad.objects.create(id_medico=med, id_especialidad=esp)
    print("Perfil de MÉDICO creado exitosamente.")
except Exception as e:
    print(f"Médico ya existe o error: {e}")

# --- Crear un Paciente de prueba ---
try:
    u_paciente = usuario.objects.create_user(
        correo='paciente@medicita.com',
        documento='987654321',
        nombre_completo='Maria Gonzalez',
        telefono='3009998877',
        password='Paciente123!'
    )
    u_paciente.id_rol = rol_paciente
    u_paciente.save()

    pacientes.objects.create(
        id_paciente=u_paciente,
        fecha_nacimiento=date(1990, 5, 15),
        sexo='F',
        eps='Sanitas'
    )
    print("Perfil de PACIENTE creado exitosamente.")
except Exception as e:
    print(f"Paciente ya existe o error: {e}")
