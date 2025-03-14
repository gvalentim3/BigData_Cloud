from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views import View
from api.serializers import UsuarioSerializer
# Criar requisições
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Usuario, Endereco, Cartao
import json


class UsuarioView(APIView):
    # List all users
    def get(self, request):
        usuarios = Usuario.objects.prefetch_related('cartoes', 'enderecos').all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
"""
class UsuarioView():
    def getAll(self, request):
        products = Usuario.objects.all()
        return render(request, 'products/list.html', {'products': products})

def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'GET':
        data = {
            'username': user.username,
            'email': user.email,
        }
        return JsonResponse(data, )
    elif request.method == 'POST':
        data = json.loads(request.body)
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.save()
        return JsonResponse({'status': 'success'}, status=201)

def address_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'GET':
        addresses = Address.objects.filter(user=user)
        data = [{
            'street': addr.street,
            'city': addr.city,
            'state': addr.state,
            'zip_code': addr.zip_code,
            'country': addr.country,
        } for addr in addresses]
        return JsonResponse(data, safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        address = Address.objects.create(
            user=user,
            street=data['street'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            country=data['country'],
        )
        return JsonResponse({'status': 'success', 'address_id': address.id}, status=201)

def credit_card_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'GET':
        cards = CreditCard.objects.filter(user=user)
        data = [{
            'card_number': card.card_number,
            'expiration_date': card.expiration_date,
            'cvv': card.cvv,
        } for card in cards]
        return JsonResponse(data, safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        card = CreditCard.objects.create(
            user=user,
            card_number=data['card_number'],
            expiration_date=data['expiration_date'],
            cvv=data['cvv'],
        )
        return JsonResponse({'status': 'success', 'card_id': card.id}, status=201)"
"""