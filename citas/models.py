from django.db import models
from django.db.models import F, Q, CheckConstraint
from django.db.models import CASCADE as cascade
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class rol(models.Model):
    id_rol=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=50,unique=True)
    
class usuariomanager(BaseUserManager):
    def create_user(self,correo,documento,password=None,**extra_fields):
        if not correo:
            raise ValueError('el correo es obligatorio')
        correo=self.normalize_email(correo)
        user=self.model(correo=correo,documento=documento,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
class usuario(AbstractBaseUser):
    id_usuario=models.AutoField(primary_key=True)
    correo=models.EmailField(unique=True,null=False)
    nombre_completo=models.CharField(max_length=255)
    documento=models.CharField(max_length=50,unique=True)
    telefono=models.CharField(max_length=20)
    id_rol=models.ForeignKey(rol,on_delete=models.SET_NULL,null=True)
    activo=models.BooleanField(default=True)
    intentos_fallidos=models.IntegerField(default=0)
    bloqueado_hasta=models.DateTimeField(null=True,blank=True)
    
    objects=usuariomanager()
    
    USERNAME_FIELD='correo'
    REQUIRED_FIELDS=['documento','nombre_completo']

class pacientes(models.Model):
    id_paciente=models.OneToOneField(usuario,on_delete=cascade,primary_key=True,db_column='id_usuario')
    fecha_nacimiento=models.DateField(null=True,blank=True)
    sexo=models.CharField(max_length=1,null=True,blank=True)
    eps=models.CharField(max_length=100,blank=True,default='')
    alergias=models.TextField(blank=True,null=True)
    
class medicos(models.Model):
    id_medico=models.OneToOneField(usuario,on_delete=cascade,primary_key=True,db_column='id_usuario')
    registro_profesional=models.CharField(max_length=50,unique=True)
    consultorio=models.CharField(max_length=50)
    estado=models.CharField(max_length=20,default='activo')
    
class especialidades(models.Model):
    id_especialidad=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100,unique=True)
    
class medico_especialidad(models.Model):
    id_medico=models.ForeignKey(medicos,on_delete=cascade)
    id_especialidad=models.ForeignKey(especialidades,on_delete=cascade)
    
    class Meta:
        unique_together=('id_medico','id_especialidad')

class horarios(models.Model):
    id_horario=models.AutoField(primary_key=True)
    id_medico=models.ForeignKey(medicos,on_delete=cascade)
    fecha=models.DateField()
    hora_inicio=models.TimeField()
    hora_fin=models.TimeField()
    disponible=models.BooleanField(default=True)
    
    class Meta:
        unique_together=('id_medico','fecha','hora_inicio','hora_fin')
        constraints=[CheckConstraint(condition=Q(hora_fin__gt=F('hora_inicio')),name='chk_hora_fin_mayor')]

class estados_cita(models.Model):
    id_estado=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=50,unique=True)

class citas(models.Model):
    id_cita=models.AutoField(primary_key=True)
    id_paciente=models.ForeignKey(pacientes,on_delete=cascade)
    id_horario=models.OneToOneField(horarios,on_delete=cascade,unique=True)
    id_estado=models.ForeignKey(estados_cita,on_delete=models.RESTRICT)
    motivo=models.TextField()
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    fecha_actualizacion=models.DateTimeField(auto_now=True)
    cancelada_por=models.ForeignKey(usuario,on_delete=models.SET_NULL,null=True,blank=True)
    fecha_cancelacion=models.DateTimeField(null=True,blank=True)
    
class auditoria_citas(models.Model):
    id_auditoria=models.AutoField(primary_key=True)
    id_cita=models.ForeignKey(citas,on_delete=cascade)
    evento=models.CharField(max_length=100)
    id_usuario_actor=models.ForeignKey(usuario,on_delete=models.SET_NULL,null=True)
    fecha_evento=models.DateTimeField(auto_now_add=True)

class tokens_recuperacion(models.Model):
    id_token=models.AutoField(primary_key=True)
    id_usuario=models.ForeignKey(usuario,on_delete=cascade)
    token=models.CharField(max_length=255,unique=True)
    expira_en=models.DateTimeField()
    usado=models.BooleanField(default=False)

class historial_clinico(models.Model):
    id_historial=models.AutoField(primary_key=True)
    id_paciente=models.ForeignKey(pacientes,on_delete=cascade)
    id_medico=models.ForeignKey(medicos,on_delete=cascade)
    fecha=models.DateField()
    diagnostico=models.TextField()
    tratamiento=models.TextField(blank=True,null=True)
    notas=models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

class notificaciones(models.Model):
    id_notificacion=models.AutoField(primary_key=True)
    id_usuario=models.ForeignKey(usuario,on_delete=cascade)
    mensaje=models.TextField()
    leida=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
