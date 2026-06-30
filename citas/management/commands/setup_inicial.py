"""
Comando de setup inicial para el Sistema de Gestión de Citas Médicas.
Uso: python manage.py setup_inicial
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Aplica los datos iniciales del sistema (roles, estados, especialidades y usuario admin)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('  MediCita - Setup Inicial del Sistema')
        self.stdout.write('=' * 50)
        self.stdout.write('')

        self.stdout.write('[*] Aplicando fixture de datos iniciales...')
        try:
            call_command('loaddata', 'citas/fixtures/initial_data.json', verbosity=0)
            self.stdout.write(self.style.SUCCESS('[OK] Fixture aplicado correctamente'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'[!]  El fixture ya estaba aplicado o hubo un conflicto: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('[OK] Setup completado exitosamente'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('[*] Inicia el servidor con:')
        self.stdout.write('    python manage.py runserver')
        self.stdout.write('')
        self.stdout.write('[*] Credenciales del administrador:')
        self.stdout.write('    Correo:     admin@medicita.com')
        self.stdout.write('    Contrasena: Admin123!')
        self.stdout.write('')
        self.stdout.write('[*] API Docs: http://127.0.0.1:8000/swagger/')
        self.stdout.write('[*] App:      http://127.0.0.1:8000/')
        self.stdout.write('')
