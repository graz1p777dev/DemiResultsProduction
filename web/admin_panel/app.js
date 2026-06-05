const API_BASE = "http://localhost:8000";

const state = {
  products: [],
  orders: [],
  health: null,
  search: "",
};

const demoProducts = [
  { id: 1, name: "DemiLab Gentle Cleansing Gel", sku: "DL-CLEAN-GEL-150", price: "890.00", stock_quantity: 24, low_stock_threshold: 8, category: { name: "Очищение" }, brand: { name: "DemiLab" } },
  { id: 2, name: "DemiLab Barrier Repair Cream", sku: "DL-BARRIER-CREAM-50", price: "1450.00", stock_quantity: 5, low_stock_threshold: 6, category: { name: "Увлажнение" }, brand: { name: "DemiLab" } },
  { id: 3, name: "SkinTheory Niacinamide Serum 10%", sku: "ST-NIACINAMIDE-30", price: "1190.00", stock_quantity: 15, low_stock_threshold: 5, category: { name: "Сыворотки" }, brand: { name: "SkinTheory" } },
];

const demoOrders = [
  { id: 101, status: "CREATED", total: "1780.00", created_at: new Date().toISOString() },
  { id: 102, status: "CONFIRMED", total: "1450.00", created_at: new Date().toISOString() },
  { id: 103, status: "PACKING", total: "2350.00", created_at: new Date().toISOString() },
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const money = (value) => `${Number(value || 0).toLocaleString("ru-RU")} сом`;

async function fetchJson(path) {
  const headers = {};
  const staffToken = localStorage.getItem("demi_admin_token");
  if (staffToken) headers.Authorization = `Bearer ${staffToken}`;
  const response = await fetch(`${API_BASE}${path}`, { headers });
  if (!response.ok) throw new Error(response.statusText);
  return response.json();
}

async function loadData() {
  try {
    state.health = await fetchJson("/api/health/");
    $("#apiStatus").textContent = "API online";
    $("#metricHealth").textContent = "OK";
  } catch {
    state.health = null;
    $("#apiStatus").textContent = "API offline demo";
    $("#metricHealth").textContent = "Demo";
  }
  try {
    const products = await fetchJson("/api/catalog/products/");
    state.products = products.results || products;
  } catch {
    state.products = demoProducts;
  }
  try {
    if (!localStorage.getItem("demi_admin_token")) throw new Error("No staff token");
    const orders = await fetchJson("/api/orders/orders/");
    state.orders = orders.results || orders;
  } catch {
    state.orders = demoOrders;
  }
  renderAll();
}

function filteredProducts() {
  const query = state.search.toLowerCase();
  return state.products.filter((product) => `${product.name} ${product.sku} ${product.brand?.name || ""}`.toLowerCase().includes(query));
}

function renderMetrics() {
  $("#metricProducts").textContent = state.products.length;
  $("#metricOrders").textContent = state.orders.length;
  $("#metricStock").textContent = state.products.reduce((sum, product) => sum + Number(product.stock_quantity || 0), 0);
}

function renderChart() {
  const values = [12, 18, 10, 24, 20, 28, Math.max(8, state.orders.length * 8)];
  const labels = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
  $("#chartBars").innerHTML = values
    .map((value, index) => `<div class="bar" style="height:${value * 7}px; animation-delay:${index * 55}ms"><span>${labels[index]}</span></div>`)
    .join("");
}

function renderProducts() {
  const rows = filteredProducts()
    .map((product, index) => {
      const low = Number(product.stock_quantity || 0) <= Number(product.low_stock_threshold || 5);
      return `
        <div class="table-row" style="animation-delay:${index * 25}ms">
          <strong>${product.name}</strong>
          <span>${product.sku}</span>
          <span>${product.brand?.name || "—"}</span>
          <span>${money(product.price)}</span>
          <span class="badge ${low ? "warn" : "good"}">${product.stock_quantity || 0} шт</span>
        </div>
      `;
    })
    .join("");
  $("#productsTable").innerHTML = `
    <div class="table-row header">
      <span>Товар</span><span>SKU</span><span>Бренд</span><span>Цена</span><span>Остаток</span>
    </div>
    ${rows}
  `;
}

function renderStock() {
  const lowStock = state.products.filter((product) => Number(product.stock_quantity || 0) <= Number(product.low_stock_threshold || 5));
  $("#stockAlerts").innerHTML =
    lowStock.map((product) => `<article><strong>${product.name}</strong><span>${product.stock_quantity || 0} шт · порог ${product.low_stock_threshold || 5}</span></article>`).join("") ||
    `<article><strong>Критичных остатков нет</strong><span>Все позиции выше порога</span></article>`;

  $("#inventoryList").innerHTML = state.products
    .map((product) => `<article><strong>${product.name}</strong><span>${product.category?.name || "Категория"} · ${product.stock_quantity || 0} шт на складе</span></article>`)
    .join("");
}

function renderOrders() {
  const statuses = ["CREATED", "CONFIRMED", "PACKING", "DELIVERING", "COMPLETED"];
  $("#ordersCount").textContent = `${state.orders.length} записей`;
  $("#ordersBoard").innerHTML = statuses
    .map((status) => {
      const tickets = state.orders
        .filter((order) => order.status === status)
        .map((order) => `<article class="order-ticket"><strong>Заказ #${order.id}</strong><span>${money(order.total)} · ${new Date(order.created_at).toLocaleDateString("ru-RU")}</span></article>`)
        .join("");
      return `<section class="kanban-column"><h3>${status}</h3>${tickets || ""}</section>`;
    })
    .join("");
}

function renderAll() {
  renderMetrics();
  renderChart();
  renderProducts();
  renderStock();
  renderOrders();
}

document.addEventListener("click", (event) => {
  const tab = event.target.closest("[data-section]");
  if (!tab) return;
  const section = tab.dataset.section;
  $$("[data-section]").forEach((button) => button.classList.toggle("is-active", button.dataset.section === section));
  $$("[data-section-panel]").forEach((panel) => panel.classList.toggle("is-active", panel.dataset.sectionPanel === section));
});

$("#catalogSearch").addEventListener("input", (event) => {
  state.search = event.target.value;
  renderProducts();
});

$("#refreshBtn").addEventListener("click", loadData);

loadData();
