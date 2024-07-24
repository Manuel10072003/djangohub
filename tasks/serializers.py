from rest_framework import serializers

from tasks.models import Hora
#from .models import Curso
#from .models import Estudiante

class EstudianteSerializer(serializers.Serializer):
    nombres = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    fecha_nacimiento = serializers.DateField()
    dni = serializers.CharField(max_length=8)
    anio = serializers.IntegerField()
    foto = serializers.ImageField()
    apoderado = serializers.IntegerField()
    relacion = serializers.CharField(max_length=50)

class CursoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)

class NotaSerializer(serializers.Serializer):
    idclase = serializers.CharField(max_length=5)
    idestudiante = serializers.CharField(max_length=10)
    tiponota = serializers.CharField(max_length=10)
    nota = serializers.IntegerField()

class ApoderadoSerializer(serializers.Serializer):
    nombres = serializers.CharField(max_length=60)
    apellidos = serializers.CharField(max_length=60)
    fechanacimiento = serializers.DateField()
    dni = serializers.CharField(max_length=8)
    numerocelular = serializers.CharField(max_length=9)

class ClaseSerializer(serializers.Serializer):
    idclase = serializers.CharField(max_length=5)
    idcurso = serializers.CharField(max_length=5)
    idseccion = serializers.IntegerField()
    iddocente = serializers.CharField(max_length=10)

class HoraSerializer(serializers.Serializer):
    idhora = serializers.CharField(max_length=14)
    idclase = serializers.CharField(max_length=5)
    diahorai = serializers.DateTimeField()
    diahoraf = serializers.DateTimeField()

class LoginSerializer(serializers.Serializer):
    nomusuario = serializers.CharField(max_length=100)
    contrasenia = serializers.CharField(max_length=100)
    tipo_usuario = serializers.IntegerField()