from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from order.views import ProductViewSet, OrderViewSet, OrderItemsViewSet

router = routers.DefaultRouter()
router.register('products', ProductViewSet)
router.register('order', OrderViewSet, basename='order')
router.register('items', OrderItemsViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Default router will handle product, order, and item paths
    path('admin/', admin.site.urls),
    
    path('order/<int:pk>/cancel/', OrderViewSet.as_view({'post': 'cancel'}), name='order_cancel'),
    path('order/<int:pk>/checkout/', OrderViewSet.as_view({'post': 'checkout'}), name='order_checkout'),
    path('order/<int:pk>/status/', OrderViewSet.as_view({'post': 'status'}), name='order_status'),
    
    # These custom paths below are unnecessary if you're using the default viewset behavior:
    # path('order_create/', OrderViewSet.create, name='order_create'),
    # path('order_retrieve/<int:pk>/', OrderViewSet.retrieve, name='order_retrieve'),
    # path('items_create/', OrderItemsViewSet.create, name='items_create'),
]
