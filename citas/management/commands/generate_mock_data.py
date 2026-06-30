"""
Comando heredado - delega al nuevo seed_database.
Se mantiene por compatibilidad. Usa 'python manage.py seed_database' para la version completa.
"""
from django.core.management.base import BaseCommand
from citas._internal.seed_runner import seed_database


class Command(BaseCommand):
    help = 'Genera datos de prueba (version legacy). Usa seed_database para la version completa.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Este comando esta obsoleto. Usando seed_database...\n'))
        seed_database(stdout=self.stdout)
