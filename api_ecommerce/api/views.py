from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Usuario, Endereco
from django.views import View
from django.http import HttpResponse

# Criar requisições

def example_view(request):
    return HttpResponse("This is the example view!")

