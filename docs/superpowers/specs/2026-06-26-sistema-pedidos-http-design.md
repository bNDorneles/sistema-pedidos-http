# Especificação — Sistema de Pedidos de Restaurante com HTTP

## 1. Objetivo

Desenvolver uma prova de conceito completa para demonstrar o uso do protocolo HTTP em um sistema de pedidos de restaurante. A solução permitirá consultar o cardápio, criar pedidos, acompanhar o preparo, atualizar o estado e cancelar pedidos.

O projeto será adequado a uma disciplina de Redes: a interface web facilitará a apresentação, enquanto a API REST e o Swagger permitirão inspecionar métodos, rotas, representações JSON e códigos de estado HTTP.

## 2. Justificativa do cenário

O sistema de pedidos é orientado a ações iniciadas por pessoas e opera naturalmente no modelo requisição–resposta. Ele precisa ser acessível por navegadores, expor recursos identificáveis por URLs e executar operações CRUD. Essas características favorecem HTTP e uma API REST.

HTTP também simplifica a integração entre a página web e o servidor, possui amplo suporte em ferramentas de teste e permite respostas explícitas para sucesso e erro. O tráfego esperado é moderado, os clientes não são dispositivos severamente limitados em energia e não há necessidade de telemetria contínua ou filas duráveis.

## 3. Escopo funcional

### 3.1 Cardápio

- Listar os produtos disponíveis.
- Informar nome, descrição e preço de cada produto.
- Popular automaticamente um cardápio inicial para demonstração.

### 3.2 Pedidos

- Criar um pedido com um ou mais produtos e respectivas quantidades.
- Listar todos os pedidos.
- Consultar um pedido pelo identificador.
- Atualizar o estado de um pedido.
- Cancelar um pedido.
- Calcular o valor total exclusivamente no servidor.

### 3.3 Estados

O fluxo normal será:

`recebido → preparando → pronto → entregue`

Somente a próxima transição do fluxo será aceita. Um pedido entregue não poderá voltar a um estado anterior. O cancelamento será representado pela exclusão do pedido por meio de uma requisição `DELETE`, conforme o escopo didático aprovado.

## 4. Arquitetura

### 4.1 Frontend

Uma página responsiva feita com HTML, CSS e JavaScript puro será servida pela própria aplicação. Ela apresentará:

- cardápio e seleção de quantidades;
- resumo e envio do pedido;
- lista de pedidos cadastrados;
- estado, total e itens de cada pedido;
- controles para avançar o estado ou cancelar.

O JavaScript usará a API `fetch` do navegador para realizar as requisições HTTP e exibirá mensagens claras de sucesso e erro.

### 4.2 Backend

O backend será desenvolvido em Python com FastAPI. A aplicação será dividida em módulos de responsabilidade clara:

- configuração e inicialização;
- modelos e acesso ao banco;
- esquemas de entrada e saída;
- regras de negócio;
- rotas HTTP;
- arquivos estáticos da interface.

O OpenAPI gerado pelo FastAPI ficará disponível pelo Swagger em `/docs`.

### 4.3 Persistência

O SQLite será utilizado por ser um banco relacional real que não exige serviço externo. O SQLAlchemy fará o mapeamento das entidades:

- `Produto`: identificador, nome, descrição e preço;
- `Pedido`: identificador, estado, total e data de criação;
- `ItemPedido`: identificador, pedido, produto, quantidade e preço unitário registrado no momento da compra.

O preço unitário será copiado para o item do pedido, preservando o valor histórico mesmo se o produto for alterado posteriormente.

## 5. Contrato HTTP

| Método | Rota | Finalidade | Resposta principal |
| --- | --- | --- | --- |
| `GET` | `/api/produtos` | Listar o cardápio | `200 OK` |
| `POST` | `/api/pedidos` | Criar um pedido | `201 Created` |
| `GET` | `/api/pedidos` | Listar pedidos | `200 OK` |
| `GET` | `/api/pedidos/{id}` | Consultar um pedido | `200 OK` |
| `PATCH` | `/api/pedidos/{id}/status` | Avançar o estado | `200 OK` |
| `DELETE` | `/api/pedidos/{id}` | Cancelar e excluir o pedido | `204 No Content` |

Os corpos de requisição e resposta usarão JSON. O backend retornará:

- `400 Bad Request` para uma regra de negócio inválida;
- `404 Not Found` para produto ou pedido inexistente;
- `422 Unprocessable Entity` para dados com estrutura ou tipos inválidos;
- `500 Internal Server Error` apenas para falhas inesperadas, sem expor detalhes internos.

## 6. Fluxo de dados

1. O navegador solicita o cardápio com `GET /api/produtos`.
2. O usuário seleciona produtos e quantidades.
3. O navegador envia os itens com `POST /api/pedidos`.
4. O servidor valida os identificadores e quantidades, lê os preços, calcula o total e abre uma transação.
5. O pedido e seus itens são persistidos no SQLite.
6. O servidor responde com `201 Created` e a representação completa do pedido.
7. A interface atualiza a listagem por meio de `GET /api/pedidos`.
8. A cozinha avança o pedido com `PATCH /api/pedidos/{id}/status`.
9. O cancelamento usa `DELETE /api/pedidos/{id}`.

## 7. Validação e tratamento de erros

- Cada pedido deve conter ao menos um item.
- Toda quantidade deve ser um número inteiro maior que zero.
- Todo produto informado deve existir.
- Produtos repetidos na mesma requisição serão consolidados em um único item.
- O cliente não enviará nem determinará preços ou o total.
- Somente transições de estado previstas serão permitidas.
- Operações no banco serão confirmadas apenas depois da validação completa.
- Erros esperados terão resposta JSON legível e código HTTP coerente.

## 8. Estratégia de testes

Os testes automatizados usarão `pytest` e o cliente de testes do FastAPI. Cada teste usará um banco isolado. A cobertura funcional incluirá:

- listagem do cardápio inicial;
- criação válida de pedido;
- cálculo de total no servidor;
- consolidação de produtos repetidos;
- rejeição de quantidade inválida;
- rejeição de produto inexistente;
- listagem e consulta de pedidos;
- transição válida e inválida de estado;
- consulta de pedido inexistente;
- cancelamento e confirmação de remoção.

Também será executado um teste manual completo na página e no Swagger, verificando o carregamento visual, as operações principais e a ausência de erros no console do navegador.

## 9. Documentação e entregáveis

O repositório público deverá conter:

- código-fonte funcional;
- `README.md` com cenário, requisitos, arquitetura e decisões;
- instruções de instalação e execução;
- exemplos de requisições e respostas;
- explicação dos métodos e códigos HTTP utilizados;
- comparação entre HTTP, MQTT, CoAP, AMQP e MCP;
- resultados dos testes;
- capturas de tela da página e do Swagger;
- `requirements.txt`;
- `.gitignore`;
- licença;
- testes automatizados.

O README explicará que HTTP foi preferido por sua compatibilidade nativa com navegadores, seu modelo requisição–resposta e sua adequação a operações CRUD. MQTT será descrito como mais apropriado para publicação e assinatura; CoAP, para dispositivos muito restritos; AMQP, para mensageria empresarial com filas; e MCP, para integração entre modelos de IA e ferramentas.

## 10. Critérios de sucesso

O projeto será considerado concluído quando:

- puder ser instalado e iniciado seguindo somente o README;
- a página permitir executar o fluxo completo sem editar dados manualmente;
- todas as rotas documentadas responderem com os códigos definidos;
- os dados permanecerem após reiniciar a aplicação;
- todos os testes automatizados passarem;
- a comparação técnica justificar HTTP com base nos requisitos do cenário;
- as evidências visuais e os resultados estiverem documentados.

## 11. Fora do escopo

Para manter a prova de conceito objetiva, não serão incluídos autenticação, pagamentos, integração com impressoras, notificações em tempo real, implantação em nuvem, gestão administrativa do cardápio ou múltiplas filiais.
