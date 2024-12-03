

# MICROSERVIÇO ORDER

Esse serviço existe para gerenciar pedidos de clientes. Aqui é possível interagir com produtos, pedidos, itens e status de pedidos. Para gerar pagamentos o serviço deve acessar o microserviço de payment via api.
O serviço utiliza um banco de dados PostgresQL para registro dos dados de Produtos e Pedidos.



### EVIDENCIA COBERTURA DE TESTES

https://drive.google.com/file/d/1zzp_ct2Kc5NnESJ59-zW-XIT2_mhplU8/view?usp=sharing


### LINK SWAGGER

Link para acesso ao swagger dos microserviços (insomnia json) https://drive.google.com/file/d/1JZSNdrp_vZI9XRROEOPhkTlDFBmln1kZ/view?usp=sharing



_______________________________________________________________________

### LINK VIDEO ENTREGA FASE 4

Video:https://drive.google.com/file/d/1siLpfPdR3oZXvNZ2GNOtzjlU-CSyYZwS/view?usp=sharing


**Até 2min: Item 1 do entregavel - Microserviços**
- Explicação de como foram divididos os microserviços bem como visão geral de estrutura e de como eles interagem entre si.

**02:02 a 04:30: Item 2 do entregável -  Testes**
- Mostra os testes e report com coverage. MS Order aplicando BDD utilizando behave, app payment utilizando coverage e admin utilizando coverage + pytest

**04:34 a 08:40 : Item 3 do entregável - Repositório e pipelines**
- Mostra as regras de proteção da branch em cada repo, bem como as pipelines com check nos steps e evidencias de realização e report de testes na pipeline

**08:44 até o final : Mostra os microserviços funcionando e interagindo entre si**, fazendo um fluo completo desde a criação do pedido, geração de qrcode de pagamento, atulização de status de pagamento, atualização do status do pedido e listagem de pedidos. 

_______________________________________________________________________


# Desenho da arquitetura do projeto

Considerando as necessidades da empresa de criar um sistema de gestão de pedido que atenda a alguns requisitos de negócio mínimos, como a criação de usuários, início de criação de pedido com e sem login pelo usuário, adição/exclusao/edição de itens nos pedidos, checkout para pagamento e acompanhamento/atualização de status de pedidos, foi desenhada essa solução utilizando Docker para orquestração de containers e Kubernetes para escalabilidade conforme fluxo de acesso/demanda, contendo:
- um container para banco de dados relacional Postgresql, de forma que é fácil a tabulação, relação e análise de dados históricos de compras e clientes;
- um container com aplicação rodando em Python utilizando django framework

A arquitetura de dados foi desenhada de forma que utilize a linguagem ubíqua adotada no projeto, performe bem as alterações dentro de um pedido separando as informações em itens do pedido. CPF foi definido como objeto de valor por ser aplicável em diferentes contextos. A base de dados é estruturada, assim como a aplicação em três principais domínios: user_auth (contendo dados de cadastro e usuário), orders (contendo dados de pedidos, itens, produtos) e payment (contendo dados de transações)  

Para atender à necessidade de negócios, as requisições podem ser feitas com Bearer ho authorization header para usuários logados ou a nível de sessão utilizando 'session' como query parameter nas urls. Quando um pedido é iniciado sem Bearer, ele será amarrado à session e só é possível interagir com ele utilizando essa session. Em caso de pedidos iniciados com Bearer válido, o pedido fica vinculado ao usuário logado e ainteração com ele só poderá ser feita pelo usuário logado. 

Ao rodar o projeto é criado um super user admin@superburger.com senha:admin . Com esse usuário é possível ver a lista completa de pedidos que possuam status 'pronto', 'em preparação' e 'recebido', ordenados do mais antigo para o mais recente.

Link para acesso ao swagger dos microserviços (insomnia json) https://drive.google.com/file/d/1JZSNdrp_vZI9XRROEOPhkTlDFBmln1kZ/view?usp=sharing

Link do vídeo da entrega fase 4:

Sobre arquitetura hexagonal: No contexto django as views são ports, as serializers são os adapters e as models definem sim alguns padroes de como salvar os dados no banco, mas são questoes, por exemplo, como limpar caracteres speciais de um cpf, nao regras de negocios. Como nas serializers (adapters)são feitas as adaptacoes de formato das dependencias, doi adotada a sugestao das aulas e utilizados use_cases para detalhar casos de uso. Apesar de nomenclaturas distintas e uso de framework, tudo que fiz ali de estrutura de pedidos, produtos, checkout, foi tudo escrito do zero e dentro dos padores, apenas utilizando outros nomes.

## Prerequisites

Before running the project, make sure you have the following installed on your machine:

- Docker (so you can run the project)
- Postgres/Dbeaver/PGAdmin (so you can manage local database if needed (optional))

## Getting Started

To build and run the project locally, follow these steps:

1. Run docker in your local enviroment

2. In your terminal, run the following command:
    ~sudo docker-compose up --build


You can now access the application in your browser at http://localhost:5000

## Prerequisites

- [Docker](https://www.docker.com/get-started)


### For testing
coverage run -m behave
coverage report --include="order/*"
