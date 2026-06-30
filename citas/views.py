from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count
from rest_framework import generics, status, permissions, views, serializers, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    usuarioSerializer, citasSerializer, horariosSerializer,
    especialidadesSerializer, medicosSerializer, pacientesSerializer,
    medico_especialidadSerializer, estados_citaSerializer,
    auditoria_citasSerializer, tokens_recuperacionSerializer,
    historial_clinicoSerializer, notificacionesSerializer
)
from .models import (
    usuario, citas, horarios, estados_cita, especialidades,
    medicos, pacientes, medico_especialidad, auditoria_citas,
    tokens_recuperacion, historial_clinico, notificaciones, rol
)
from .permissions import IsPaciente, IsMedico, IsAdmin
import secrets
import re

# ─────────── AUTH ───────────

class RegisterView(generics.CreateAPIView):
    queryset = usuario.objects.all()
    serializer_class = usuarioSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        rol_paciente, _ = rol.objects.get_or_create(nombre='paciente')
        user.id_rol = rol_paciente
        user.save()
        pacientes.objects.create(id_paciente=user)

class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        correo = request.data.get('correo', '')
        password = request.data.get('password', '')

        try:
            user = usuario.objects.get(correo=correo)
        except usuario.DoesNotExist:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.activo:
            return Response({'detail': 'Cuenta inactiva'}, status=status.HTTP_403_FORBIDDEN)

        if user.bloqueado_hasta and timezone.now() < user.bloqueado_hasta:
            remaining = (user.bloqueado_hasta - timezone.now()).seconds // 60
            return Response(
                {'detail': f'Cuenta bloqueada. Intente nuevamente en {remaining} minutos'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if not user.check_password(password):
            user.intentos_fallidos += 1
            if user.intentos_fallidos >= 3:
                user.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
            user.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        user.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])

        return super().post(request, *args, **kwargs)

class ForgotPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        correo = request.data.get('correo')
        if not correo:
            return Response({'detail': 'Correo es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = usuario.objects.get(correo=correo)
        except usuario.DoesNotExist:
            return Response({'detail': 'Si el correo existe, recibirá un enlace de recuperación'}, status=status.HTTP_200_OK)

        token = secrets.token_urlsafe(48)
        tokens_recuperacion.objects.create(
            id_usuario=user,
            token=token,
            expira_en=timezone.now() + timedelta(hours=1)
        )
        from django.core.mail import send_mail
        send_mail(
            'Recuperación de contraseña',
            f'Use este token para recuperar su contraseña: {token}',
            'noreply@sistema-citas.com',
            [user.correo],
            fail_silently=True,
        )
        return Response({'detail': 'Si el correo existe, recibirá un enlace de recuperación'}, status=status.HTTP_200_OK)

class ResetPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_str = request.data.get('token')
        new_password = request.data.get('password')
        if not token_str or not new_password:
            return Response({'detail': 'Token y contraseña son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8 or not re.search(r'[A-Z]', new_password) or not re.search(r'[0-9]', new_password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            return Response({'detail': 'La contraseña debe tener mínimo 8 caracteres, 1 mayúscula, 1 número y 1 carácter especial'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = tokens_recuperacion.objects.get(token=token_str, usado=False, expira_en__gt=timezone.now())
        except tokens_recuperacion.DoesNotExist:
            return Response({'detail': 'Token inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)

        user = token.id_usuario
        user.set_password(new_password)
        user.save()
        token.usado = True
        token.save()
        return Response({'detail': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)

class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        user_id = pk if pk else request.user.id_usuario
        try:
            user = usuario.objects.get(id_usuario=user_id)
        except usuario.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = usuarioSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk=None):
        user_id = pk if pk else request.user.id_usuario
        if request.user.id_usuario != user_id and not IsAdmin().has_permission(request, None):
            return Response({'detail': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = usuario.objects.get(id_usuario=user_id)
        except usuario.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = usuarioSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not IsAdmin().has_permission(request, None):
            return Response({'detail': 'Solo administradores pueden eliminar usuarios'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = usuario.objects.get(id_usuario=pk)
            user.activo = False
            user.save()
            return Response({'detail': 'Usuario desactivado'}, status=status.HTTP_200_OK)
        except usuario.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ─────────── USERS LIST (ADMIN) ───────────

class UserListView(generics.ListAPIView):
    queryset = usuario.objects.all()
    serializer_class = usuarioSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['correo', 'nombre_completo', 'documento']

# ─────────── MEDICOS ───────────

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = medicos.objects.select_related('id_medico').all()
    serializer_class = medicosSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'disponibilidad']:
            return [permissions.IsAuthenticated()]
        if self.action == 'especialidades' and self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        rol_medico, _ = rol.objects.get_or_create(nombre='medico')
        user_data = self.request.data.get('usuario')
        if user_data:
            user_serializer = usuarioSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            user.id_rol = rol_medico
            user.save()
            serializer.save(id_medico=user)
        else:
            serializer.save()

    @action(detail=True, methods=['get', 'post', 'delete'], url_path='especialidades')
    def especialidades(self, request, pk=None):
        medico = self.get_object()
        if request.method == 'GET':
            qs = medico_especialidad.objects.filter(id_medico=medico).select_related('id_especialidad')
            data = [{'id_especialidad': me.id_especialidad.id_especialidad, 'nombre': me.id_especialidad.nombre} for me in qs]
            return Response(data)
        elif request.method == 'POST':
            esp_id = request.data.get('id_especialidad')
            try:
                esp = especialidades.objects.get(id_especialidad=esp_id)
            except especialidades.DoesNotExist:
                return Response({'detail': 'Especialidad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            _, created = medico_especialidad.objects.get_or_create(id_medico=medico, id_especialidad=esp)
            if not created:
                return Response({'detail': 'Ya tiene esta especialidad'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Especialidad asignada'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            esp_id = request.data.get('id_especialidad')
            deleted, _ = medico_especialidad.objects.filter(id_medico=medico, id_especialidad_id=esp_id).delete()
            if deleted:
                return Response({'detail': 'Especialidad removida'}, status=status.HTTP_200_OK)
            return Response({'detail': 'Especialidad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='disponibilidad')
    def disponibilidad(self, request, pk=None):
        medico = self.get_object()
        qs = horarios.objects.filter(id_medico=medico, disponible=True, fecha__gte=timezone.now().date())
        serializer = horariosSerializer(qs, many=True)
        return Response(serializer.data)

# ─────────── ESPECIALIDADES ───────────

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = especialidades.objects.all()
    serializer_class = especialidadesSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

# ─────────── HORARIOS (DISPONIBILIDAD) ───────────

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = horarios.objects.all()
    serializer_class = horariosSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsMedico() | IsAdmin()]

    def perform_create(self, serializer):
        serializer.save(disponible=True)

    @action(detail=False, methods=['post'], url_path='crear-slots')
    def crear_slots(self, request):
        medico_id = request.data.get('id_medico')
        fecha = request.data.get('fecha')
        hora_inicio = request.data.get('hora_inicio')
        hora_fin = request.data.get('hora_fin')
        duracion = int(request.data.get('duracion_minutos', 30))

        try:
            medico = medicos.objects.get(id_medico_id=medico_id)
        except medicos.DoesNotExist:
            return Response({'detail': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        from datetime import datetime as dt
        start = dt.strptime(hora_inicio, '%H:%M').time()
        end = dt.strptime(hora_fin, '%H:%M').time()
        if end <= start:
            return Response({'detail': 'hora_fin debe ser mayor a hora_inicio'}, status=status.HTTP_400_BAD_REQUEST)

        import datetime
        current = datetime.datetime.combine(datetime.date.today(), start)
        end_dt = datetime.datetime.combine(datetime.date.today(), end)
        slots_creados = []

        while current + datetime.timedelta(minutes=duracion) <= end_dt:
            slot_start = current.time()
            slot_end = (current + datetime.timedelta(minutes=duracion)).time()
            exists = horarios.objects.filter(
                id_medico=medico, fecha=fecha,
                hora_inicio__lt=slot_end, hora_fin__gt=slot_start
            ).exists()
            if not exists:
                h = horarios.objects.create(
                    id_medico=medico, fecha=fecha,
                    hora_inicio=slot_start, hora_fin=slot_end,
                    disponible=True
                )
                slots_creados.append(h.id_horario)
            current += datetime.timedelta(minutes=duracion)

        return Response({'slots_creados': len(slots_creados), 'ids': slots_creados}, status=status.HTTP_201_CREATED)

# ─────────── CITAS ───────────

class CitaViewSet(viewsets.ModelViewSet):
    queryset = citas.objects.select_related('id_paciente__id_paciente', 'id_horario', 'id_estado').all()
    serializer_class = citasSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if IsPaciente().has_permission(self.request, None):
            try:
                pac = pacientes.objects.get(id_paciente=user)
                return qs.filter(id_paciente=pac)
            except pacientes.DoesNotExist:
                return qs.none()
        if IsMedico().has_permission(self.request, None):
            try:
                med = medicos.objects.get(id_medico=user)
                return qs.filter(id_horario__id_medico=med)
            except medicos.DoesNotExist:
                return qs.none()
        return qs

    def get_permissions(self):
        if self.action == 'create':
            return [IsPaciente()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        with transaction.atomic():
            horario_id = self.request.data.get('id_horario')
            motivo = self.request.data.get('motivo', '')
            horario = horarios.objects.select_for_update().get(id_horario=horario_id)
            if not horario.disponible:
                raise serializers.ValidationError('El horario seleccionado no está disponible')
            paciente = pacientes.objects.get(id_paciente=self.request.user)
            estado = estados_cita.objects.get(nombre='pendiente')
            horario.disponible = False
            horario.save()
            cita = serializer.save(id_paciente=paciente, id_horario=horario, id_estado=estado, motivo=motivo)
            auditoria_citas.objects.create(id_cita=cita, evento='creada', id_usuario_actor=self.request.user)

    @action(detail=True, methods=['put'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        cita = self.get_object()
        horario = cita.id_horario
        start_dt = timezone.make_aware(datetime.combine(horario.fecha, horario.hora_inicio))
        is_admin = IsAdmin().has_permission(request, None)

        if not is_admin and timezone.now() > start_dt - timedelta(hours=24):
            return Response({'detail': 'No se puede cancelar con menos de 24h de antelación'}, status=status.HTTP_400_BAD_REQUEST)

        if cita.id_estado.nombre in ['cancelada', 'realizada', 'no_asistio']:
            return Response({'detail': f'La cita ya está {cita.id_estado.nombre}'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            estado = estados_cita.objects.get(nombre='cancelada')
            cita.id_estado = estado
            cita.cancelada_por = request.user
            cita.fecha_cancelacion = timezone.now()
            cita.save()
            horario.disponible = True
            horario.save()
            auditoria_citas.objects.create(id_cita=cita, evento='cancelada', id_usuario_actor=request.user)

        return Response({'detail': 'Cita cancelada correctamente'})

    @action(detail=True, methods=['put'], url_path='realizada')
    def realizada(self, request, pk=None):
        cita = self.get_object()
        if cita.id_estado.nombre in ['cancelada', 'realizada', 'no_asistio']:
            return Response({'detail': f'La cita ya está {cita.id_estado.nombre}'}, status=status.HTTP_400_BAD_REQUEST)
        if not IsMedico().has_permission(request, None) and not IsAdmin().has_permission(request, None):
            return Response({'detail': 'Solo médicos o admin pueden marcar realizada'}, status=status.HTTP_403_FORBIDDEN)
        estado = estados_cita.objects.get(nombre='realizada')
        cita.id_estado = estado
        cita.save()
        auditoria_citas.objects.create(id_cita=cita, evento='realizada', id_usuario_actor=request.user)
        return Response({'detail': 'Cita marcada como realizada'})

    @action(detail=True, methods=['put'], url_path='no-asistio')
    def no_asistio(self, request, pk=None):
        cita = self.get_object()
        if cita.id_estado.nombre in ['cancelada', 'realizada', 'no_asistio']:
            return Response({'detail': f'La cita ya está {cita.id_estado.nombre}'}, status=status.HTTP_400_BAD_REQUEST)
        if not IsMedico().has_permission(request, None) and not IsAdmin().has_permission(request, None):
            return Response({'detail': 'Solo médicos o admin pueden marcar no asistió'}, status=status.HTTP_403_FORBIDDEN)
        estado = estados_cita.objects.get(nombre='no_asistio')
        cita.id_estado = estado
        cita.save()
        auditoria_citas.objects.create(id_cita=cita, evento='no_asistio', id_usuario_actor=request.user)
        return Response({'detail': 'Cita marcada como no asistió'})

# ─────────── HISTORIAL CLINICO ───────────

class HistorialViewSet(viewsets.ModelViewSet):
    queryset = historial_clinico.objects.select_related('id_paciente__id_paciente', 'id_medico__id_medico').all()
    serializer_class = historial_clinicoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        paciente_id = self.request.query_params.get('paciente')
        if paciente_id:
            qs = qs.filter(id_paciente_id=paciente_id)
        if IsPaciente().has_permission(self.request, None):
            try:
                pac = pacientes.objects.get(id_paciente=user)
                return qs.filter(id_paciente=pac)
            except pacientes.DoesNotExist:
                return qs.none()
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsMedico() | IsAdmin()]
        return [permissions.IsAuthenticated()]

# ─────────── NOTIFICACIONES ───────────

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = notificaciones.objects.all()
    serializer_class = notificacionesSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if IsAdmin().has_permission(self.request, None):
            usuario_id = self.request.query_params.get('usuario')
            if usuario_id:
                qs = qs.filter(id_usuario_id=usuario_id)
            return qs
        return qs.filter(id_usuario=user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['put'], url_path='leer')
    def marcar_leida(self, request, pk=None):
        notif = self.get_object()
        notif.leida = True
        notif.save()
        return Response({'detail': 'Notificación marcada como leída'})

# ─────────── ADMIN ───────────

class AdminBloquearUsuarioView(views.APIView):
    permission_classes = [IsAdmin]

    def put(self, request, pk):
        try:
            user = usuario.objects.get(id_usuario=pk)
        except usuario.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        user.activo = not user.activo
        user.save()
        estado = 'activado' if user.activo else 'bloqueado'
        return Response({'detail': f'Usuario {estado} correctamente', 'activo': user.activo})

class AdminReportesView(views.APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        tipo = request.query_params.get('tipo', 'citas-por-especialidad')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if tipo == 'citas-por-especialidad':
            reporte = (
                citas.objects.values('id_horario__id_medico__id_medico__id_medico')
                .annotate(total=Count('id_cita'))
            )
            return Response({'tipo': tipo, 'data': list(reporte)})

        elif tipo == 'cancelaciones':
            total_canceladas = citas.objects.filter(id_estado__nombre='cancelada').count()
            total_general = citas.objects.count()
            return Response({
                'tipo': tipo,
                'total_canceladas': total_canceladas,
                'total_general': total_general,
                'porcentaje': round(total_canceladas / total_general * 100, 2) if total_general else 0
            })

        elif tipo == 'no-asistencia-por-medico':
            reporte = (
                citas.objects.filter(id_estado__nombre='no_asistio')
                .values('id_horario__id_medico__id_medico__nombre_completo')
                .annotate(total=Count('id_cita'))
            )
            return Response({'tipo': tipo, 'data': list(reporte)})

        return Response({'detail': 'Tipo de reporte no válido'}, status=status.HTTP_400_BAD_REQUEST)

# ─────────── BUSQUEDA MEDICOS (para pacientes) ───────────

class BuscarMedicoDisponibilidadView(generics.ListAPIView):
    serializer_class = horariosSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = horarios.objects.filter(disponible=True, fecha__gte=timezone.now().date())
        especialidad_id = self.request.query_params.get('especialidad')
        medico_id = self.request.query_params.get('medico')

        if especialidad_id:
            medicos_ids = medico_especialidad.objects.filter(
                id_especialidad_id=especialidad_id
            ).values_list('id_medico_id', flat=True)
            qs = qs.filter(id_medico_id__in=medicos_ids)

        if medico_id:
            qs = qs.filter(id_medico_id=medico_id)

        return qs.select_related('id_medico__id_medico')
