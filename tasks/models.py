from django.db import models

# Create your models here.
class Apoderado(models.Model):
    idapoderado = models.CharField(db_column='IdApoderado', primary_key=True, max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    nombres = models.CharField(db_column='Nombres', max_length=60, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    apellidos = models.CharField(db_column='Apellidos', max_length=60, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    fechanacimiento = models.DateField(db_column='FechaNacimiento')  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=8, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    numerocelular = models.CharField(db_column='NumeroCelular', max_length=9, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Apoderado'


class Asistenciacolegio(models.Model):
    idasistencia = models.ForeignKey('Diario', models.DO_NOTHING, db_column='IdAsistencia')  # Field name made lowercase.
    idestudiante = models.ForeignKey('Estudiante', models.DO_NOTHING, db_column='IdEstudiante')  # Field name made lowercase.
    asistencia = models.IntegerField(db_column='Asistencia', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AsistenciaColegio'
        constraints = [
            models.UniqueConstraint(fields=['idasistencia', 'idestudiante'], name='unique_asistencia_estudiante')
        ]


class Asistenciacurso(models.Model):
    idhora = models.ForeignKey('Hora', models.DO_NOTHING, db_column='IdHora')  # Field name made lowercase.
    idestudiante = models.ForeignKey('Estudiante', models.DO_NOTHING, db_column='IdEstudiante')  # Field name made lowercase.
    asistencia = models.IntegerField(db_column='Asistencia', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AsistenciaCurso'

    
class Clase(models.Model):
    idclase = models.CharField(db_column='IdClase', primary_key=True, max_length=5, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idcurso = models.ForeignKey('Curso', models.DO_NOTHING, db_column='IdCurso')  # Field name made lowercase.
    idseccion = models.ForeignKey('Seccion', models.DO_NOTHING, db_column='IdSeccion')  # Field name made lowercase.
    iddocente = models.ForeignKey('Docente', models.DO_NOTHING, db_column='IdDocente')  # Field name made lowercase.
    auxiliar = models.CharField(db_column='Auxiliar', max_length=10, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Clase'

class Curso(models.Model):
    idcurso = models.CharField(db_column='IdCurso', primary_key=True, max_length=5, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=40, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Curso'


class Diario(models.Model):
    idasistencia = models.CharField(db_column='IdAsistencia', primary_key=True, max_length=8, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    dia = models.DateField(db_column='Dia')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Diario'


class Docente(models.Model):
    iddocente = models.CharField(db_column='IdDocente', primary_key=True, max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    nombres = models.CharField(db_column='Nombres', max_length=60, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    apellidos = models.CharField(db_column='Apellidos', max_length=60, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    fechanacimiento = models.DateField(db_column='FechaNacimiento')  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=8, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    numerocelular = models.CharField(db_column='NumeroCelular', max_length=9, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Docente'
    def __str__(self):
        return self.iddocente
    

class Estudiante(models.Model):
    idestudiante = models.CharField(db_column='IdEstudiante', primary_key=True, max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    nombres = models.CharField(db_column='Nombres', max_length=60, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    apellidos = models.CharField(db_column='Apellidos', max_length=60, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    fechanacimiento = models.DateField(db_column='FechaNacimiento')  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=8, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    anioescolar = models.IntegerField(db_column='AnioEscolar')  # Field name made lowercase.
    imagen = models.BinaryField(db_column='Imagen')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Estudiante'


class Hora(models.Model):
    idhora = models.CharField(db_column='IdHora', primary_key=True, max_length=14, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idclase = models.ForeignKey(Clase, models.DO_NOTHING, db_column='IdClase')  # Field name made lowercase.
    diahorai = models.DateTimeField(db_column='DiaHoraI')  # Field name made lowercase.
    diahoraf = models.DateTimeField(db_column='DiaHoraF')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Hora'


class Lista(models.Model):
    idestudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='IdEstudiante')  # Field name made lowercase.
    idseccion = models.ForeignKey('Seccion', models.DO_NOTHING, db_column='IdSeccion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Lista'


class Notas(models.Model):
    idclase = models.ForeignKey(Clase, models.DO_NOTHING, db_column='IdClase')  # Field name made lowercase.
    idestudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='IdEstudiante')  # Field name made lowercase.
    tiponota = models.CharField(db_column='TipoNota', max_length=10, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    nota = models.IntegerField(db_column='Nota', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Notas'


class Relacion(models.Model):
    idestudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='IdEstudiante')  # Field name made lowercase.
    idapoderado = models.ForeignKey(Apoderado, models.DO_NOTHING, db_column='IdApoderado')  # Field name made lowercase.
    relacion = models.CharField(db_column='Relacion', max_length=30, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Relacion'


class Seccion(models.Model):
    idseccion = models.IntegerField(db_column='IdSeccion', primary_key=True)  # Field name made lowercase.
    designacion = models.CharField(db_column='Designacion', max_length=30, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Seccion'
    

class Usuario(models.Model):
    idusuario = models.IntegerField(db_column='IdUsuario', primary_key=True)  # Field name made lowercase.
    nomusuario = models.CharField(db_column='NomUsuario', max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    contrasenia = models.CharField(db_column='Contrasenia', max_length=30, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    tipousuario = models.IntegerField(db_column='TipoUsuario')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Usuario'
    def __str__(self):
        return self.nomusuario