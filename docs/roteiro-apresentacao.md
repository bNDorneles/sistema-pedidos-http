# Roteiro de Apresentação

Este roteiro pode ser usado para explicar o projeto ao professor de forma rápida e organizada.

## 1. Apresentação inicial

“Meu projeto se chama Mesa Rápida. Ele é uma prova de conceito de um sistema de pedidos para restaurante usando o protocolo HTTP. A ideia é demonstrar uma aplicação cliente-servidor, onde o navegador se comunica com uma API REST desenvolvida em Python com FastAPI.”

## 2. Cenário escolhido

“O cenário representa um restaurante que precisa registrar pedidos e acompanhar o estado deles. O usuário acessa uma página web, consulta o cardápio, cria pedidos e acompanha o fluxo do pedido até a entrega.”

Fluxo dos pedidos:

```text
recebido → preparando → pronto → entregue
```

## 3. Por que HTTP?

“Escolhi HTTP porque o sistema é acessado por navegador e funciona com ações iniciadas pelo usuário. Cada ação gera uma requisição para o servidor e recebe uma resposta. Além disso, o HTTP combina bem com APIs REST, permite usar JSON, códigos de status e documentação automática com Swagger.”

Pontos para citar:

- `GET` consulta dados;
- `POST` cria pedidos;
- `PATCH` atualiza status;
- `DELETE` cancela pedidos;
- `200`, `201`, `204`, `400`, `404` e `422` demonstram respostas diferentes do protocolo.

## 4. Demonstração prática

### Passo 1 — Rodar o projeto

No terminal:

```powershell
cd sistema-pedidos-http
python -m uvicorn app.main:app --reload
```

Depois abrir:

```text
http://127.0.0.1:8000
```

### Passo 2 — Mostrar a interface

Na página web:

1. mostrar o cardápio;
2. escolher alguns produtos;
3. criar um pedido;
4. mostrar o pedido aparecendo na lista;
5. avançar o status do pedido;
6. cancelar ou entregar o pedido.

### Passo 3 — Mostrar o Swagger

Abrir:

```text
http://127.0.0.1:8000/docs
```

Explicar que o Swagger é gerado automaticamente pela FastAPI e permite testar os endpoints HTTP.

Sugestão de teste no Swagger:

1. executar `GET /api/produtos`;
2. executar `GET /api/pedidos`;
3. executar `POST /api/pedidos`;
4. executar `PATCH /api/pedidos/{id}/status`.

## 5. Comparação com outros protocolos

Resumo para falar:

“MQTT seria melhor para sensores publicando dados continuamente, como temperatura. CoAP seria melhor para IoT com dispositivos muito limitados. AMQP seria melhor para filas corporativas com alta confiabilidade. MCP seria melhor para integração com agentes de IA. Neste caso, como é uma aplicação web tradicional com navegador e API REST, HTTP é a escolha mais adequada.”

## 6. Testes

Para mostrar que o sistema funciona:

```powershell
python -m pytest -v
```

Resultado esperado:

```text
20 passed
```

Explicação:

“Os testes verificam criação de pedidos, validação de dados, cálculo de total, fluxo de status, cancelamento, listagem e entrega dos arquivos da interface.”

## 7. Fechamento

“Com esse projeto, foi possível demonstrar a comunicação entre cliente e servidor usando HTTP, a troca de mensagens em JSON, o uso de métodos e códigos HTTP, a documentação da API e a persistência dos dados em banco local.”

## Checklist antes de apresentar

- [ ] Rodar o servidor local.
- [ ] Abrir a interface web.
- [ ] Criar um pedido novo.
- [ ] Avançar status do pedido.
- [ ] Abrir Swagger.
- [ ] Testar pelo menos um endpoint.
- [ ] Rodar os testes com `pytest`.
- [ ] Mostrar o README e o relatório no GitHub.
