from django.views.generic import FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from .models import (
    Service,
    Position,
    Employee,
    Feature,

)
from django.contrib import messages
from .forms import ContactForm

from rest_framework import generics
from .serializers import (
    ServiceSerializer,
    PositionSerializer,
    EmployeeSerializer,
    FeatureSerializer,

)
from rest_framework.generics import get_object_or_404

from rest_framework import viewsets
from rest_framework import mixins

from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import (
    EsuperUserPost,
    EsuperUserPut,
    EsuperUserDelete,
)
from rest_framework import permissions


class IndexView(FormView):
    form_class = ContactForm
    success_url = reverse_lazy('index')
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.order_by('?').all()  # noqa
        context['employees'] = Employee.objects.order_by('?').all()  # noqa
        context['features'] = Feature.objects.order_by('?').all()  # noqa
        return context

    def form_valid(self, form, *args, **kwargs):
        form.send_mail()
        messages.success(self.request, _('Mensagem enviada com sucesso!'))
        return super(IndexView, self).form_valid(form, *args, **kwargs)  # noqa

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, _('Erro ao enviar a mensagem!'))
        return super(IndexView, self).form_invalid(form, *args, **kwargs)  # noqa


# API Versão 1 usando 'generics'


class ServicesAPIView(generics.ListCreateAPIView):
    queryset = Service.objects.all()  # noqa
    serializer_class = ServiceSerializer


class ServiceAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()  # noqa
    serializer_class = ServiceSerializer


class PositionsAPIView(generics.ListCreateAPIView):
    queryset = Position.objects.all()  # noqa
    serializer_class = PositionSerializer


class PositionAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.all()  # noqa
    serializer_class = PositionSerializer


class EmployeesAPIView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()  # noqa
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        if self.kwargs.get('position_pk'):
            return self.queryset.filter(position_id=self.kwargs.get('position_pk'))
        return self.queryset.all()


class EmployeeAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()  # noqa
    serializer_class = EmployeeSerializer

    def get_object(self):
        if self.kwargs.get('position_pk'):
            return get_object_or_404(self.get_queryset(), position_id=self.kwargs.get('position_pk'),
                                     pk=self.kwargs.get('employee_pk'))
        return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('employee_pk'))


class FeaturesAPIView(generics.ListCreateAPIView):
    queryset = Feature.objects.all()  # noqa
    serializer_class = FeatureSerializer


class FeatureAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feature.objects.all()  # noqa
    serializer_class = FeatureSerializer


# API versão 2 usando 'viewsets'


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()  # noqa
    serializer_class = ServiceSerializer


class PositionViewSet(viewsets.ModelViewSet):
    permission_classes = (
        permissions.DjangoModelPermissions,
        EsuperUserPost,
        EsuperUserPut,
        EsuperUserDelete,
    )
    queryset = Position.objects.all()  # noqa
    serializer_class = PositionSerializer

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):  # noqa
        self.pagination_class.page_size = 1
        employees = Employee.objects.filter(position_id=pk)  # noqa
        page = self.paginate_queryset(employees)

        if page is not None:
            serializer = EmployeeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


# API  versão 2 usando 'mixins'

class EmployeeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Employee.objects.all()  # noqa
    serializer_class = EmployeeSerializer


class FeatureViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Feature.objects.all()  # noqa
    serializer_class = FeatureSerializer
