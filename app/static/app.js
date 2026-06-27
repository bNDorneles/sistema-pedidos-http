const state = {
  products: [],
  cart: new Map(),
  orders: [],
};

const money = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const statusLabels = {
  recebido: "Recebido",
  preparando: "Preparando",
  pronto: "Pronto",
  entregue: "Entregue",
};

const nextStatus = {
  recebido: "preparando",
  preparando: "pronto",
  pronto: "entregue",
};

const byId = (id) => document.getElementById(id);

function element(tag, options = {}) {
  const node = document.createElement(tag);
  if (options.className) node.className = options.className;
  if (options.text !== undefined) node.textContent = options.text;
  if (options.attributes) {
    Object.entries(options.attributes).forEach(([name, value]) => {
      node.setAttribute(name, value);
    });
  }
  return node;
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: options.body ? { "Content-Type": "application/json" } : {},
    ...options,
  });

  if (!response.ok) {
    let message = `Falha HTTP ${response.status}.`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // A resposta pode não ter corpo JSON.
    }
    throw new Error(message);
  }

  return response.status === 204 ? null : response.json();
}

function showToast(message, isError = false) {
  const toast = byId("toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("visible");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("visible"), 4000);
}

function renderMenu() {
  const grid = byId("menu-grid");
  grid.replaceChildren();
  grid.setAttribute("aria-busy", "false");
  byId("menu-count").textContent = `${state.products.length} itens`;

  state.products.forEach((product) => {
    const card = element("article", { className: "menu-card" });
    card.append(
      element("h3", { text: product.nome }),
      element("p", { text: product.descricao }),
    );

    const footer = element("div", { className: "menu-card-footer" });
    footer.append(element("span", {
      className: "price",
      text: money.format(Number(product.preco)),
    }));

    const button = element("button", {
      className: "button primary add-item",
      text: "Adicionar",
      attributes: {
        type: "button",
        "aria-label": `Adicionar ${product.nome} ao pedido`,
      },
    });
    button.addEventListener("click", () => changeQuantity(product.id, 1));
    footer.append(button);
    card.append(footer);
    grid.append(card);
  });
}

function changeQuantity(productId, change) {
  const quantity = (state.cart.get(productId) || 0) + change;
  if (quantity <= 0) state.cart.delete(productId);
  else state.cart.set(productId, quantity);
  renderCart();
}

function renderCart() {
  const container = byId("cart-items");
  container.replaceChildren();

  if (state.cart.size === 0) {
    container.append(element("p", {
      className: "empty-state",
      text: "Selecione um item do cardápio para começar.",
    }));
  } else {
    state.cart.forEach((quantity, productId) => {
      const product = state.products.find((item) => item.id === productId);
      const row = element("div", { className: "cart-row" });
      const description = element("div");
      description.append(
        element("strong", { text: product.nome }),
        element("small", {
          text: money.format(Number(product.preco) * quantity),
        }),
      );

      const controls = element("div", {
        className: "quantity",
        attributes: { "aria-label": `Quantidade de ${product.nome}` },
      });
      const decrease = element("button", {
        text: "−",
        attributes: {
          type: "button",
          "aria-label": `Remover uma unidade de ${product.nome}`,
        },
      });
      decrease.addEventListener("click", () => changeQuantity(productId, -1));
      const increase = element("button", {
        text: "+",
        attributes: {
          type: "button",
          "aria-label": `Adicionar uma unidade de ${product.nome}`,
        },
      });
      increase.addEventListener("click", () => changeQuantity(productId, 1));
      controls.append(decrease, element("span", { text: quantity }), increase);
      row.append(description, controls);
      container.append(row);
    });
  }

  const total = Array.from(state.cart.entries()).reduce((sum, [productId, quantity]) => {
    const product = state.products.find((item) => item.id === productId);
    return sum + Number(product.preco) * quantity;
  }, 0);

  byId("cart-total").textContent = money.format(total);
  byId("submit-order").disabled = state.cart.size === 0;
}

function createOrderCard(order) {
  const card = element("article", { className: "order-card" });
  const meta = element("div", { className: "order-meta" });
  const badge = element("span", {
    className: `status-badge status-${order.status}`,
    text: statusLabels[order.status],
  });
  meta.append(
    badge,
    element("strong", { text: `Pedido #${order.id}` }),
    element("small", {
      text: new Date(order.criado_em).toLocaleString("pt-BR"),
    }),
  );

  const details = element("div");
  const list = element("ul", { className: "order-items" });
  order.itens.forEach((item) => {
    list.append(element("li", {
      text: `${item.quantidade}× ${item.nome_produto} — ${money.format(Number(item.subtotal))}`,
    }));
  });
  details.append(
    list,
    element("div", {
      className: "order-total",
      text: `Total: ${money.format(Number(order.total))}`,
    }),
  );

  const actions = element("div", { className: "order-actions" });
  if (nextStatus[order.status]) {
    const advance = element("button", {
      className: "button primary compact",
      text: `Marcar como ${statusLabels[nextStatus[order.status]].toLowerCase()}`,
      attributes: { type: "button" },
    });
    advance.addEventListener("click", () => updateStatus(order.id, nextStatus[order.status], advance));
    actions.append(advance);
  }

  const remove = element("button", {
    className: "button danger compact",
    text: "Cancelar",
    attributes: { type: "button", "aria-label": `Cancelar pedido ${order.id}` },
  });
  remove.addEventListener("click", () => cancelOrder(order.id, remove));
  actions.append(remove);
  card.append(meta, details, actions);
  return card;
}

function renderOrders() {
  const container = byId("orders-list");
  container.replaceChildren();
  container.setAttribute("aria-busy", "false");

  if (state.orders.length === 0) {
    container.append(element("p", {
      className: "empty-state",
      text: "Ainda não há pedidos. Monte o primeiro no cardápio acima.",
    }));
    return;
  }

  state.orders.forEach((order) => container.append(createOrderCard(order)));
}

async function loadProducts() {
  try {
    state.products = await request("/api/produtos");
    renderMenu();
  } catch (error) {
    byId("menu-grid").replaceChildren(element("p", {
      className: "empty-state",
      text: "Não foi possível carregar o cardápio. Recarregue a página.",
    }));
    showToast(error.message, true);
  }
}

async function loadOrders() {
  const button = byId("refresh-orders");
  button.disabled = true;
  try {
    state.orders = await request("/api/pedidos");
    renderOrders();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
  }
}

async function submitOrder() {
  const button = byId("submit-order");
  button.disabled = true;
  button.textContent = "Enviando…";
  try {
    const itens = Array.from(state.cart.entries()).map(([produtoId, quantidade]) => ({
      produto_id: produtoId,
      quantidade,
    }));
    const order = await request("/api/pedidos", {
      method: "POST",
      body: JSON.stringify({ itens }),
    });
    state.cart.clear();
    renderCart();
    await loadOrders();
    showToast(`Pedido #${order.id} criado com sucesso.`);
    byId("pedidos").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.textContent = "Enviar pedido";
    button.disabled = state.cart.size === 0;
  }
}

async function updateStatus(orderId, status, button) {
  button.disabled = true;
  try {
    await request(`/api/pedidos/${orderId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    await loadOrders();
    showToast(`Pedido #${orderId} atualizado para ${statusLabels[status].toLowerCase()}.`);
  } catch (error) {
    button.disabled = false;
    showToast(error.message, true);
  }
}

async function cancelOrder(orderId, button) {
  if (!window.confirm(`Cancelar o pedido #${orderId}? Esta ação não pode ser desfeita.`)) return;
  button.disabled = true;
  try {
    await request(`/api/pedidos/${orderId}`, { method: "DELETE" });
    await loadOrders();
    showToast(`Pedido #${orderId} cancelado.`);
  } catch (error) {
    button.disabled = false;
    showToast(error.message, true);
  }
}

byId("submit-order").addEventListener("click", submitOrder);
byId("refresh-orders").addEventListener("click", loadOrders);

Promise.all([loadProducts(), loadOrders()]);
