import os
import django
import sys

# Verifica se estamos em ambiente de testes e ajusta as configurações
if 'test' in sys.argv:
    # Configura o Django para usar o arquivo de configurações para testes
    os.environ['DJANGO_SETTINGS_MODULE'] = 'superburger.settings'
    # Ajusta o banco de dados para usar SQLite em memória durante os testes
    import django.db.backends.sqlite3  # Para garantir que o SQLite seja carregado corretamente
    django.setup()
else:
    # Caso contrário, usa a configuração padrão
    os.environ['DJANGO_SETTINGS_MODULE'] = 'superburger.settings'
    django.setup()

# Agora, você pode importar os modelos e outras funcionalidades do Django para usá-los nos testes
from order.models import Order, Product

