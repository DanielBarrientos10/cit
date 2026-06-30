"""
Comando para generar datos de prueba masivos con información realista.
Uso: python manage.py seed_database
"""
from django.core.management.base import BaseCommand
from citas._internal.seed_runner import seed_database


class Command(BaseCommand):
    help = 'Genera datos de prueba masivos: médicos, pacientes, horarios, citas, historial y notificaciones.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean', action='store_true',
            help='Elimina datos existentes antes de generar nuevos.',
        )

    def handle(self, *args, **kwargs):
        if kwargs['clean']:
            from citas.models import (
                usuario, medicos, pacientes, horarios, citas,
                historial_clinico, notificaciones, auditoria_citas,
                medico_especialidad, rol
            )
            self.stdout.write('Limpiando datos anteriores...')
            notificaciones.objects.all().delete()
            auditoria_citas.objects.all().delete()
            historial_clinico.objects.all().delete()
            citas.objects.all().delete()
            horarios.objects.all().delete()
            medico_especialidad.objects.all().delete()
            medicos.objects.all().delete()
            pacientes.objects.all().delete()
            usuario.objects.exclude(correo='admin@medicita.com').delete()
            self.stdout.write(self.style.WARNING('Datos eliminados (excepto admin).'))

        self.stdout.write(self.style.SUCCESS('Iniciando generación de seed data...\n'))
        stats = seed_database(stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS('\n¡Seed data generado exitosamente!'))
