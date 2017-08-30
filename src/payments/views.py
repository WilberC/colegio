from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import TemplateView
from utils.views import MyLoginRequiredMixin
from payments.models import TipoPago
from payments.models import CajaChica
from payments.models import Pago
from register.models import PersonalColegio
from payments.forms import TipoPagoForm
from payments.forms import PagoForm
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

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
    success_url = reverse_lazy('payments:cashier_list')
    template_name = 'TipoPago/tipopago_form.html'


class TipoPagoUpdateView(UpdateView):
    model = TipoPago
    form_class = TipoPagoForm
    success_url = reverse_lazy('payments:cashier_list')
    template_name = 'TipoPago/tipopago_form.html'


class TipoPagoDeleteView(UpdateView):
    model = TipoPago
    form_class = TipoPagoForm
    success_url = reverse_lazy('payments:cashier_list')
    template_name = 'TipoPago/tipopago_list.html'



#########################################################
#   Registrar Pago
#########################################################

class RegistrarPagoCreateView(CreateView):
    model = Pago
    form_class = PagoForm
    success_url = reverse_lazy('payments:registrarpago_create')
    template_name = 'RegistrarPago/registrarpago_form.html'

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

        if form.is_valid():
            data_form = form.cleaned_data
            cajachica_actual = CajaChica.objects.get(colegio__id_colegio=self.request.session.get('colegio'))
            if (cajachica_actual.saldo - data_form['monto']) > 0:

                pago = self.model(proveedor=data_form['proveedor'],
                                  caja_chica=data_form['caja_chica'],
                                  personal=data_form['personal'],
                                  tipo_pago=data_form['tipo_pago'],
                                  descripcion=data_form['descripcion'],
                                  monto=data_form['monto'],
                                  fecha=data_form['fecha'],
                                  numero_comprobante=data_form['numero_comprobante'])
                pago.save()

                cajachica_actual.saldo = cajachica_actual.saldo - pago.monto
                cajachica_actual.save()

            return HttpResponseRedirect(reverse('payments:registrarpago_create'))
        return HttpResponseRedirect(reverse('payments:registrarpago_create'))

