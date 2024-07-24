import datetime
import logging
import re
from venv import logger
from django.shortcuts import render, redirect, get_object_or_404
import pytz

from .models import *
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import User
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import connection
from django.utils import timezone


from django.shortcuts import redirect, render
from django.db import connection
from django.core import serializers

import pyodbc
import requests

from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

# Create your views here.

URL='http://localhost:8000/'

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            nomusuario = serializer.validated_data['nomusuario']
            contrasenia = serializer.validated_data['contrasenia']
            
            try:
                user = Usuario.objects.get(nomusuario=nomusuario, contrasenia=contrasenia)
                # Aquí puedes definir la lógica de redirección
                redirect_url = self.get_redirect_url(user.tipousuario)
                return Response({
                    'status': 'success',
                    'redirect_url': redirect_url
                }, status=status.HTTP_200_OK)
            except Usuario.DoesNotExist:
                return Response({'error': 'Nombre de usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_redirect_url(self, tipo_usuario):
        if tipo_usuario == 1:
            return '/menuPrincipal/'
        elif tipo_usuario == 2:
            return '/RegistroIngresoColegio/'
        return '/login/'

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            nomusuario = form.cleaned_data['nomusuario']
            contrasenia = form.cleaned_data['contrasenia']
            
            data = {
                'nomusuario': nomusuario,
                'contrasenia': contrasenia
            }
            
            api_url = 'http://localhost:8000/Api/Login/'
            try:
                response = requests.post(api_url, json=data)
                response.raise_for_status()
                data = response.json()
                
                if data.get('status') == 'success':
                    redirect_url = data.get('redirect_url')
                    # Guardar datos de sesión si es necesario
                    request.session['user_id'] = nomusuario  # O el ID del usuario
                    return redirect(redirect_url)  # Redirigir a la URL proporcionada
                else:
                    return render(request, 'logIn.html', {
                        'form': form,
                        'error_message': data.get('error', 'Error desconocido')
                    })
            except requests.exceptions.HTTPError as http_err:
                return render(request, 'logIn.html', {
                    'form': form,
                    'error_message': f"HTTP error occurred: {http_err}"
                })
            except requests.exceptions.RequestException as err:
                return render(request, 'logIn.html', {
                    'form': form,
                    'error_message': f"Other error occurred: {err}"
                })
    
    else:
        form = LoginForm()
        
    return render(request, 'logIn.html', {'form': form})
def regGC(request):
    cursor=connection.cursor()
    sql = 'SELECT ac.IdAsistencia, ac.IdEstudiante, ac.Asistencia, e.Nombres, e.Apellidos FROM AsistenciaColegio ac INNER JOIN Estudiante e ON ac.IdEstudiante = e.IdEstudiante INNER JOIN Diario d ON d.IdAsistencia = ac.IdAsistencia WHERE Dia = CONVERT(DATE, GETDATE())'
    try:
        cursor.execute(sql)
        lis = dictfetchall(cursor)
    except:
        pass

    #Lógica de registro pendiente, carga inicial completa
    if request.method=='POST':
        sql="UPDATE AsistenciaColegio SET Asistencia={} WHERE IdAsistencia='{}' AND IdEstudiante='{}'"
        asi = request.POST.get('')

    cursor.close()

    context={
        'asistencia':lis
    }
    return render(request, 'RegGC.html', context)

def registro_doc_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Usuario.objects.get(idusuario=user_id)
            context = {
                'nombre_docente': user.nomusuario,
                'codigo_docente': user.idusuario,
            }
        except Usuario.DoesNotExist:
            context = {
                'nombre_docente': 'Desconocido',
                'codigo_docente': 'Desconocido',
            }
    else:
        return redirect('login')

    return render(request, 'RegistroDoc.html', context)

def menuPrincipal(request):
    # Obtener el ID de usuario de la sesión
    user_id = request.session.get('user_id')
    
    # Obtener los datos del usuario desde la base de datos
    try:
        user = Usuario.objects.get(idusuario=user_id)
        docente = Docente.objects.get(iddocente=user.nomusuario)
    except Usuario.DoesNotExist:
        return redirect('login')  # Redirigir a la página de inicio de sesión si el usuario no existe
    except Docente.DoesNotExist:
        return redirect('login')  # Redirigir a la página de inicio de sesión si el usuario no existe
    val = getattr(docente, 'iddocente') # Obtener valores de texto de la celda específica
    sql = "SELECT * FROM Clase WHERE IdDocente='{}'".format(val)
    cursos = Clase.objects.raw(sql)
    # obtener clase actual
    sql = "DECLARE @Id VARCHAR(14), @doc VARCHAR(10) SELECT @doc='{}' SELECT @Id=IdHora FROM Hora h INNER JOIN Clase cl ON h.IdClase = cl.IdClase WHERE IdDocente=@doc AND DiaHoraI<CURRENT_TIMESTAMP AND DiaHoraF>CURRENT_TIMESTAMP SELECT IdHora, h.IdClase, DiaHoraI, DiaHoraF, cu.Nombre AS Curso, Designacion AS Seccion, (SELECT COUNT(Asistencia) FROM AsistenciaCurso WHERE Asistencia=1 AND IdHora=@Id) AS Asistentes, (SELECT COUNT(Asistencia) FROM AsistenciaCurso WHERE IdHora=@Id) AS Total FROM Hora h INNER JOIN Clase cl ON h.IdClase = cl.IdClase INNER JOIN Curso cu ON cl.IdCurso = cu.IdCurso INNER JOIN Seccion s ON cl.IdSeccion = s.IdSeccion WHERE IdDocente=@doc AND DiaHoraI<CURRENT_TIMESTAMP AND DiaHoraF>CURRENT_TIMESTAMP"
    sql = sql.format(val)
    #print(sql)
    cursor=connection.cursor()
    cursor.execute(sql)
    act=dictfetchall(cursor)
    #print(act)
    cursor.close()
    # Pasar los datos del usuario a la plantilla
    context = {
        'codigo_docente': user.nomusuario,
        'nombre_docente': docente.nombres + " " + docente.apellidos,
        'cursos': cursos,
        'act': act,
    }
    
    return render(request, 'RegistroDoc.html', context)

def home_view(request):
    return redirect('login')

def main(request):
    return render(request, 'RegistroDoc.html')

def iniS(request):
    if request.method == "GET":
        print("here")
        return render(request, 'logIn.html')
    else:
        print(request.method)
        return render(request, 'menuPrincipal')
    
def registrar_alumnos(request):
    return render(request, 'RegMC.html')

def encontrarVarMenu (request):
    user_id = request.session.get('user_id')
    try:
        user = Usuario.objects.get(idusuario=user_id)
        docente = Docente.objects.get(iddocente=user.nomusuario)
    except Usuario.DoesNotExist:
        return redirect('login')  # Redirigir a la página de inicio de sesión si el usuario no existe
    val = getattr(docente, 'iddocente')
    sql = "SELECT * FROM Clase WHERE IdDocente='"+ val +"'"
    cursos = Clase.objects.raw(sql)
    return cursos

# recordar eliminar hora extralarga cuando se arregle
def regmc_view(request):
    # Tu lógica para la vista RegMC
    if request.method == "POST":
        f=request.POST['idclase']

        sql = "SELECT * FROM Hora WHERE IdClase='{}' AND DiaHoraI<CURRENT_TIMESTAMP AND DiaHoraF>CURRENT_TIMESTAMP"
        sql=sql.format(f)
        print(sql)
        hora = Hora.objects.raw(sql)
        g = getattr(hora[0], 'idhora')
        #print("==========================")
        sql = "SELECT IdHora, ac.IdEstudiante, Asistencia, Apellidos, Nombres FROM AsistenciaCurso ac INNER JOIN Estudiante e ON ac.IdEstudiante = e.IdEstudiante WHERE IdHora='{}' ORDER BY Apellidos, Nombres"
        sql = sql.format(g)
        #print(g)
        #print(sql)
        cursor=connection.cursor()
        cursor.execute(sql)

        asistencia=dictfetchall(cursor)
        #print(asistencia)
        clase = Clase.objects.get(idclase=f)
        docente = Docente.objects.get(iddocente=clase.iddocente)

    context = {
        'data': clase,
        'nomd': docente.nombres + " " + docente.apellidos,
        'hora': hora,
        'asistencia': asistencia,
    }
    cursor.close()
    return render(request, 'RegMC.html', context,)

def updateAC(request):
    sql="UPDATE AsistenciaCurso SET Asistencia={} WHERE IdHora='{}' AND IdEstudiante='{}'"
    cursor=connection.cursor()
    hora=request.POST['hora']
    x=True
    i=0
    #if(request.method=="POST"):
    #    try:
    #        v="cod[{}]".format(i)
    #        var=request.POST[v]
    #        print(var)
    #    except:
    #        print("error")

    while x:
        try:
            cod="cod[{}]".format(i)
            asis="ind[{}]".format(i)
            if asis in request.POST:
                var=1
            else:
                var=0
            lis=request.POST[cod]
            s=sql.format(var,hora,lis)
            cursor.execute(s)
        except:
            print("error")
            x=False
        i=i+1
    cursor.close()
    return redirect('menuPrincipal')

def regma_view(request):
    # Tu lógica para la vista RegMA
    return render(request, 'RegMA.html')

class CrearApoderado(APIView):
    def post(self, request):
        serializer = ApoderadoSerializer(data=request.data)
        if serializer.is_valid():
            nom = serializer.validated_data['nombres']
            ape = serializer.validated_data['apellidos']
            fec = serializer.validated_data['fechanacimiento']
            dni = serializer.validated_data['dni']
            tel = serializer.validated_data['numerocelular']
            
            cursor = connection.cursor()
            try:
                sql = "EXEC CrearAp @Nombres=%s, @Apellidos=%s, @FechaNacimiento=%s, @DNI=%s, @NumeroCelular=%s"
                cursor.execute(sql, [nom, ape, fec, dni, tel])
                cursor.close()
                return Response({'status': 'Apoderado creado'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
def CApoderado(request):
    if request.method == 'POST':
        nom = request.POST['Nombres']
        ape = request.POST['Apellidos']
        fec = request.POST['FechaNacimiento']
        dni = request.POST['DNI']
        tel = request.POST['telefono']

        data = {
            'nombres': nom,
            'apellidos': ape,
            'fechanacimiento': fec,
            'dni': dni,
            'numerocelular': tel,
        }

        try:
            url = 'http://localhost:8000/Api/CrearApoderado/'  # URL de la API
            response = requests.post(url, json=data)
            response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
            if response.status_code == 201:
                return redirect('menuPrincipal')  # Redirige a la página principal
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as err:
            print(f"Other error occurred: {err}")

    return render(request, 'crearApoderado.html')

def CDocente(request):
    if request.method == 'POST':
        cursor = connection.cursor()
        try:
            nom = request.POST['Nombres']
            ape = request.POST['Apellidos']
            fec = request.POST['FechaNacimiento']
            dni = request.POST['DNI']
            tel = request.POST['NumeroCelular']
            con = request.POST.get('Contrasenia')
            print(nom, ape, fec, dni, tel)
            sql = "EXEC CrearDocente @Nombres='{}', @Apellidos='{}', @FechaNacimiento='{}', @DNI='{}', @NumeroCelular='{}', @Contrasenia='{}'"
            cursor.execute(sql.format(nom, ape, fec, dni, tel, con))
            cursor.close()
        except:
            print('error')
    return render(request, 'crearDocente.html')


'''
def CEstudiante(request):
    apo=Apoderado.objects.all()
    context={
        'Apo': apo,
    }
    if request.method=='POST':
        cursor=connection.cursor()
        nom=request.POST.get('Nombres')
        ape=request.POST['Apellidos']
        fec=request.POST['FechaNacimiento']
        dni=request.POST['DNI']
        ani=request.POST['Anio']
        fot=request.FILES['Foto']
        apo=request.POST['Apoderado']
        rel=request.POST['Relacion']
        dat=fot.read()
        print(fec)
        sql="EXEC CrearEs @Nombres=%s, @Apellidos=%s, @FechaNacimiento=%s, @DNI=%s, @anio=%s, @foto=%s, @IdApoderado=%s, @Relacion=%s"
        par=(nom, ape, fec, dni, ani, pyodbc.Binary(dat), apo, rel)
        print(sql,par)
        try:
            cursor.execute(sql, par)
        except:
            print()
        #cursor.callproc('CrearEs', [nom, ape, fec, dni, ani, dat, apo, rel])
        #uso de 
        #print(dat)
        cursor.close()
    return render(request, 'crearEstudiante.html', context,)
'''

def REstudiante(request):
    estudiantes = Estudiante.objects.all()
    context={
        'Lista':estudiantes,
    }
    return render(request, 'leerEstudiante.html', context)

def UEstudiante(request, idestudiante):
    apo=Apoderado.objects.all()
    Es = get_object_or_404(Estudiante, idestudiante=idestudiante)
    if request.method=='POST':
        Es.nombres=request.POST.get('Nombres')
        Es.apellidos=request.POST.get('Apellidos')
        try:
            fec=request.POST.get('FechaNacimiento')
            if fec!='':
                Es.fechanacimiento=fec
        except:
            print('no fecha')
        Es.dni=request.POST.get('DNI')
        Es.anioescolar=request.POST.get('Anio')
        try:
            fot=request.FILES.get('Foto').read()
            Es.imagen=pyodbc.Binary(fot)
        except:
            print('no foto')
        Es.save()
        return redirect('LeerEs')
    context = {
        'Estudiante':Es,
        'Apo':apo
    }
    return render(request, 'modificarEstudiante.html', context)

def DEstudiante(request, idestudiante):
    Es = get_object_or_404(Estudiante, idestudiante=idestudiante)
    Relacion.objects.filter(idestudiante=idestudiante).delete()
    Es.delete()
    return redirect('LeerEs')

class ADocente(APIView):
    def post(self, request):
        serializer = ClaseSerializer(data=request.data)
        if serializer.is_valid():
            idclase = serializer.validated_data.get('idclase')
            idcurso = serializer.validated_data.get('idcurso')
            idseccion = serializer.validated_data.get('idseccion')
            iddocente = serializer.validated_data.get('iddocente')

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO Clase (IdClase, IdCurso, IdSeccion, IdDocente) "
                        "VALUES (%s, %s, %s, %s)",
                        [idclase, idcurso, idseccion, iddocente]
                    )
                return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
def AsignarDocente(request):
    seccion_id = request.GET.get('seccion')
    selected_seccion = None

    seccion_prefijos = {
        '1': 'A',
        '2': 'B',
        '3': 'C',
        '4': 'D',
        '5': 'E',
    }

    if seccion_id:
        selected_seccion = seccion_id
        clases = Clase.objects.filter(idseccion=seccion_id)
    else:
        clases = Clase.objects.all()

    secciones = Seccion.objects.all()
    cursos = Curso.objects.all()
    docentes = Docente.objects.all()

    if request.method == 'POST':
        docente_id = request.POST.get('docente')
        seccion_id = request.POST.get('seccion')
        curso_id = request.POST.get('curso')

        prefijo = seccion_prefijos.get(seccion_id)
        
        if not prefijo:
            return render(request, 'AsignarDocente.html', {
                'secciones': secciones,
                'docentes': docentes,
                'cursos': cursos,
                'clases': clases,
                'selected_seccion': selected_seccion,
                'error_message': 'Sección no válida.'
            })

        ultimo_idclase = Clase.objects.filter(idclase__startswith=prefijo).order_by('-idclase').first()
        if ultimo_idclase:
            ultimo_numero = int(re.search(r'\d+', ultimo_idclase.idclase).group())
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1

        new_idclase = f"{prefijo}{nuevo_numero:04d}"

        data = {
            'idclase': new_idclase,
            'idcurso': curso_id,
            'idseccion': int(seccion_id),  # Convertir a int si es necesario
            'iddocente': docente_id,
        }

        try:
            url_dir = 'http://localhost:8000/Api/AsignarDocente/'
            response = requests.post(url_dir, json=data)
            response.raise_for_status()
            if response.json().get('status') == 'success':
                return redirect('AsignarDocente')
            else:
                error = response.json().get('error', 'Error desconocido')
                return render(request, 'AsignarDocente.html', {
                    'secciones': secciones,
                    'docentes': docentes,
                    'cursos': cursos,
                    'clases': clases,
                    'selected_seccion': selected_seccion,
                    'error_message': error
                })
        except requests.exceptions.HTTPError as http_err:
            return render(request, 'AsignarDocente.html', {
                'secciones': secciones,
                'docentes': docentes,
                'cursos': cursos,
                'clases': clases,
                'selected_seccion': selected_seccion,
                'error_message': f"HTTP error occurred: {http_err}"
            })
        except requests.exceptions.RequestException as err:
            return render(request, 'AsignarDocente.html', {
                'secciones': secciones,
                'docentes': docentes,
                'cursos': cursos,
                'clases': clases,
                'selected_seccion': selected_seccion,
                'error_message': f"Other error occurred: {err}"
            })

    context = {
        'secciones': secciones,
        'docentes': docentes,
        'cursos': cursos,
        'clases': clases,
        'selected_seccion': selected_seccion,
    }

    return render(request, 'AsignarDocente.html', context)
def reg_notas(request):
    if request.method == "POST":
        idclase = request.POST.get('idclase')
        
        # Filtrar notas por IdClase y unir con la tabla de estudiantes para obtener nombres y apellidos
        notas = Notas.objects.filter(idclase=idclase).select_related('idestudiante').values(
            'idclase', 'idestudiante', 'idestudiante__nombres', 'idestudiante__apellidos', 'tiponota', 'nota'
        )
        
        # Obtener información adicional del curso y del docente si es necesario
        clase = Clase.objects.get(idclase=idclase)
        docente = Docente.objects.get(iddocente=clase.iddocente)
        
        context = {
            'notas': notas,
            'data': clase,
            'nomd': docente.nombres + " " + docente.apellidos,
        }

        return render(request, 'RegNotas.html', context)
    
    # Si no es un POST, redirigir o mostrar un mensaje de error
    return redirect('menuPrincipal')


# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CEstudiante(APIView):
    def post(self, request):
        logger.debug("Iniciando POST request para crear estudiante")
        serializer = EstudianteSerializer(data=request.data)
        
        if serializer.is_valid():
            logger.debug("Datos del serializer son válidos")
            nom = serializer.validated_data['nombres']
            ape = serializer.validated_data['apellidos']
            fec = serializer.validated_data['fecha_nacimiento']
            dni = serializer.validated_data['dni']
            ani = serializer.validated_data['anio']
            fot = serializer.validated_data['foto']
            apo = serializer.validated_data['apoderado']
            rel = serializer.validated_data['relacion']
            dat = fot.read()

            sql = "EXEC CrearEs @Nombres=%s, @Apellidos=%s, @FechaNacimiento=%s, @DNI=%s, @anio=%s, @foto=%s, @IdApoderado=%s, @Relacion=%s"
            par = (nom, ape, fec, dni, ani, pyodbc.Binary(dat), apo, rel)

            logger.debug(f"Ejecutando SQL: {sql} con parámetros: {par}")
            
            try:
                cursor = connection.cursor()
                cursor.execute(sql, par)
                cursor.close()
                logger.debug("Estudiante creado exitosamente en la base de datos")
                messages.success(request, 'Estudiante creado exitosamente')  # Mensaje de éxito
                return redirect('CrearEs')  # Redirigir para evitar resubmisión de formulario
            except Exception as e:
                logger.error(f"Error al crear estudiante: {e}")
                messages.error(request, f'Error al crear estudiante: {str(e)}')  # Mensaje de error
                return redirect('CrearEs')
        else:
            logger.debug(f"Datos inválidos: {serializer.errors}")
            messages.error(request, f'Datos inválidos: {serializer.errors}')  # Mensaje de datos inválidos
            return redirect('CrearEs')

    def get(self, request):
        logger.debug("Iniciando GET request para obtener apoderados")
        apo = Apoderado.objects.all()
        apoderados_data = [{'id': x.idapoderado, 'apellidos': x.apellidos, 'nombres': x.nombres, 'dni': x.dni} for x in apo]
        logger.debug(f"Apoderados obtenidos: {apoderados_data}")
        return Response({'Apoderados': apoderados_data})

def CEstudianteView(request):
    api_url = URL + 'Api/CrearEs/'  # Actualiza esto con la URL correcta de tu API interna

    logger.debug(f"Realizando GET request a la API: {api_url}")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        apoderados_data = response.json().get('Apoderados', [])
        logger.debug(f"Datos de apoderados obtenidos: {apoderados_data}")
    else:
        logger.error(f"Error al obtener apoderados: {response.status_code}")
        apoderados_data = []

    context = {
        'Apo': apoderados_data,
    }

    return render(request, 'crearEstudiante.html', context)
def asignar_clase(request):
    if request.method == 'POST':
        id_clase = request.POST['IdClase']
        fecha = request.POST['Fecha']
        hora = request.POST['Hora']
        
        data = {
            'idclase': id_clase,
            'fecha': fecha,
            'hora': hora
        }

        api_url = 'http://localhost:8000/Api/AsignarClase/'
        try:
            response = requests.post(api_url, json=data)
            response.raise_for_status()
            if response.json().get('status') == 'success':
                return redirect('AsignarClase')
            else:
                error = response.json().get('error', 'Error desconocido')
                return render(request, 'AsignarClase.html', {
                    'clases': Clase.objects.all(),
                    'error_message': error
                })
        except requests.exceptions.HTTPError as http_err:
            return render(request, 'AsignarClase.html', {
                'clases': Clase.objects.all(),
                'error_message': f"HTTP error occurred: {http_err}"
            })
        except requests.exceptions.RequestException as err:
            return render(request, 'AsignarClase.html', {
                'clases': Clase.objects.all(),
                'error_message': f"Other error occurred: {err}"
            })

    clases = Clase.objects.all()
    return render(request, 'AsignarClase.html', {'clases': clases})

class AClase(APIView):
    def post(self, request):
        id_clase = request.data.get('idclase')
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')

        # Definir la zona horaria (ajusta según tu necesidad, por ejemplo 'UTC' o 'America/Lima')
        timezone = pytz.timezone('America/Lima')
        
        # Combinar la fecha con la hora seleccionada para crear un objeto datetime
        dia_hora_i_str = f"{fecha} {hora}"
        dia_hora_i = datetime.datetime.strptime(dia_hora_i_str, '%Y-%m-%d %H:%M')
        
        # Asignar la zona horaria
        dia_hora_i = timezone.localize(dia_hora_i)
        
        # Calcular la hora de fin basada en la hora de inicio
        dia_hora_f = dia_hora_i + datetime.timedelta(minutes=45)
        
        # Generar el nuevo IdHora
        date_part = dia_hora_i.strftime('%Y%m%d')
        
        # Obtener la última entrada en la base de datos
        last_entry = Hora.objects.order_by('-idhora').first()
        
        if last_entry:
            # Extraer la parte numérica del último idhora
            last_numeric_part = last_entry.idhora[9:]
            last_id = int(last_numeric_part)
            new_id = last_id + 1
        else:
            new_id = 1

        sequential_part = f"A{new_id:05d}"  # Ajustar para tener solo 5 dígitos
        id_hora = f"{date_part}{sequential_part}"
        
        if len(id_hora) > 14:
            return Response({'error': f"Generated IdHora '{id_hora}' exceeds maximum length of 14 characters."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el objeto Hora
        nueva_hora = Hora(idhora=id_hora, idclase_id=id_clase, diahorai=dia_hora_i, diahoraf=dia_hora_f)
        nueva_hora.save()

        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class ActualizarNota(APIView):
    def post(self, request):
        serializer = NotaSerializer(data=request.data, many=True)
        if serializer.is_valid():
            notas = serializer.validated_data

            for nota in notas:
                idclase = nota.get('idclase')
                idestudiante = nota.get('idestudiante')
                tiponota = nota.get('tiponota')
                nota_valor = nota.get('nota')

                if idclase and idestudiante and tiponota and nota_valor is not None:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE Notas SET Nota = %s WHERE IdClase = %s AND IdEstudiante = %s AND TipoNota = %s",
                                [nota_valor, idclase, idestudiante, tiponota]
                            )
                    except Exception as e:
                        return Response({'error': f"Error al actualizar la nota: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def actualizar_notas(request):
    if request.method == "POST":
        notas_data = []
        for key, value in request.POST.items():
            if key.startswith('notas['):
                index = int(key.split('[')[1].split(']')[0])
                field = key.split('[')[2].split(']')[0]
                while len(notas_data) <= index:
                    notas_data.append({})
                notas_data[index][field] = value

        try:
            url_dir = 'http://localhost:8000/Api/ActualizarNotas/'  # URL actualizada
            response = requests.post(url_dir, json=notas_data)
            response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
            if response.headers.get('content-type') == 'application/json':
                response_data = response.json()
            else:
                response_data = {'status': 'success'}  # Asume éxito si no hay JSON pero no hay error HTTP
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            response_data = {'error': str(http_err)}
        except requests.exceptions.RequestException as err:
            print(f"Other error occurred: {err}")
            response_data = {'error': str(err)}
        except ValueError as json_err:
            print(f"JSON decode error occurred: {json_err}")
            response_data = {'error': 'Respuesta no válida del servidor'}

        if response_data.get('status') == 'success':
            return redirect('menuPrincipal')
        else:
            error = response_data.get('error', 'Error desconocido')
            return render(request, 'RegNotas.html', {'error': error})

    return redirect('RegNotas')

class CCurso(APIView):
    def post(self, request):
        serializer = CursoSerializer(data=request.data)
        if serializer.is_valid():
            nom=serializer.validated_data['nombre']
            cursor = connection.cursor()
            try:
                # Obtener el último ID de curso
                cursor.execute("SELECT MAX(IdCurso) FROM Curso WHERE IdCurso LIKE 'C%'")
                last_id = cursor.fetchone()[0]
                
                # Generar el siguiente ID de curso
                if last_id:
                    next_id_number = int(last_id[1:]) + 1  # Extraer el número y aumentarlo en 1
                    next_id = f"C{next_id_number:03}"  # Formatear el nuevo ID con ceros a la izquierda
                else:
                    next_id = "C001"  # Primer ID si no hay cursos previos

                print(next_id, nom)

                # Insertar el nuevo curso con el ID generado
                cursor.execute("INSERT INTO Curso (IdCurso, Nombre) VALUES (%s, %s)", (next_id, nom))
                cursor.close()
                return Response({'status': 'Estudiante creado'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print('Error:', e)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def CrearCurso(request):
    url_dir=URL+'Api/CrearCurso/'
    if request.method=='POST':
        # Preparar datos para enviar a la API
        nom=request.POST.get('Nombre')
        data={
            'nombre': nom,
        }
        response = requests.post(url_dir, data=data)
        if response.status_code == 201:
            return redirect('login')
    return render(request, 'crearCurso.html')