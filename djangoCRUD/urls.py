"""
URL configuration for djangoCRUD project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('RegistroIngresoColegio/', views.regGC, name='RegistroIngresoColegio'),
    path('login/', views.login_view, name='login'),
    path('inis/', views.login_view, name='inicioSesion'),
    path('Api/Login/', views.LoginView.as_view(), name='api_login'),
    path('regM/', views.updateAC, name='regM'),
    path('menuPrincipal/', views.menuPrincipal, name='menuPrincipal'),
    path('logIn/', views.login_view, name='login'),
    path('registrarAlumnos/', views.registrar_alumnos, name='registrarAlumnos'),
    path('RegMC/', views.regmc_view, name='RegMC'),  # Nueva ruta para RegMC
    path('RegMA/', views.regma_view, name='RegMA'),  # Nueva ruta para RegMA
    path('RegistroDoc/', views.registro_doc_view, name='RegistroDoc'),  # Asegúrate de que esta línea está presente
    path('RegistroDoc/', views.registro_doc_view, name='registroDoc'),  # Aquí está la URL correcta
    path('', views.home_view, name='home'),  # Nueva ruta para la raíz
    #path('CrearAp/', views.CApoderado, name='CrearAp'),
    path('CrearDo/', views.CDocente, name='CrearDo'),
    path('Api/CrearEs/', views.CEstudiante.as_view(), name='ApiCrearEs'),
    path('CrearEs/', views.CEstudianteView, name='CrearEs'),
    path('LeerEs/', views.REstudiante, name='LeerEs'),
    path('ModificarEs/<str:idestudiante>/', views.UEstudiante, name='ModificarEs'),
    path('EliminarEs/<str:idestudiante>/', views.DEstudiante, name='EliminarEs'),
    #path('AsigDo/', views.AsignarDocente, name='AsigDo'),
    path('reg_notas/', views.reg_notas, name='reg_notas'),
    #path('actualizar_notas/', views.actualizar_notas, name='actualizar_notas'),
    #path('asignar_clase/', views.asignar_clase, name='asignar_clase'),
    path('Api/CrearCurso/',views.CCurso.as_view(), name='ApiCrearCurso'),
    path('CrearCurso/', views.CrearCurso, name='CrearCurso'),
    path('Api/ActualizarNotas/', views.ActualizarNota.as_view(), name='ApiActualizarNotas'),
    path('ActualizarNotas/', views.actualizar_notas, name='ActualizarNotas'),
    path('Api/CrearApoderado/', views.CrearApoderado.as_view(), name='ApiCrearApoderado'),
    path('CrearApoderado/', views.CApoderado, name='CrearApoderado'),
    path('Api/AsignarDocente/', views.ADocente.as_view(), name='ApiAsignarDocente'),
    path('AsignarDocente/', views.AsignarDocente, name='AsignarDocente'),
    path('Api/AsignarClase/', views.AClase.as_view(), name='ApiAsignarClase'),
    path('asignar_clase/', views.asignar_clase, name='AsignarClase'),
    

]