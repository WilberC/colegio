from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import TemplateView
from utils.views import MyLoginRequiredMixin
from payments.models import TipoPago
from payments.models import CajaChica
from income.models import obtener_mes
from register.models import PersonalColegio, Tesorero
from payments.forms import TipoPagoForm
from payments.forms import PagoForm
#from datetime import datetime
from django.utils.timezone import now as timezone_now
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from payments.forms import ControlPagosPromotorForm
from payments.models import Pago, calculo_pagos_total
# Create your views here.
from django.views.generic import FormView
import logging
from datetime import date
from django.conf import settings
from utils.middleware import get_current_colegio, get_current_user


logger = logging.getLogger("project")


#################################################
#####          CRUD DE TIPO PAGO            #####
#################################################

class TipoPagoListView(ListView):
    model = TipoPago
    template_name = 'TipoPago/tipopago_list.html'


class TipoPagoDetailView(DetailView):
    template_name = 'TipoPago/tipopago_detail.html'
    model = TipoPago


class TipoPagoCreationView(CreateView):
    model = TipoPago
    form_class = TipoPagoForm
    success_url = reverse_lazy('payments:tipopago_list')
    template_name = 'TipoPago/tipopago_form.html'


class TipoPagoUpdateView(UpdateView):
    model = TipoPago
    form_class = TipoPagoForm
    success_url = reverse_lazy('payments:tipopago_list')
    template_name = 'TipoPago/tipopago_form.html'


class TipoPagoDeleteView(UpdateView):
    model = TipoPago
    form_class = TipoPagoForm
    success_url = reverse_lazy('payments:tipopago_list')
    template_name = 'TipoPago/tipopago_confirm_delete.html'



#########################################################
#   Registrar Pago
#########################################################

class RegistrarPagoCreateView(CreateView):
    model = Pago
    form_class = PagoForm
    success_url = reverse_lazy('payments:registrarpago_create')
    template_name = 'RegistrarPago/registrarpago_form.html'

    def get(self, request, *args, **kwargs):
        try:
            logger.info("Estoy en el Registrar Pago")
            user_now = PersonalColegio.objects.get(personal__user=get_current_user(), colegio_id= get_current_colegio())
            logger.info(user_now)
            rol_tesorero = Tesorero.objects.filter(personalcolegio=user_now)
            logger.info(rol_tesorero.count())
            if (rol_tesorero.count()) > 0:
                logger.info("Tengo los permisos")
                return super(RegistrarPagoCreateView, self).get(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(settings.REDIRECT_PERMISOS)
        except:
            return HttpResponseRedirect(settings.REDIRECT_PERMISOS)

    def form_valid(self, form):
        form.instance.personal = PersonalColegio.objects.get(pagos__proveedor__user=self.request.user)
        form.instance.caja_chica = CajaChica.objects.get(colegio__id_colegio = self.request.session.get('colegio'))
        form.instance.fecha = datetime.today()
        return super(RegistrarPagoCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RegistrarPagoCreateView, self).get_context_data(**kwargs)
        cajachica_actual = CajaChica.objects.get(colegio__id_colegio = self.request.session.get('colegio'))
        saldo = cajachica_actual.saldo
        context['saldo'] = saldo
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        logger.info(form)
        if form.is_valid():
            data_form = form.cleaned_data
            logger.info(data_form)
            cajachica_actual = CajaChica.objects.get(colegio__id_colegio=self.request.session.get('colegio'))
            if (cajachica_actual.saldo - data_form['monto']) > 0:

                pago = self.model(proveedor=data_form['proveedor'],
                                  caja_chica=cajachica_actual,
                                  personal=PersonalColegio.objects.get(personal__cajero__user=self.request.user),
                                  tipo_pago=data_form['tipo_pago'],
                                  descripcion=data_form['descripcion'],
                                  monto=data_form['monto'],
                                  fecha=timezone_now(),
                                  numero_comprobante=data_form['numero_comprobante'])
                pago.save()

                cajachica_actual.saldo = cajachica_actual.saldo - pago.monto
                cajachica_actual.save()

            return HttpResponseRedirect(reverse('payments:registrarpago_create'))
        return HttpResponseRedirect(reverse('payments:registrarpago_create'))


"""
PROMOTOR: PAGOS REALIZADOS POR AÑO, MES Y TIPO DE PAGO
"""
class ControlPagosPromotorView(FormView):

    model = Pago
    template_name = "control_pagos_promotor.html"
    form_class = ControlPagosPromotorForm

    def get_queryset(self):
        return []

    def post(self, request, *args, **kwargs):

        anio = request.POST["anio"]
        logger.debug("El año ingresado es {0}".format(anio))
        tipo_pago = request.POST["tipo_pago"]
        logger.debug("El tipo o estado ingresado es {0}".format(tipo_pago))
        mes = request.POST["mes"]
        logger.debug("El mes ingresado es {0}".format(mes))

        fecha_inicio = date.today()
        fecha_final = date.today()

        pagos_colegio = calculo_pagos_total(anio, tipo_pago, mes)

        num_mes = obtener_mes(mes)

        pagos_colegio_2 = calculo_pagos_total(anio, tipo_pago, "Todos")
        pagos_rango = pagos_colegio_2.filter(fecha__gte=fecha_inicio).filter(fecha__lte=fecha_final)

        anio = int(anio)
        if anio == date.today().year:
            rango_mes = date.today().month
        else:
            rango_mes = 12
        logger.debug("El rango de meses es {0}".format(rango_mes))

        # CALCULO DE MONTO TOTAL DE PAGOS POR MES SEGÚN AÑO ESCOGIDO
        monto_mes_total = []  # Lista de Montos totales por mes
        for mes in range (0, rango_mes):
            pagos_mes = pagos_colegio.filter(fecha__month=mes + 1)
            monto_mes_total.append(0)  # Declara las Montos totales iniciales de un mes como '0'
            for pagos in pagos_mes:
                monto_mes_total[mes] = monto_mes_total[mes] + pagos.monto  # Cálculo de los montos totales del mes
        logger.debug("El monto del año por mes es {0}".format(monto_mes_total))

        # CALCULO DE MONTO TOTAL DE PAGOS POR RANGO
        monto_total_rango = 0  # Lista de Montos totales por mes
        for pagos_1 in pagos_rango:
            monto_total_rango = monto_total_rango + pagos_1.monto  # Cálculo de los montos totales del mes

        logger.debug("El monto total de los pagos para el rango de tiempo es {0}".format(monto_total_rango))

        # CALCULO DE MONTO POR MES PARA UN RANGO
        #mes_inicio = fecha_inicio.month
        #mes_final = fecha_final.month
        mes_inicio = 3
        mes_final = 8
        rango_mes = mes_final - mes_inicio
        monto_rango_mes = []
        for mes in range(0, rango_mes+1):
            monto_rango_mes.append(0)
            pagos_mes = pagos_colegio.filter(fecha__month=mes + mes_inicio)
            for pagos in pagos_mes:
                monto_rango_mes[mes] = monto_rango_mes[mes] + pagos.monto

        logger.debug("El monto de rango por mes es {0}".format(monto_rango_mes))

        mes_labels = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]

        if len(pagos_colegio) != 0:
            return render(request, template_name=self.template_name, context={
                'pagos_colegio': pagos_colegio,
                'monto_mes_total': monto_mes_total,
                'mes_labels': mes_labels,
                'form': ControlPagosPromotorForm,
            })
        else:
            return render(request, template_name=self.template_name,context={
                'pagos_colegio': [],
                'monto_mes_total': [],
                'mes_labels': mes_labels,
                'form': ControlPagosPromotorForm,
            })




from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render


"""
PROMOTOR: PAGOS REALIZADOS POR AÑO, MES Y TIPO DE PAGO (PAGINACIÓN INCLUÍDA)
"""
class ControlPagosDirectorView(FormView):

    model = Pago
    template_name = "list2.html"
    form_class = ControlPagosPromotorForm

    def get_queryset(self):
        return []

    def post(self, request, *args, **kwargs):

        anio = request.POST["anio"]
        logger.debug("El año ingresado es {0}".format(anio))
        tipo_pago = request.POST["tipo_pago"]
        logger.debug("El tipo o estado ingresado es {0}".format(tipo_pago))
        mes = request.POST["mes"]
        logger.debug("El mes ingresado es {0}".format(mes))

        pagos_colegio = calculo_pagos_total(anio, tipo_pago, mes)

        anio = int(anio)
        if anio == date.today().year:
            rango_mes = date.today().month
        else:
            rango_mes = 12
        logger.debug("El rango de meses es {0}".format(rango_mes))

        # CALCULO DE MONTO TOTAL DE PAGOS POR MES SEGÚN AÑO ESCOGIDO
        monto_mes_total = []  # Lista de Montos totales por mes
        for mes in range (0, rango_mes):
            pagos_mes = pagos_colegio.filter(fecha__month=mes + 1)
            monto_mes_total.append(0)  # Declara las Montos totales iniciales de un mes como '0'
            for pagos in pagos_mes:
                monto_mes_total[mes] = monto_mes_total[mes] + pagos.monto  # Cálculo de los montos totales del mes
        logger.debug("El monto del año por mes es {0}".format(monto_mes_total))

        paginator = Paginator(pagos_colegio, 3)  # Show 25 contacts per page

        if pagos_colegio != []:
            page = request.GET.get('page')
            try:
                pagos = paginator.page(page)
            except PageNotAnInteger:
                pagos = paginator.page(1)
            except EmptyPage:
                pagos = paginator.page(paginator.num_pages)

        if len(pagos_colegio) != 0:
            return render(request, template_name=self.template_name, context={
                'pagos_colegio': pagos,
                'monto_mes_total': monto_mes_total,
                'form': ControlPagosPromotorForm,
            })
        else:
            return render(request, template_name=self.template_name, context={
                'pagos_colegio': [],
                'monto_mes_total': [],
                'form': ControlPagosPromotorForm,
            })


from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login
import json

def myajaxview(request):
    if request.method == 'POST':
        if request.is_ajax():
            print("**ajax post**")
            data = request.POST['mydata']
            astr = "<html><b> you sent an ajax post request </b> <br> returned data: %s</html>" % data
            return HttpResponse(astr)
    return render(request)

def myajaxformview(request):
    if request.method == 'POST':
        if request.is_ajax():

            print("**ajax form post**")
            for k, v in request.POST.items():
                print(k, v)

            print("field1 data: %s" % request.POST['field1'])
            print("field2 data: %s" % request.POST['field2'])

            mydata = [{'foo': 1, 'baz': 2}]
            return HttpResponse(json.dumps(mydata), mimetype="application/json")

    return render(request)

def foo(request, template='foo.html'):
    return render(request, template)