from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    rol, usuario, pacientes, medicos, especialidades,
    horarios, estados_cita, citas
)
from datetime import date, time, timedelta
from django.utils import timezone

class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol_paciente = rol.objects.create(nombre='paciente')
        cls.rol_medico = rol.objects.create(nombre='medico')
        cls.rol_admin = rol.objects.create(nombre='admin')

        cls.paciente_user = usuario.objects.create_user(
            correo='paciente@test.com', documento='123', password='Test1234!',
            nombre_completo='Paciente Test', telefono='555-0001'
        )
        cls.paciente_user.id_rol = cls.rol_paciente
        cls.paciente_user.save()
        cls.paciente = pacientes.objects.create(
            id_paciente=cls.paciente_user, fecha_nacimiento='1990-01-01',
            sexo='M', eps='Sura', alergias='Ninguna'
        )

        cls.medico_user = usuario.objects.create_user(
            correo='medico@test.com', documento='456', password='Test1234!',
            nombre_completo='Medico Test', telefono='555-0002'
        )
        cls.medico_user.id_rol = cls.rol_medico
        cls.medico_user.save()
        cls.medico = medicos.objects.create(
            id_medico=cls.medico_user, registro_profesional='RP123',
            consultorio='101', estado='activo'
        )

        cls.admin_user = usuario.objects.create_user(
            correo='admin@test.com', documento='789', password='Test1234!',
            nombre_completo='Admin Test', telefono='555-0003'
        )
        cls.admin_user.id_rol = cls.rol_admin
        cls.admin_user.save()

        cls.estado_pendiente, _ = estados_cita.objects.get_or_create(nombre='pendiente')
        cls.estado_cancelada, _ = estados_cita.objects.get_or_create(nombre='cancelada')
        cls.estado_realizada, _ = estados_cita.objects.get_or_create(nombre='realizada')
        cls.estado_no_asistio, _ = estados_cita.objects.get_or_create(nombre='no_asistio')

        cls.horario = horarios.objects.create(
            id_medico=cls.medico, fecha=date.today() + timedelta(days=5),
            hora_inicio=time(9, 0), hora_fin=time(9, 30), disponible=True
        )


class AuthTests(BaseTestCase):
    def test_register_paciente(self):
        client = APIClient()
        data = {
            'correo': 'nuevo@test.com', 'documento': '999',
            'nombre_completo': 'Nuevo Paciente', 'telefono': '555-9999',
            'password': 'Pass1234!'
        }
        response = client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(usuario.objects.filter(correo='nuevo@test.com').exists())

    def test_login_success(self):
        client = APIClient()
        response = client.post('/api/auth/login/', {
            'correo': 'paciente@test.com', 'password': 'Test1234!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_wrong_password(self):
        client = APIClient()
        response = client.post('/api/auth/login/', {
            'correo': 'paciente@test.com', 'password': 'WrongPass1!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_bloqueo(self):
        client = APIClient()
        for _ in range(3):
            client.post('/api/auth/login/', {
                'correo': 'paciente@test.com', 'password': 'WrongPass1!'
            }, format='json')
        response = client.post('/api/auth/login/', {
            'correo': 'paciente@test.com', 'password': 'Test1234!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_register_password_weak(self):
        client = APIClient()
        data = {
            'correo': 'weak@test.com', 'documento': '111',
            'nombre_completo': 'Weak', 'telefono': '555-1111',
            'password': 'short'
        }
        response = client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CitaTests(BaseTestCase):
    def test_crear_cita(self):
        client = APIClient()
        login = client.post('/api/auth/login/', {
            'correo': 'paciente@test.com', 'password': 'Test1234!'
        }, format='json')
        self.assertEqual(login.status_code, 200, f'Login failed: {login.data}')
        token = login.data['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = client.post('/api/citas/', {
            'id_horario': self.horario.id_horario, 'motivo': 'Consulta general'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f'Create failed: {response.data}')

    def test_cancelar_cita(self):
        cita = citas.objects.create(
            id_paciente=self.paciente, id_horario=self.horario,
            id_estado=self.estado_pendiente, motivo='Test'
        )
        self.horario.disponible = False
        self.horario.save()
        client = APIClient()
        login = client.post('/api/auth/login/', {
            'correo': 'paciente@test.com', 'password': 'Test1234!'
        }, format='json')
        token = login.data['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = client.put(f'/api/citas/{cita.id_cita}/cancelar/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cita.refresh_from_db()
        self.assertEqual(cita.id_estado.nombre, 'cancelada')


class MedicoTests(BaseTestCase):
    def test_listar_medicos(self):
        client = APIClient()
        login = client.post('/api/auth/login/', {
            'correo': 'paciente@test.com', 'password': 'Test1234!'
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')
        response = client.get('/api/medicos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ver_disponibilidad(self):
        client = APIClient()
        login = client.post('/api/auth/login/', {
            'correo': 'paciente@test.com', 'password': 'Test1234!'
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')
        response = client.get(f'/api/medicos/{self.medico.id_medico_id}/disponibilidad/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AdminTests(BaseTestCase):
    def test_bloquear_usuario(self):
        client = APIClient()
        login = client.post('/api/auth/login/', {
            'correo': 'admin@test.com', 'password': 'Test1234!'
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')
        response = client.put(f'/api/admin/usuarios/{self.paciente_user.id_usuario}/bloquear/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['activo'])

    def test_reportes(self):
        client = APIClient()
        login = client.post('/api/auth/login/', {
            'correo': 'admin@test.com', 'password': 'Test1234!'
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')
        response = client.get('/api/admin/reportes/?tipo=cancelaciones')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordRecoveryTests(BaseTestCase):
    def test_forgot_password(self):
        client = APIClient()
        response = client.post('/api/auth/forgot-password/', {
            'correo': 'paciente@test.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
