"""
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from AE_academico.forms import AulaForm
from AE_academico.forms import CursoDocenteForm
from AE_academico.models import Aula
from AE_academico.models import CursoDocente
from AE_academico.models import Curso
from register.models import Docente, Personal, PersonalColegio
from django.conf import settings
from utils.middleware import validar_roles, get_current_request, get_current_colegio, get_current_user
from django.http import HttpResponseRedirect
from utils.views import MyLoginRequiredMixin


#################################################
#####            CRUD DE AULA               #####
#################################################


class AulaListView(MyLoginRequiredMixin, ListView):
    model = Aula
    template_name = 'aula_list.html'

    def get(self, request, *args, **kwargs):
        roles = ['promotor', 'director', 'administrativo', 'tesorero', 'cajero']
        if validar_roles(roles=roles):
            return super(AulaListView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(settings.REDIRECT_PERMISOS)

    def get_context_data(self, **kwargs):

            context = super(AulaListView, self).get_context_data(**kwargs)

            request = get_current_request()

            if request.session.get('colegio'):
                id = request.session.get('colegio')
                context['idcolegio'] = id
            return context


class AulaDetailView(UpdateView):
    model = Aula
    form_class = AulaForm
    template_name = 'aula_detail.html'

    def get(self, request, *args, **kwargs):
        roles = ['promotor', 'director', 'administrativo', 'tesorero', 'cajero']
        if validar_roles(roles=roles):
            return super(AulaDetailView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(settings.REDIRECT_PERMISOS)


class AulaCreationView(CreateView):
    model = Aula
    form_class = AulaForm
    success_url = reverse_lazy('academic:aula_list')
    template_name = 'aula_form.html'

    def get(self, request, *args, **kwargs):
        roles = ['promotor', 'director', 'administrativo', 'tesorero']
        if validar_roles(roles=roles):
            return super(AulaCreationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(settings.REDIRECT_PERMISOS)


class AulaUpdateView(UpdateView):
    model = Aula
    form_class = AulaForm
    success_url = reverse_lazy('academic:aula_list')
    template_name = 'aula_form.html'


class AulaDeleteView(DeleteView):
    model = Aula
    form_class = AulaForm
    success_url = reverse_lazy('academic:aula_list')
    template_name = 'aula_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        roles = ['promotor', 'director', 'administrativo']
        if validar_roles(roles=roles):
            return super(AulaDeleteView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(settings.REDIRECT_PERMISOS)


#################################################
#####            CRUD DE CURSO DOCENTE      #####
#################################################

class CursoDocenteCreateView(CreateView):
    model = CursoDocente
    form_class = CursoDocenteForm
    success_url = reverse_lazy('academic:aula_list')
    template_name = 'cursodocente_form.html'

    def get(self, request, *args, **kwargs):
        roles = ['promotor', 'director', 'administrativo', 'tesorero']
        if validar_roles(roles=roles):
            personalcolegio = PersonalColegio.objects.filter(colegio_id=get_current_colegio(), activo=True)
            personal = []
            for personalcol in personalcolegio:
                personal.append(personalcol.personal)
            cursos = Curso.objects.filter(aula__tipo_servicio__colegio_id=get_current_colegio(), activo= True)
            docentes = Docente.objects.filter(empleado=personal)
            return render(request, template_name=self.template_name, context={
                'form': self.form_class,
                'docentes': docentes,
                'cursos': cursos,
            })

        else:
            return HttpResponseRedirect(settings.REDIRECT_PERMISOS)

"""