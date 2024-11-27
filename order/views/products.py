from rest_framework.permissions import AllowAny
from order.models.products import Product
from order.serializers.products import ProductSerializer
from order.use_cases.products import ListProductsUseCase
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response 

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.using('default').all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        # Passando os parâmetros de consulta diretamente para o caso de uso
        list_products_use_case = ListProductsUseCase()
        return list_products_use_case.execute(self.request.query_params)

    def list(self, request, *args, **kwargs):
        # Chama o método get_queryset para obter a lista de produtos
        queryset = self.get_queryset()
        # Serializa e retorna a resposta
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
