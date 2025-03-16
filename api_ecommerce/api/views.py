from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views import View
from api.serializers import UsuarioSerializer
# Criar requisições
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Usuario, Endereco, CartaoCredito
import json
from rest_framework import status


class UsuarioView(APIView):
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            cpf = serializer.validated_data.get('cpf')

            if Usuario.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Este email já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if Usuario.objects.filter(cpf=cpf).exists():
                return Response(
                    {'error': 'Este CPF já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        if pk:
            try:
                # Se na requisição é enviado um ID de usuário, programa verifica se existe na base de dados e caso exista, retorna os dados do usuário junto dos de cartão e endereço.
                usuario = Usuario.objects.prefetch_related('cartoes', 'enderecos').get(pk=pk)
                serializer = UsuarioSerializer(usuario)
                return Response(serializer.data)
            except Usuario.DoesNotExist:
                return Response(
                    {'error': 'Usuário não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        usuarios = Usuario.objects.prefetch_related('cartoes', 'enderecos').all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            if Usuario.objects.filter(email=email).exclude(pk=pk).exists():
                return Response(
                    {'error': 'Este email já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete a user by ID.
        """
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete the user
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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