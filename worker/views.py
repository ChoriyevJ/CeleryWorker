from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from rest_framework import generics
from .models import Flat
from .serializers import FlatSerializer
from . import tasks


def index(request: HttpRequest):
    tasks.task_1.delay()
    return HttpResponse("Hello world")


class FlatAPIView(generics.ListAPIView):
    tasks.get_data_from_olx_v1.delay()
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
