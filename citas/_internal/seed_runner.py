"""
Seed data runner - Generación masiva de datos realistas para MediCita.
Contiene toda la lógica de generación de datos de prueba.
"""
import random
from datetime import date, timedelta, time, datetime, timezone
from django.contrib.auth.hashers import make_password


NOMBRES_MASCULINOS = [
    'Carlos', 'Andrés', 'Juan', 'Miguel', 'Santiago', 'Sebastián', 'Mateo',
    'Nicolás', 'Alejandro', 'Diego', 'Daniel', 'Samuel', 'Lucas', 'Gabriel',
    'Emilio', 'Joaquín', 'Tomás', 'Felipe', 'Martín', 'Adrián',
    'Ricardo', 'Fernando', 'Gustavo', 'Rafael', 'Roberto', 'Luis', 'Pedro',
    'Jorge', 'Manuel', 'David', 'Pablo', 'Sergio', 'Eduardo', 'Mauricio',
    'Camilo', 'Andrés', 'Kevin', 'Brayan', 'Steven', 'Cristian',
]

NOMBRES_FEMENINOS = [
    'María', 'Sofía', 'Valentina', 'Isabella', 'Camila', 'Luciana', 'Gabriela',
    'Daniela', 'Victoria', 'Martina', 'Lucía', 'Mariana', 'Paula', 'Regina',
    'Ana', 'Laura', 'Carolina', 'Diana', 'Claudia', 'Patricia',
    'Lorena', 'Sandra', 'Mónica', 'Adriana', 'Catalina', 'Alejandra',
    'Natalia', 'Andrea', 'Juliana', 'Tatiana', 'Vanessa', 'Yeimmy',
    'Luisa', 'Fernanda', 'Ximena', 'Julia', 'Elena', 'Rosa', 'Carmen', 'Isabel',
]

APELLIDOS = [
    'Rodríguez', 'García', 'Martínez', 'López', 'González', 'Hernández',
    'Ramírez', 'Torres', 'Flórez', 'Morales', 'Romero', 'Gutiérrez',
    'Álvarez', 'Rojas', 'Mendoza', 'Castro', 'Vargas', 'Jiménez',
    'Ruiz', 'Suárez', 'Rincón', 'Medina', 'Arango', 'Gómez',
    'Ospina', 'Muñoz', 'Cardona', 'Restrepo', 'Zuluaga', 'Velásquez',
    'Henao', 'Londoño', 'Carvajal', 'Aristizábal', 'Echeverri', 'Mejía',
    'Salazar', 'Pedraza', 'Córdoba', 'Becerra',
]

EPS_LISTA = [
    'Sura', 'Sanitas', 'Coomeva', 'Salud Total', 'Compensar',
    'Famisanar', 'Colsanitas', 'Medimás', 'Nueva EPS', 'Aliansalud',
    'Comfandi', 'Comfama', 'Yompí', 'Esenttia', 'Cafesalud',
]

MOTIVOS_CITA = [
    'Dolor de cabeza persistente desde hace 3 días',
    'Chequeo general anual de control',
    'Dolor lumbar bajo que se intensifica al caminar',
    'Revisión de resultados de exámenes de sangre',
    'Control de presión arterial - hipertensión diagnosticada',
    'Erupción cutánea en antebrazo derecho',
    'Malestar estomacal después de comer',
    'Dolor en el pecho al respirar profundo',
    'Frecuentes mareos y náuseas desde la semana pasada',
    'Seguimiento post-operatorio de apendicitis',
    'Dolor articular en rodilla izquierda',
    'Consulta para renovación de receta médica',
    'Problemas de visión - dificultad para leer a distancia',
    'Insomnio y dificultad para conciliar el sueño',
    'Dolor de garganta y fiebre alta desde hace 2 días',
    'Control de diabetes tipo 2 - resultados recientes',
    'Ansiedad y episodios de angustia frecuentes',
    'Dolor abdominal recurrente después de las comidas',
    'Revisión de lunar que ha cambiado de forma',
    'Control prenatal - semana 24 de gestación',
    'Fractura en muñeca derecha - seguimiento',
    'Alergias estacionales - estornudos y moqueoconstante',
    'Dolor en la mandíbula al masticar',
    'Examen de rutina pre-operatorio',
    'Consulta sobre tratamiento para acné quístico',
    'Dolor en el cuello por mala postura laboral',
    'Tos seca persistente por más de 2 semanas',
    'Control de colesterol alto después de dieta',
    'Evaluación de síntomas de gastritis',
    'Seguimiento de tratamiento antidepresivo',
]

DIAGNOSTICOS = [
    'Cefalea tensional - estrés laboral como factor desencadenante. Se recomienda descanso y analgésicos.',
    'Paciente sano, sin hallazgos relevantes. Se programan exámenes de control anual.',
    'Lumbalgia mecánica grado II. Se sugiere fisioterapia y antiinflamatorios.',
    'Hemograma completo dentro de parámetros normales. Colesterol LDL ligeramente elevado.',
    'Hipertensión arterial etapa 1. Se ajusta dosis de Losartán a 50mg diarios.',
    'Dermatitis de contacto por agente irritante. Se prescribe crema de betametasona.',
    'Gastritis leve. Se inicia tratamiento con omeprazol 20mg por 30 días.',
    'Dolor torácico musculoesquelético. ECG y radiografía sin alteraciones.',
    'Migraña sin aura. Se indica sumatriptán 50mg y seguimiento mensual.',
    'Post-operatorio satisfactorio. Herida quirúrgica sin signos de infección.',
    'Gonartrosis incipiente. Se prescribe condroitín sulfato y ejercicios de bajo impacto.',
    'Renovación de tratamiento para hipertensión arterial crónica.',
    'Presbicia. Se indica graduación para lentes de lectura.',
    'Trastorno del sueño leve. Se recomienda higiene del sueño y melatonina.',
    'Faringitis estreptocócica. Se inicia antibioticoterapia con amoxicilina.',
    'Diabetes tipo 2 controlada. HbA1c en 6.8%. Se mantiene metformina.',
    'Trastorno de ansiedad generalizada. Se ajusta dosis de sertralina.',
    'Síndrome de intestino irritable. Dieta baja en FODMAP y probióticos.',
    'Lunar benigno. Se recomienda vigilancia dermatológica cada 6 meses.',
    'Embarazo sin complicaciones. Ecografía muestra bienestar fetal.',
    'Consolidación ósea correcta. Se retira yeso en 2 semanas.',
    'Rinitis alérgica estacional. Se prescribe antihistamínico y lavados nasales.',
    'Bruxismo. Se indica uso de férula dental nocturna.',
    'Examen pre-operatorio sin contraindicaciones. Apto para cirugía.',
    'Acné vulgar grado III. Se inicia tratamiento con isotretinoína.',
    'Cervicalgia por tensión muscular. Se recomienda fisioterapia y ergonomía laboral.',
    'Bronquitis aguda. Se prescribe mucolítico y seguimiento en 1 semana.',
    'Dislipidemia mixta. Se intensifica dieta y se añade estatina.',
    'Gastritis erosiva. Se descarta H. pylori. Tratamiento con IPP por 8 semanas.',
    'Trastorno depresivo mayor en remisión parcial. Se mantiene tratamiento actual.',
]

TRATAMIENTOS = [
    'Ibuprofeno 400mg cada 8 horas por 5 días. Reposo relativo.',
    'Losartán 50mg cada 12 horas. Dieta baja en sodio. Control en 1 mes.',
    'Betametasona crema 0.05% aplicación tópica cada 12 horas por 7 días.',
    'Omeprazol 20mg en ayunas por 30 días. Evitar cafeína y picantes.',
    'Sumatriptán 50mg vía oral al inicio del cuadro. Control en 2 semanas.',
    'Fisioterapia 3 sesiones por semana por 4 semanas. Paracetamol si dolor.',
    'Amoxicilina 500mg cada 8 horas por 10 días. Completar tratamiento completo.',
    'Metformina 850mg cada 12 horas. Dieta para diabéticos. Control HbA1c en 3 meses.',
    'Sertralina 50mg diarios. Terapia psicológica semanal. Seguimiento en 1 mes.',
    'Dieta baja en FODMAP. Probiótico diario. Evitar lácteos por 2 semanas.',
    'Melatonina 3mg 30 minutos antes de dormir. Higiene del sueño.',
    'Condroitín sulfato 800mg diarios. Ejercicios de bajo impacto 30 min/día.',
    'Lentes de lectura graduados +2.0 dioptrías. Control oftalmológico anual.',
    'Férula dental nocturna. Evitar alimentos duros. Control en 1 mes.',
    'Isotretinoína 20mg diarios con comida. Evitar exposición solar. Control mensual.',
    'Fisioterapia cervical. Ejercicios de estiramiento. Analgésico si dolor.',
    'Acetilcisteína 600mg diarios. Hidratación abundante. Seguimiento en 1 semana.',
    'Atorvastatina 20mg nocte. Dieta cardioprotectora. Control lipídico en 3 meses.',
    'Pantoprazol 40mg en ayunas por 6 semanas. Control endoscópico.',
    'Ninguno - control de rutina. Próxima cita en 6 meses.',
]

NOTAS_VARIAS = [
    'Volver a control en 1 mes.',
    'Paciente refiere mejoría parcial con el tratamiento actual.',
    'Se programan exámenes complementarios para próxima cita.',
    'Paciente refiere adherencia al tratamiento. Sin efectos adversos.',
    'Se_deriv_a especialista para segunda opinión.',
    'Paciente estable. Se mantiene plan de tratamiento actual.',
    'Volver si los síntomas persisten más de 5 días.',
    'Paciente informada sobre cambios en estilo de vida.',
    'Se ajusta medicación según respuesta clínica.',
    'Próxima cita en 2 semanas para reevaluación.',
    'Sin novedad. Evolución favorable.',
    'Se recomienda interconsulta con nutricionista.',
    'Paciente presenta mejoría notable. Continuar tratamiento.',
    'Control de rutina sin hallazgos patológicos.',
    'Se sugiere práctica de actividad física moderada 3 veces por semana.',
]

NOTIFICACIONES_MENSAJES = [
    'Su cita con el {medico} ha sido confirmada para el {fecha}.',
    'Recordatorio: Tiene una cita programada mañana a las {hora}.',
    'Su cita del {fecha} ha sido cancelada. Puede reprogramar desde el panel.',
    'El Dr. {medico} ha actualizado su historial clínico.',
    'Nuevo mensaje de su médico tratante. Revise su bandeja.',
    'Su solicitud de cita está pendiente de confirmación.',
    'Se ha creado una nueva especialidad: {especialidad}.',
    'Su contraseña ha sido cambiada exitosamente.',
    'Cita completada exitosamente. Puede calificar su experiencia.',
    'Recordatorio: Faltan 3 días para su próxima cita médica.',
]


def _random_name(gender=None):
    if gender == 'M':
        first = random.choice(NOMBRES_MASCULINOS)
    elif gender == 'F':
        first = random.choice(NOMBRES_FEMENINOS)
    else:
        first = random.choice(NOMBRES_MASCULINOS + NOMBRES_FEMENINOS)
    last1 = random.choice(APELLIDOS)
    last2 = random.choice(APELLIDOS)
    return f'{first} {last1} {last2}'


def _random_phone():
    prefix = random.choice(['300', '301', '302', '304', '305', '310', '311', '312', '313', '314', '315', '316', '320', '321', '322'])
    num = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f'{prefix}{num}'


def _random_doc_number(prefix, idx):
    digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f'{prefix}{digits}'


def _random_alergias():
    alergias_pool = [
        'Penicilina', 'Sulfas', 'Mariscos', 'Látex', 'Polen', 'Ácaros',
        'Aspirina', 'Ibuprofeno', 'Ninguna conocida', 'Picadura de abeja',
        'Lactosa', 'Gluten', 'Nueces', 'Maní', 'Huevo',
    ]
    n = random.randint(0, 3)
    if n == 0:
        return 'Ninguna conocida'
    return ', '.join(random.sample(alergias_pool, n))


def seed_database(stdout=None):
    """
    Función principal que genera datos de prueba masivos.
    Retorna un dict con estadísticas de lo creado.
    """
    from citas.models import (
        usuario, rol, medicos, pacientes, especialidades,
        medico_especialidad, horarios, estados_cita, citas,
        historial_clinico, notificaciones, auditoria_citas
    )

    log = stdout or __import__('sys').stdout

    stats = {'medicos': 0, 'pacientes': 0, 'horarios': 0, 'citas': 0, 'historiales': 0, 'notificaciones': 0}

    # --- Roles ---
    rol_admin, _ = rol.objects.get_or_create(nombre='admin')
    rol_medico, _ = rol.objects.get_or_create(nombre='medico')
    rol_paciente, _ = rol.objects.get_or_create(nombre='paciente')

    # --- Estados de cita ---
    estados = {}
    for nombre in ['pendiente', 'confirmada', 'realizada', 'cancelada', 'no_asistio']:
        obj, _ = estados_cita.objects.get_or_create(nombre=nombre)
        estados[nombre] = obj

    # --- Especialidades ---
    nombres_esp = [
        'Cardiología', 'Dermatología', 'Pediatría', 'Neurología',
        'Ortopedia', 'Ginecología', 'Oftalmología', 'Psiquiatría',
        'Medicina General', 'Odontología', 'Endocrinología', 'Gastroenterología',
        'Neumología', 'Urología', 'Reumatología', 'Otorrinolaringología',
    ]
    esp_objs = {}
    for nombre in nombres_esp:
        obj, _ = especialidades.objects.get_or_create(nombre=nombre)
        esp_objs[nombre] = obj
    todas_esp = list(esp_objs.values())

    # --- Admin user ---
    admin_user, created = usuario.objects.get_or_create(
        correo='admin@medicita.com',
        defaults={
            'nombre_completo': 'Administrador MediCita',
            'documento': '000000001',
            'telefono': '3000000000',
            'id_rol': rol_admin,
            'activo': True,
            'password': make_password('Admin123!'),
        }
    )
    if created:
        log.write('[OK] Admin user created\n')

    # --- Crear 8 médicos ---
    medicos_data = [
        ('Andrés Felipe Gómez', 'CARD', 'Cardiología', '101A'),
        ('María Elena Restrepo', 'DERM', 'Dermatología', '202B'),
        ('Carlos Alberto Muñoz', 'PEDI', 'Pediatría', '303A'),
        ('Diana Patricia Flórez', 'NEUR', 'Neurología', '404C'),
        ('Jorge Luis Ospina', 'ORTO', 'Ortopedia', '505A'),
        ('Laura Sofía Henao', 'GINE', 'Ginecología', '606B'),
        ('Santiago Moreno Velásquez', 'OFTAL', 'Oftalmología', '707A'),
        ('Valentina Álvarez Cardona', 'PSIQ', 'Psiquiatría', '808C'),
    ]

    medicos_creados = []
    for idx, (nombre, prefix, especialidad, consultorio) in enumerate(medicos_data):
        correo = f'dr{prefix.lower()}@medicita.com'
        u, created = usuario.objects.get_or_create(
            correo=correo,
            defaults={
                'nombre_completo': nombre,
                'documento': _random_doc_number(prefix, idx),
                'telefono': _random_phone(),
                'id_rol': rol_medico,
                'activo': True,
                'password': make_password('Medico123!'),
            }
        )
        if created:
            stats['medicos'] += 1
        m, _ = medicos.objects.get_or_create(
            id_medico=u,
            defaults={
                'registro_profesional': f'RP-{random.randint(10000, 99999)}',
                'consultorio': consultorio,
                'estado': 'activo',
            }
        )
        medico_especialidad.objects.get_or_create(
            id_medico=m,
            id_especialidad=esp_objs[especialidad]
        )
        # Asignar 1-2 especialidades extra
        extra_esp = [e for e in todas_esp if e.nombre != especialidad]
        for extra in random.sample(extra_esp, random.randint(0, 2)):
            medico_especialidad.objects.get_or_create(id_medico=m, id_especialidad=extra)
        medicos_creados.append(m)

    log.write(f'[OK] {stats["medicos"]} médicos creados (total: {len(medicos_creados)})\n')

    # --- Crear 20 pacientes ---
    pacientes_creados = []
    for i in range(20):
        gender = random.choice(['M', 'F'])
        nombre = _random_name(gender)
        correo = f'paciente{i+1:02d}@medicita.com'
        u, created = usuario.objects.get_or_create(
            correo=correo,
            defaults={
                'nombre_completo': nombre,
                'documento': _random_doc_number('CC', i),
                'telefono': _random_phone(),
                'id_rol': rol_paciente,
                'activo': True,
                'password': make_password('Paciente123!'),
            }
        )
        if created:
            stats['pacientes'] += 1
        year = random.randint(1955, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        p, _ = pacientes.objects.get_or_create(
            id_paciente=u,
            defaults={
                'fecha_nacimiento': date(year, month, day),
                'sexo': gender,
                'eps': random.choice(EPS_LISTA),
                'alergias': _random_alergias(),
            }
        )
        pacientes_creados.append(p)

    log.write(f'[OK] {stats["pacientes"]} pacientes creados (total: {len(pacientes_creados)})\n')

    # --- Crear horarios (14 días) ---
    today = date.today()
    horas_disponibles = [
        (time(7, 0), time(8, 0)),
        (time(8, 0), time(9, 0)),
        (time(9, 0), time(10, 0)),
        (time(10, 0), time(11, 0)),
        (time(11, 0), time(12, 0)),
        (time(14, 0), time(15, 0)),
        (time(15, 0), time(16, 0)),
        (time(16, 0), time(17, 0)),
        (time(17, 0), time(18, 0)),
    ]

    todos_horarios = []
    for medico in medicos_creados:
        # 2-3 días por médico, 3-5 slots cada día
        num_days = random.randint(2, 4)
        dias_seleccionados = sorted(random.sample(range(0, 14), num_days))
        for day_offset in dias_seleccionados:
            fecha_h = today + timedelta(days=day_offset)
            num_slots = random.randint(3, 5)
            slots_hoy = random.sample(horas_disponibles, num_slots)
            for hora_i, hora_f in slots_hoy:
                h, created = horarios.objects.get_or_create(
                    id_medico=medico,
                    fecha=fecha_h,
                    hora_inicio=hora_i,
                    hora_fin=hora_f,
                    defaults={'disponible': True}
                )
                if created:
                    stats['horarios'] += 1
                todos_horarios.append(h)

    log.write(f'[OK] {stats["horarios"]} horarios creados\n')

    # --- Crear citas ---
    horarios_libres = list(horarios.objects.filter(disponible=True).select_related('id_medico'))
    random.shuffle(horarios_libres)

    # 60% de los horarios se ocupan con citas
    num_citas = int(len(horarios_libres) * 0.6)
    horarios_a_ocupar = horarios_libres[:num_citas]

    now = datetime.now(timezone.utc)

    for h in horarios_a_ocupar:
        pac = random.choice(pacientes_creados)

        # Distribución: 25% realizadas, 5% canceladas, 5% no_asistio, 65% pendientes/confirmadas
        r = random.random()
        if r < 0.05:
            est = estados['cancelada']
        elif r < 0.10:
            est = estados['no_asistio']
        elif r < 0.35:
            est = estados['realizada']
        elif r < 0.55:
            est = estados['confirmada']
        else:
            est = estados['pendiente']

        cita, created = citas.objects.get_or_create(
            id_paciente=pac,
            id_horario=h,
            defaults={
                'id_estado': est,
                'motivo': random.choice(MOTIVOS_CITA),
            }
        )
        if not created:
            continue

        stats['citas'] += 1

        # Marcar horario como ocupado
        h.disponible = False
        h.save(update_fields=['disponible'])

        # Si cancelada, registrar quién canceló
        if est == estados['cancelada']:
            cita.cancelada_por = pac.id_paciente
            cita.fecha_cancelacion = now - timedelta(days=random.randint(1, 5))
            cita.save(update_fields=['cancelada_por', 'fecha_cancelacion'])

        # Auditoría
        auditoria_citas.objects.create(
            id_cita=cita,
            evento='cita_creada',
            id_usuario_actor=pac.id_paciente,
        )

        # Historial clínico para citas realizadas
        if est == estados['realizada']:
            hist, created_h = historial_clinico.objects.get_or_create(
                id_paciente=pac,
                id_medico=h.id_medico,
                fecha=h.fecha,
                defaults={
                    'diagnostico': random.choice(DIAGNOSTICOS),
                    'tratamiento': random.choice(TRATAMIENTOS),
                    'notas': random.choice(NOTAS_VARIAS),
                }
            )
            if created_h:
                stats['historiales'] += 1

        # Notificaciones
        medico_nombre = h.id_medico.id_medico.nombre_completo.split()[-1]
        if est in (estados['pendiente'], estados['confirmada']):
            msg = random.choice(NOTIFICACIONES_MENSAJES[:3]).format(
                medico=medico_nombre,
                fecha=h.fecha.strftime('%d/%m/%Y'),
                hora=h.hora_inicio.strftime('%H:%M'),
            )
            notificaciones.objects.create(
                id_usuario=pac.id_paciente,
                mensaje=msg,
                leida=random.choice([True, False]),
            )
            notificaciones.objects.create(
                id_usuario=h.id_medico.id_medico.id_usuario,
                mensaje=f'Nueva cita con {pac.id_paciente.nombre_completo} - {h.fecha.strftime("%d/%m/%Y")}',
                leida=random.choice([True, False]),
            )
            stats['notificaciones'] += 2

    log.write(f'[OK] {stats["citas"]} citas creadas\n')
    log.write(f'[OK] {stats["historiales"]} historiales clínicos creados\n')
    log.write(f'[OK] {stats["notificaciones"]} notificaciones creadas\n')

    # --- Notificaciones adicionales para admin ---
    admin_notifs = [
        'Sistema inicializado correctamente. Bienvenido a MediCita.',
        'Hay 3 nuevas solicitudes de registro de médicos pendientes.',
        'Reporte mensual disponible: 45 citas completadas este mes.',
        'Actualización del sistema aplicada exitosamente.',
        'Nuevo médico registrado: Dr. Santiago Moreno - Oftalmología.',
    ]
    for msg in admin_notifs:
        notificaciones.objects.create(
            id_usuario=admin_user,
            mensaje=msg,
            leida=False,
        )

    log.write(f'\n{"="*50}\n')
    log.write(f'  RESUMEN DE SEED DATA\n')
    log.write(f'{"="*50}\n')
    log.write(f'  Medicos:            {stats["medicos"]}\n')
    log.write(f'  Pacientes:          {stats["pacientes"]}\n')
    log.write(f'  Horarios:           {stats["horarios"]}\n')
    log.write(f'  Citas:              {stats["citas"]}\n')
    log.write(f'  Historiales:        {stats["historiales"]}\n')
    log.write(f'  Notificaciones:     {stats["notificaciones"]}\n')
    log.write(f'{"="*50}\n')
    log.write(f'  Credenciales de prueba:\n')
    log.write(f'    Admin:    admin@medicita.com / Admin123!\n')
    log.write(f'    Médico:   drcard@medicita.com / Medico123!\n')
    log.write(f'    Paciente: paciente01@medicita.com / Paciente123!\n')
    log.write(f'{"="*50}\n')

    return stats
