# serializers for all models

from rest_framework import serializers
from .models import rol, usuario, pacientes, medicos, especialidades, medico_especialidad, horarios, estados_cita, citas, auditoria_citas

class rolSerializer(serializers.ModelSerializer):
    class Meta:
        model = rol
        fields = ['id_rol','nombre']

class usuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = usuario
        fields = ['id_usuario','correo','nombre_completo','documento','telefono','id_rol','activo','password']
        extra_kwargs = {'password':{'write_only':True}}
    def create(self,validated_data):
        password = validated_data.pop('password')
        user = usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user
    def validate_password(self,value):
        import re
        if len(value) < 8:
            raise serializers.ValidationError('la contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]',value):
            raise serializers.ValidationError('la contraseña debe contener al menos una mayúscula')
        if not re.search(r'[0-9]',value):
            raise serializers.ValidationError('la contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]',value):
            raise serializers.ValidationError('la contraseña debe contener al menos un carácter especial')
        return value

class pacientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = pacientes
        fields = ['id_paciente','fecha_nacimiento','sexo','eps','alergias']

class medicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = medicos
        fields = ['id_medico','registro_profesional','consultorio','estado']

class especialidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = especialidades
        fields = ['id_especialidad','nombre']

class medico_especialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = medico_especialidad
        fields = ['id_medico','id_especialidad']

class horariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = horarios
        fields = ['id_horario','id_medico','fecha','hora_inicio','hora_fin','disponible']

class estados_citaSerializer(serializers.ModelSerializer):
    class Meta:
        model = estados_cita
        fields = ['id_estado','nombre']

class citasSerializer(serializers.ModelSerializer):
    class Meta:
        model = citas
        fields = ['id_cita','id_paciente','id_horario','id_estado','motivo','fecha_creacion','fecha_actualizacion','cancelada_por','fecha_cancelacion']
        read_only_fields = ['fecha_creacion','fecha_actualizacion']

class auditoria_citasSerializer(serializers.ModelSerializer):
    class Meta:
        model = auditoria_citas
        fields = ['id_auditoria','id_cita','evento','id_usuario_actor','fecha_evento']
