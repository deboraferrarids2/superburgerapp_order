from rest_framework import viewsets
import json
from django.http import JsonResponse
import urllib.request
from urllib.error import URLError, HTTPError
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.contrib.sessions.backends.db import SessionStore
from order.models.orders import OrderItems, Order
from order.serializers.orders import *
from order.use_cases.orders import ListOrdersUseCase, ListOrdersAdminUseCase

import logging

# Set up a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# You can configure a handler if necessary (e.g., FileHandler, StreamHandler)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    # Defina as permissões diretamente para as ações
    permission_classes = [AllowAny]  # Permissão geral para todas as ações

    serializer_action_classes = {
        'create': OrderSerializer,
        'create_item': OrderInlineItemsSerializer,
        'list': OrderInlineItemsSerializer,
        'retrieve': OrderInlineItemsSerializer,
        'update': OrderSerializer,
    }


    def create(self, request, *args, **kwargs):
        user = request.user
        session = request.session if user.is_authenticated else SessionStore()
        session.create()
        session_token = session.session_key
        user = user if user.is_authenticated else None

        # Create a mutable copy of the request data
        mutable_data = request.data.copy()
        mutable_data['cpf'] = str(mutable_data.get('cpf'))
        
        serializer = OrderSerializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(session_token=session_token, user=user)

        cart_serializer = OrderInlineItemsSerializer(instance)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='cancel', permission_classes=[AllowAny])
    def cancel(self, request, pk=None):
        print(f'entrou cancel')  
        user = request.user
        if user.is_authenticated:
            user_id=user.id
            try:
                order = Order.objects.get(pk=pk, user=user_id)
            except Order.DoesNotExist:
                raise NotFound("Order not found for the given user.")
        else:
            try:
                order = Order.objects.get(pk=pk, session_token=request.query_params.get('session'))
            except Order.DoesNotExist:
                raise NotFound("Order not found for the given user.")
        print(order)
        if order.status == 'em aberto':
            order.status = 'cancelado'
            order.save()
            return Response({'message': 'Order status updated to "cancelado".'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Esse pedido não pode ser finalizado.'}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=True, methods=['post'], url_path='checkout', permission_classes=[AllowAny])
    def checkout(self, request, pk=None):
        # Get the order object
        order = get_object_or_404(Order, pk=pk)
       
        # Calculate total amount for the order
        total_amount = sum(item.product.amount * item.quantity for item in OrderItems.objects.filter(order=order))
        print(f"Total amount for order {order.id}: {total_amount}")

        # Payment data that needs to be sent to the payment microservice
        payment_data = {
            'order': order.id,
            'transaction_amount': total_amount,
        }

        # Payment service URL (ensure this is correct for your microservice)
        url = 'http://payment-app:7000/transactions/'
        print(f"Sending payment data to URL: {url} with data: {payment_data}")
        
        try:
            # Convert payment data to JSON
            json_data = json.dumps(payment_data).encode('utf-8')
            print( f'print 1')
            # Prepare the request
            req = urllib.request.Request(
                url, 
                data=json_data, 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            print( f'print 2')
            # Send the request and capture the response
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                logger.debug(f"Response received: {response_data}")
                
                # Check if the payment was successful (200 OK)
                if response.status == 200:
                    response_json = json.loads(response_data)
                    # Return the response data if successful
                    return Response(response_json, status=200)
                else:
                    # Handle failure, such as a non-200 status code from the payment service
                    logger.error(f"Payment failed with status: {response.status}")
                    return Response({'error': 'Falha no pagamento'}, status=400)

        except HTTPError as e:
            # Handle HTTP errors (e.g., 4xx or 5xx)
            logger.error(f"HTTPError occurred: {e.code}, {e.reason}")
            return Response({'error': f'HTTPError: {e.code}'}, status=500)
        except URLError as e:
            # Handle URL errors (e.g., network issues)
            logger.error(f"URLError occurred: {e.reason}")
            return Response({'error': f'URLError: {e.reason}'}, status=500)
        except Exception as e:
            # Handle other unforeseen exceptions
            logger.error(f"Unexpected error: {str(e)}")
            return Response({'error': f'Erro desconhecido: {str(e)}'}, status=500)


        
    def get_queryset(self, request):
        use_case = ListOrdersUseCase()
        return use_case.execute(self.request)
    
    def list(self, request, *args, **kwargs):
        use_case = ListOrdersUseCase()
        orders = use_case.execute(request)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            user_id=user.id
            try:
                order = Order.objects.get(pk=pk, user=user_id)
            except Order.DoesNotExist:
                raise NotFound("Order not found for the given user.")
        else:
            order = get_object_or_404(Order, pk=pk, session_token=request.query_params.get('session'))
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        user = request.user
        instance = get_object_or_404(Order, pk=pk, user=user.id) if user.is_authenticated else get_object_or_404(Order, pk=pk, session_token=request.query_params.get('session'))
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='status', permission_classes=[AllowAny])
    def status(self, request, pk=None):
        try:
            data = json.loads(request.body)
            order = Order.objects.get(id=pk)
            order.status = data['status']
            order.save()
            return JsonResponse({"message": "Order status updated successfully"}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderInlineItemsSerializer
        return super().get_serializer_class()
    

class OrderItemsViewSet(viewsets.ModelViewSet):
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemsSerializer    

    permission_classes=[AllowAny]

    serializer_action_classes = {
        'create': OrderItemsWriteSerializer,
        'create_item': OrderItemsSerializer,
        'list': OrderInlineItemsSerializer,
        'retrieve': OrderItemsSerializer,
        'update': OrderItemsSerializer,

    }

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        print(f' data {request.data}')
        serializer.is_valid(raise_exception=True)
        print(f'validated data {serializer.validated_data}')
        order = serializer.validated_data['order']
        order_id = order.id
        user = request.user
        if user.is_authenticated:
            user_id=user.id
            try:
                print(user)
                print(order_id)
                order = Order.objects.get(id=order_id, user=user_id)
            except Order.DoesNotExist:
                return Response({'error': 'Você não tem permissão para editar esse carrinho'}, status=403)
        else:
            session = self.request.query_params.get('session')
            try:
                order = Order.objects.get(id=order_id, session_token=session)
            except Order.DoesNotExist:
                return Response({'error': 'Você não tem permissão para editar esse carrinho'}, status=403)

        instance = serializer.save(order=order)
        return Response(serializer.data, status=201)


    def delete(self, request, pk=None):
        order_item = self.get_object()
        order = order_item.order
        user = request.user

        if user.is_authenticated:
            if order.user != user:
                return Response({'error': 'Você não tem permissão para editar esse carrinho'}, status=403)
        else:
            session = request.query_params.get('session')
            if order.session_token != session:
                return Response({'error': 'Você não tem permissão para editar esse carrinho'}, status=403)

        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        user = request.user

        if user.is_authenticated:
            if order.user != user:
                return Response({'error': 'Você não tem permissão para visualizar esse carrinho'}, status=403)
        else:
            session = request.query_params.get('session')
            if order.session_token != session:
                return Response({'error': 'Você não tem permissão para visualizar esse carrinho'}, status=403)

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        instance = self.get_object()
        order = instance.order
        user = request.user

        if user.is_authenticated:
            if order.user != user:
                return Response({'error': 'Você não tem permissão para editar esse carrinho'}, status=403)
        else:
            session = request.query_params.get('session')
            if order.session_token != session:
                return Response({'error': 'Você não tem permissão para editar esse carrinho'}, status=403)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    

class OrderAdminViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderInlineItemsSerializer
    
    # Defina as permissões diretamente para as ações
    permission_classes = [AllowAny]  # Permissão geral para todas as ações

    serializer_action_classes = {
        'list': OrderInlineItemsSerializer,
    }
    
    def list(self, request, *args, **kwargs):
        use_case = ListOrdersAdminUseCase()
        orders = use_case.execute(request)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        return super().get_serializer_class()