from rest_framework import serializers
from .models import (
    rol, usuario, pacientes, medicos, especialidades,
    medico_especialidad, horarios, estados_cita, citas,
    auditoria_citas, tokens_recuperacion, historial_clinico, notificaciones
)

class rolSerializer(serializers.ModelSerializer):
    class Meta:
        model = rol
        fields = ['id_rol', 'nombre']

class usuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    id_rol_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = usuario
        fields = ['id_usuario', 'correo', 'nombre_completo', 'documento', 'telefono', 'id_rol', 'id_rol_nombre', 'activo', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def get_id_rol_nombre(self, obj):
        return obj.id_rol.nombre if obj.id_rol else None

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_password(self, value):
        import re
        if len(value) < 8:
            raise serializers.ValidationError('la contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('la contraseña debe contener al menos una mayúscula')
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('la contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError('la contraseña debe contener al menos un carácter especial')
        return value

class pacientesSerializer(serializers.ModelSerializer):
    usuario_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = pacientes
        fields = ['id_paciente', 'usuario_info', 'fecha_nacimiento', 'sexo', 'eps', 'alergias']

    def get_usuario_info(self, obj):
        if obj.id_paciente:
            return {'id': obj.id_paciente.id_usuario, 'nombre': obj.id_paciente.nombre_completo, 'correo': obj.id_paciente.correo}
        return None

class medicosSerializer(serializers.ModelSerializer):
    usuario_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = medicos
        fields = ['id_medico', 'usuario_info', 'registro_profesional', 'consultorio', 'estado']

    def get_usuario_info(self, obj):
        if obj.id_medico:
            return {'id': obj.id_medico.id_usuario, 'nombre': obj.id_medico.nombre_completo, 'correo': obj.id_medico.correo}
        return None

class especialidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = especialidades
        fields = ['id_especialidad', 'nombre']

class medico_especialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = medico_especialidad
        fields = ['id_medico', 'id_especialidad']

class horariosSerializer(serializers.ModelSerializer):
    medico_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = horarios
        fields = ['id_horario', 'id_medico', 'medico_nombre', 'fecha', 'hora_inicio', 'hora_fin', 'disponible']

    def get_medico_nombre(self, obj):
        if obj.id_medico and obj.id_medico.id_medico:
            return obj.id_medico.id_medico.nombre_completo
        return None

class estados_citaSerializer(serializers.ModelSerializer):
    class Meta:
        model = estados_cita
        fields = ['id_estado', 'nombre']

class citasSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.SerializerMethodField(read_only=True)
    medico_nombre = serializers.SerializerMethodField(read_only=True)
    estado_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = citas
        fields = [
            'id_cita', 'id_paciente', 'paciente_nombre',
            'id_horario', 'medico_nombre',
            'id_estado', 'estado_nombre',
            'motivo', 'fecha_creacion', 'fecha_actualizacion',
            'cancelada_por', 'fecha_cancelacion'
        ]
        read_only_fields = [
            'id_paciente', 'id_estado',
            'fecha_creacion', 'fecha_actualizacion',
            'cancelada_por', 'fecha_cancelacion'
        ]

    def get_paciente_nombre(self, obj):
        if obj.id_paciente and obj.id_paciente.id_paciente:
            return obj.id_paciente.id_paciente.nombre_completo
        return None

    def get_medico_nombre(self, obj):
        if obj.id_horario and obj.id_horario.id_medico and obj.id_horario.id_medico.id_medico:
            return obj.id_horario.id_medico.id_medico.nombre_completo
        return None

    def get_estado_nombre(self, obj):
        return obj.id_estado.nombre if obj.id_estado else None

class auditoria_citasSerializer(serializers.ModelSerializer):
    class Meta:
        model = auditoria_citas
        fields = ['id_auditoria', 'id_cita', 'evento', 'id_usuario_actor', 'fecha_evento']

class tokens_recuperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = tokens_recuperacion
        fields = ['id_token', 'id_usuario', 'token', 'expira_en', 'usado']

class historial_clinicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = historial_clinico
        fields = ['id_historial', 'id_paciente', 'id_medico', 'fecha', 'diagnostico', 'tratamiento', 'notas', 'created_at']
        read_only_fields = ['created_at']

class notificacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = notificaciones
        fields = ['id_notificacion', 'id_usuario', 'mensaje', 'leida', 'created_at']
        read_only_fields = ['created_at']
