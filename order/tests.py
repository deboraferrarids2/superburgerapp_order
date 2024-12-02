from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from order.models import Product, Order, OrderItems


class ProductViewSetTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.refresh = RefreshToken.for_user(self.user)
        self.token = str(self.refresh.access_token)

        # Set the URL for testing
        self.product_url = reverse('product-list')  # Adjust to your URL pattern name


    def test_list_products(self):
        """Test listing all products"""
        response = self.client.get(self.product_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Check that two products are listed
        self.assertEqual(response.data[0]['name'], self.product1.name)  # Ensure the correct product is listed
        self.assertEqual(response.data[1]['name'], self.product2.name)

    def test_get_product(self):
        """Test getting a specific product"""
        product_detail_url = reverse('product-detail', args=[self.product1.id])  # Adjust to your URL pattern name
        response = self.client.get(product_detail_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product1.name)  # Ensure correct product details are returned

class OrderViewSetTests(APITestCase):
    def setUp(self):
        # Create user and authenticate
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.refresh = RefreshToken.for_user(self.user)
        self.token = str(self.refresh.access_token)

        # Create products and an order
        self.product = Product.objects.create(name="Burger", amount=10.00)
        self.order = Order.objects.create(user=self.user, status='em aberto')

        # Create order item
        self.order_item = OrderItems.objects.create(order=self.order, product=self.product, quantity=2)

        # Set the URL for testing
        self.order_url = reverse('order-list')  # Adjust to your URL pattern name
        self.order_detail_url = reverse('order-detail', args=[self.order.id])

    def test_create_order(self):
        """Test creating a new order"""
        data = {
            "cpf": "12345678901",
            "status": "em aberto",
        }
        response = self.client.post(self.order_url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)  # Ensure an order is created

    def test_cancel_order(self):
        """Test cancelling an order"""
        cancel_url = reverse('order-cancel', args=[self.order.id])  # Adjust to your URL pattern name
        response = self.client.post(cancel_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.status, 'cancelado')

    def test_checkout_order(self):
        """Test checkout of an order"""
        checkout_url = reverse('order-checkout', args=[self.order.id])  # Adjust to your URL pattern name
        response = self.client.post(checkout_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_status(self):
        """Test updating order status"""
        status_url = reverse('order-status', args=[self.order.id])  # Adjust to your URL pattern name
        data = {"status": "finalizado"}
        response = self.client.post(status_url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.status, "finalizado")


class OrderItemsViewSetTests(APITestCase):
    def setUp(self):
        # Create user and authenticate
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Create products and order
        self.product = Product.objects.create(name="Fries", amount=5.00)
        self.order = Order.objects.create(user=self.user, status="em aberto")
        self.order_item = OrderItems.objects.create(order=self.order, product=self.product, quantity=1)

        # Set URLs for testing
        self.order_item_url = reverse('orderitems-list')  # Adjust to your URL pattern name
        self.order_item_detail_url = reverse('orderitems-detail', args=[self.order_item.id])

    def test_create_order_item(self):
        """Test creating an order item"""
        data = {
            "order": self.order.id,
            "product": self.product.id,
            "quantity": 2,
        }
        response = self.client.post(self.order_item_url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItems.objects.count(), 2)

    def test_delete_order_item(self):
        """Test deleting an order item"""
        response = self.client.delete(self.order_item_detail_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(OrderItems.objects.count(), 0)

    def test_update_order_item(self):
        """Test updating an order item"""
        data = {
            "quantity": 3,
        }
        response = self.client.patch(self.order_item_detail_url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.order_item.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order_item.quantity, 3)


if __name__ == '__main__':
    import unittest
    unittest.main()
