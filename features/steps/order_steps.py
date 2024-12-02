from behave import given, when, then
import requests
from hamcrest import assert_that, is_, is_not
import logging

# Configure o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"  # Substitua pela URL correta da sua API

@given('I create an order without a user')
def step_impl_create_order(context):
    # Criando um pedido sem um usuário vinculado
    url = f"{BASE_URL}/orders/"
    response = requests.post(url)
    
    # Verificando o código de status e extraindo os dados necessários
    assert_that(response.status_code, is_(201))  # Espera-se o código de status 201 (Created)
    
    response_data = response.json()
    context.order = response_data
    context.order_id = response_data["id"]  # Armazena o ID do pedido
    context.session_token = response_data["session_token"]  # Armazena o session_token
    
    logger.info(f"Order created with ID: {context.order_id} and session_token: {context.session_token}")

@when('I add an item to the order with session token')
def step_impl_add_item(context):
    logger.info("Creating a product manually in the test database...")

    # Criando o produto manualmente
    url = f"{BASE_URL}/products/"
    payload = {
        "name": "Burger",
        "category": "lanche",
        "description": "Hamburger delicioso",
        "amount": 1099,
        "size": "pequeno"
    }
    response = requests.post(url, json=payload)
    
    assert_that(response.status_code, is_(201))
    product_data = response.json()
    context.product_id = product_data["id"]
    
    logger.info(f"Product created with ID: {context.product_id}")

    # Adicionando um item ao pedido
    url = f"{BASE_URL}/items/?session={context.session_token}"
    payload = {
        "order": context.order_id,
        "product": context.product_id,  # Usando o ID do produto criado
        "quantity": 2,
        "changes": ""
    }
    logger.info(f"Adding item to order {context.order_id} with product {context.product_id}")
    logger.info(F'CONTEXT ORDER: {context.order}')
    logger.info(f"Payload: {payload}")
    logger.info(f"url: {url}")
    response = requests.post(url, json=payload)
    logger.info(f'response: {response}')
    
    # Verificando se o item foi adicionado com sucesso
    assert_that(response.status_code, is_(201))  # Espera-se o código de status 201 (Created)
    logger.info(f"Item added to order {context.order_id} with product ID {context.product_id}.")

@when('I attempt to create a payment link for the order')
def step_impl_checkout(context):
    # Tentando gerar o link de pagamento
    url = f"{BASE_URL}/orders/{context.order_id}/checkout/"
    response = requests.post(url)
    
    # Armazena a resposta para validação posterior
    context.payment_response = response
    
    logger.info(f"Payment link generation response: {response.status_code}")

@then('I should receive an order ID and a session token')
def step_impl_order_response(context):
    # Verificando se o ID do pedido e o session_token estão presentes
    assert_that(context.order_id, is_not(None))
    assert_that(context.session_token, is_not(None))

