# views for authentication and appointment management

from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from rest_framework import generics, status, permissions, views, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import usuarioSerializer, citasSerializer, horariosSerializer
from .models import usuario, citas, horarios, estados_cita
from .permissions import IsPaciente, IsMedico, IsAdmin

# Registration endpoint
class RegisterView(generics.CreateAPIView):
    queryset = usuario.objects.all()
    serializer_class = usuarioSerializer
    permission_classes = [permissions.AllowAny]

# Login endpoint (SimpleJWT)
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

# Create appointment (cita) – only pacientes can create
class CitaCreateView(generics.CreateAPIView):
    queryset = citas.objects.all()
    serializer_class = citasSerializer
    permission_classes = [IsPaciente]

    def perform_create(self, serializer):
        with transaction.atomic():
            horario_id = self.request.data.get('id_horario')
            horario = horarios.objects.select_for_update().get(id_horario=horario_id)
            if not horario.disponible:
                raise serializers.ValidationError('El horario seleccionado no está disponible')
            # set horario to not available
            horario.disponible = False
            horario.save()
            # set default estado "pendiente"
            estado = estados_cita.objects.get(nombre='pendiente')
            serializer.save(id_estado=estado)

# Cancel appointment – pacientes can cancel, respecting 24h rule
class CitaCancelView(views.APIView):
    permission_classes = [IsPaciente]

    def put(self, request, pk):
        try:
            cita = citas.objects.get(id_cita=pk)
        except citas.DoesNotExist:
            return Response({'detail': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        # check 24h rule
        horario = cita.id_horario
        start_dt = timezone.make_aware(
            datetime.combine(horario.fecha, horario.hora_inicio)
        )
        if timezone.now() > start_dt - timedelta(hours=24):
            return Response({'detail': 'No se puede cancelar la cita con menos de 24 horas de antelación'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            # mark cancelled
            estado_cancelada = estados_cita.objects.get(nombre='cancelada')
            cita.id_estado = estado_cancelada
            cita.cancelada_por = request.user
            cita.fecha_cancelacion = timezone.now()
            cita.save()
            # release horario
            horario.disponible = True
            horario.save()
        return Response({'detail': 'Cita cancelada correctamente'}, status=status.HTTP_200_OK)

# Medico disponibilidad – list free slots
class MedicoDisponibilidadView(generics.ListAPIView):
    serializer_class = horariosSerializer
    permission_classes = [IsMedico]

    def get_queryset(self):
        medico_id = self.kwargs.get('medico_id')
        return horarios.objects.filter(id_medico_id=medico_id, disponible=True)
