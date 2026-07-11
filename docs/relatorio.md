# Relatório do Projeto — Sistema de Pedidos com HTTP

| Identificação | Informação |
| --- | --- |
| Aluno | Bernardo Gomes Dorneles |
| Matrícula | 2410103114 |
| Professor | Silvio Ereno Quincozes |
| Disciplina | Redes |
| Protocolo escolhido | HTTP |
| Projeto | Mesa Rápida — Sistema de Pedidos com HTTP |

## 1. Introdução

Este projeto apresenta uma prova de conceito de uma aplicação distribuída baseada no protocolo HTTP. O sistema simula o funcionamento de pedidos em um restaurante, permitindo que um usuário consulte produtos, crie pedidos, acompanhe o estado de preparo e teste as operações por meio de uma API REST documentada com Swagger.

A proposta foi desenvolvida para demonstrar conceitos importantes de redes, como comunicação cliente-servidor, métodos HTTP, códigos de resposta, troca de dados em JSON, uso de URLs para representar recursos e separação entre interface web, API e banco de dados.

## 2. Cenário escolhido

O cenário escolhido foi um sistema de pedidos para restaurante. Nesse ambiente, atendentes, clientes ou funcionários da cozinha acessam uma aplicação web por meio do navegador. As ações realizadas na tela geram requisições HTTP para o servidor, que processa os dados, aplica regras de negócio, persiste informações em banco SQLite e retorna respostas em JSON.

O fluxo principal do pedido é:

```text
recebido → preparando → pronto → entregue
```

Esse cenário é adequado para HTTP porque a comunicação acontece sob demanda, isto é, quando o usuário executa uma ação: consultar cardápio, enviar pedido, listar pedidos, avançar status ou cancelar um pedido.

## 3. Requisitos de comunicação

| Requisito | Análise no cenário |
| --- | --- |
| Frequência de comunicação | Sob demanda, conforme ações dos usuários |
| Quantidade de dispositivos | Poucos ou médios clientes acessando via navegador |
| Baixa latência | Importante para resposta interativa, mas sem exigência de tempo real rígido |
| Banda | Baixo consumo, pois as mensagens JSON são pequenas |
| Energia | Não há dispositivos restritos por bateria |
| Confiabilidade | Cada requisição recebe resposta clara de sucesso ou erro |
| Escalabilidade | A API não depende de estado de sessão e pode evoluir para outro banco |

## 4. Justificativa da escolha do HTTP

O protocolo HTTP foi escolhido porque combina naturalmente com o cenário de uma aplicação web. O cliente acessa uma página no navegador, a página chama endpoints da API e o servidor responde utilizando JSON e códigos de status padronizados.

No projeto, os métodos HTTP foram usados da seguinte forma:

| Método | Uso no sistema |
| --- | --- |
| `GET` | Consultar produtos e pedidos |
| `POST` | Criar um novo pedido |
| `PATCH` | Atualizar parcialmente o status do pedido |
| `DELETE` | Cancelar/remover um pedido |

Além disso, o HTTP facilita a visualização e validação da aplicação, pois pode ser testado diretamente pelo navegador, pelo Swagger, por ferramentas como curl ou por testes automatizados.

## 5. Funcionamento da prova de conceito

A aplicação possui duas partes principais:

1. Interface web, disponível em `http://127.0.0.1:8000`.
2. API REST, disponível em rotas iniciadas por `/api`.

O usuário pode abrir a interface, selecionar produtos do cardápio, criar pedidos, visualizar um resumo por status, filtrar a lista de pedidos e acompanhar os pedidos cadastrados. A API calcula o total no servidor, valida os dados recebidos e impede transições inválidas de status.

Exemplos de regras implementadas:

- não é permitido criar pedido vazio;
- a quantidade de cada item deve ser positiva;
- o servidor calcula o total, evitando confiar no valor enviado pelo cliente;
- um pedido só pode avançar para a próxima etapa correta;
- produtos inexistentes retornam erro;
- pedidos inexistentes retornam erro.

## 6. Endpoints implementados

| Método | Rota | Função | Código esperado |
| --- | --- | --- | --- |
| `GET` | `/api/produtos` | Listar cardápio | `200 OK` |
| `POST` | `/api/pedidos` | Criar pedido | `201 Created` |
| `GET` | `/api/pedidos` | Listar pedidos | `200 OK` |
| `GET` | `/api/pedidos/resumo` | Resumir pedidos por status | `200 OK` |
| `GET` | `/api/pedidos/{id}` | Consultar pedido específico | `200 OK` |
| `PATCH` | `/api/pedidos/{id}/status` | Avançar status | `200 OK` |
| `DELETE` | `/api/pedidos/{id}` | Cancelar pedido | `204 No Content` |

Também são demonstrados erros HTTP como:

- `400 Bad Request`, para transição de status inválida;
- `404 Not Found`, para produto ou pedido inexistente;
- `422 Unprocessable Entity`, para dados inválidos no corpo da requisição.

## 7. Comparação com os demais protocolos

| Protocolo | Pontos fortes | Limitação para este projeto |
| --- | --- | --- |
| HTTP | Simples para aplicações web, suporte nativo em navegadores, REST, Swagger e códigos de status | Maior overhead que protocolos mais leves |
| MQTT | Excelente para sensores, telemetria e publicação/assinatura | Exigiria broker e não representa CRUD de forma tão direta |
| CoAP | Leve para dispositivos IoT restritos e redes de baixa potência | Menor suporte direto em navegadores comuns |
| AMQP | Forte para filas, mensageria corporativa e entrega robusta | Complexidade maior do que o necessário para um sistema simples |
| MCP | Útil para integração entre modelos de IA e ferramentas externas | Não é voltado para uma aplicação web comum de pedidos |

Assim, HTTP foi a melhor escolha porque o sistema é acessado por navegador, possui operações iniciadas por usuários e trabalha com recursos bem definidos, como produtos e pedidos.

## 8. Tecnologias utilizadas

- Python;
- FastAPI;
- Uvicorn;
- SQLAlchemy;
- SQLite;
- Pydantic;
- pytest;
- HTML, CSS e JavaScript;
- Swagger/OpenAPI.

## 9. Resultados obtidos

A prova de conceito demonstrou:

- comunicação real entre navegador e servidor via HTTP;
- uso de JSON como formato de troca de dados;
- uso adequado dos métodos `GET`, `POST`, `PATCH` e `DELETE`;
- uso de códigos de status HTTP;
- documentação automática da API com Swagger;
- persistência local com SQLite;
- validação de regras no servidor;
- resumo de pedidos por status;
- filtro visual de pedidos no painel web;
- testes automatizados cobrindo os principais fluxos.

O resultado dos testes automatizados da entrega é:

```text
22 passed
```

## 10. Limitações e melhorias futuras

Como o projeto é didático, ele roda localmente e não possui todos os recursos esperados em uma aplicação de produção. Melhorias possíveis:

- usar HTTPS;
- adicionar autenticação e perfis de acesso;
- publicar em nuvem;
- trocar SQLite por PostgreSQL;
- adicionar paginação e filtros;
- registrar logs de auditoria;
- adicionar atualização em tempo real com WebSocket caso a cozinha precise receber pedidos instantaneamente.

## 11. Conclusão

O projeto atende ao objetivo de demonstrar o uso prático de um protocolo de rede em um cenário distribuído. O HTTP se mostrou adequado por permitir comunicação simples, padronizada e facilmente testável entre navegador e servidor.

A implementação evidencia conceitos fundamentais de redes e aplicações web, como requisição e resposta, representação de recursos, códigos de estado, troca de mensagens em JSON e documentação da interface de comunicação.
