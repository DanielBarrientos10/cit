"""
Runner independiente para generar seed data.
Ejecutar desde la raíz del proyecto:
    python run_seed.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_citas.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from citas._internal.seed_runner import seed_database

if __name__ == '__main__':
    seed_database()
