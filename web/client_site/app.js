const API_BASE = "http://localhost:8000";

const demoProducts = [
  { id: 1, name: "Gentle Cleansing Gel", price: "890.00", description: "Мягкое очищение без стянутости", stock_quantity: 24, category: { id: 1, name: "Очищение" }, brand: { name: "DemiLab" }, usage_instructions: "Нанести на влажную кожу, вспенить, смыть водой." },
  { id: 2, name: "Barrier Repair Cream", price: "1450.00", description: "Крем для восстановления барьера кожи.", stock_quantity: 18, category: { id: 2, name: "Увлажнение" }, brand: { name: "DemiLab" }, usage_instructions: "Использовать утром и вечером после сыворотки." },
  { id: 3, name: "Niacinamide Serum 10%", price: "1190.00", description: "Себорегуляция и ровный тон.", stock_quantity: 15, category: { id: 3, name: "Сыворотки" }, brand: { name: "SkinTheory" }, usage_instructions: "Нанести 2-3 капли перед кремом." },
  { id: 4, name: "Daily SPF 50", price: "1590.00", description: "Лёгкий дневной SPF для города.", stock_quantity: 20, category: { id: 4, name: "SPF" }, brand: { name: "SunCare KG" }, usage_instructions: "Нанести за 15 минут до выхода." },
];

const state = {
  token: localStorage.getItem("demi_client_token") || "",
  products: [],
  categories: [],
  cart: JSON.parse(localStorage.getItem("demi_cart") || "[]"),
  favorites: JSON.parse(localStorage.getItem("demi_favorites") || "[]"),
  routine: JSON.parse(localStorage.getItem("demi_routine") || "[]"),
  theme: localStorage.getItem("demi_theme") || "light",
  me: null,
  bonuses: null,
  orders: [],
  consultations: [],
  category: "all",
  search: "",
};

const defaultRoutine = [
  { id: "morning-cleanse", group: "Утренний уход", title: "Умывание", time: "1 мин", icon: "☼", done: true },
  { id: "morning-toner", group: "Утренний уход", title: "Тонер", time: "2 мин", icon: "☼", done: true },
  { id: "morning-cream", group: "Утренний уход", title: "Увлажняющий крем", time: "2 мин", icon: "☼", done: false },
  { id: "morning-spf", group: "Утренний уход", title: "SPF защита", time: "1 мин", icon: "☼", done: false },
  { id: "evening-cleanse", group: "Вечерний уход", title: "Двойное очищение", time: "3 мин", icon: "☾", done: true },
  { id: "evening-serum", group: "Вечерний уход", title: "Сыворотка", time: "2 мин", icon: "☾", done: false },
  { id: "evening-cream", group: "Вечерний уход", title: "Ночной крем", time: "2 мин", icon: "☾", done: false },
  { id: "weekly-mask", group: "Еженедельно", title: "Успокаивающая маска", time: "10 мин", icon: "✦", done: false },
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const money = (value) => `${Number(value || 0).toLocaleString("ru-RU")} сом`;

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("is-visible"), 2300);
}

function setLoading(isLoading) {
  $("#loadingOverlay")?.classList.toggle("is-visible", isLoading);
  $(".phone-shell")?.classList.toggle("is-loading", isLoading);
}

function applyTheme() {
  document.body.classList.toggle("theme-dark", state.theme === "dark");
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  if (response.status === 204) return null;
  return response.json();
}

async function ensureDemoUser() {
  if (state.token) return;
  const stamp = Date.now().toString().slice(-6);
  const payload = {
    email: `client-${stamp}@demiresults.local`,
    phone: `+996700${stamp}`,
    password: "StrongPass12345!",
    first_name: "Demi",
  };
  const data = await api("/api/auth/register/", { method: "POST", body: JSON.stringify(payload) });
  state.token = data.access;
  localStorage.setItem("demi_client_token", state.token);
}

async function loadData() {
  setLoading(true);
  try {
    const productData = await api("/api/catalog/products/");
    state.products = productData.results || productData;
  } catch {
    state.products = demoProducts;
  }
  state.categories = ["all", ...new Map(state.products.map((p) => [p.category?.id || p.category?.name, p.category])).values()].filter(Boolean);
  try {
    await ensureDemoUser();
    state.me = await api("/api/me/");
    state.bonuses = await api("/api/me/bonuses/");
    const orderData = await api("/api/me/orders/");
    state.orders = orderData.results || orderData;
    const consultData = await api("/api/me/consultations/");
    state.consultations = consultData.results || consultData;
  } catch {
    showToast("Backend недоступен, показан demo-режим");
  }
  applyTheme();
  renderAll();
  setLoading(false);
}

function productDescription(product) {
  return product.description || product.ingredients || product.brand?.name || "Персональный уход DemiResults";
}

function renderProductCard(product) {
  const isFavorite = state.favorites.includes(String(product.id));
  return `
    <article class="product-card">
      <div class="product-visual" data-detail="${product.id}">
        <div class="product-icon"></div>
        <button class="favorite-btn ${isFavorite ? "is-active" : ""}" data-favorite="${product.id}" aria-label="В избранное">♡</button>
      </div>
      <div class="product-info">
        <span class="brand-name">${product.brand?.name || "DemiResults"}</span>
        <h3 data-detail="${product.id}">${product.name}</h3>
        <div class="rating-line">★★★★★ <span>4.9</span></div>
        <strong>${money(product.price)}</strong>
        <div class="product-actions">
          <button class="cart-btn" data-add="${product.id}">+ В корзину</button>
          <button class="detail-btn" data-detail="${product.id}">Подробнее</button>
        </div>
      </div>
    </article>
  `;
}

function filteredProducts() {
  return state.products.filter((product) => {
    const byCategory = state.category === "all" || String(product.category?.id || product.category?.name) === String(state.category);
    const text = `${product.name} ${product.description || ""} ${product.brand?.name || ""}`.toLowerCase();
    return byCategory && text.includes(state.search.toLowerCase());
  });
}

function renderCatalog() {
  $("#homeProducts").innerHTML = state.products.slice(0, 4).map(renderProductCard).join("");
  $("#categoryChips").innerHTML = state.categories
    .map((category) => {
      const id = category === "all" ? "all" : category.id || category.name;
      const name = category === "all" ? "Все" : category.name;
      return `<button class="chip ${String(state.category) === String(id) ? "is-active" : ""}" data-category="${id}">${name}</button>`;
    })
    .join("");
  $("#catalogProducts").innerHTML = filteredProducts().map(renderProductCard).join("") || `<p class="empty">Ничего не найдено</p>`;
}

function cartLines() {
  return state.cart.map((line) => {
    const product = state.products.find((item) => String(item.id) === String(line.id)) || line;
    return { ...line, product, total: Number(product.price || 0) * line.quantity };
  });
}

function renderCart() {
  const lines = cartLines();
  $("#cartItems").innerHTML =
    lines
      .map(
        (line) => `
          <article class="cart-item">
            <div>
              <h3>${line.product.name}</h3>
              <p>${money(line.product.price)} · ${line.quantity} шт</p>
              <button class="remove-btn" data-remove="${line.id}">Убрать</button>
            </div>
            <div class="qty-stepper">
              <button data-dec="${line.id}">−</button>
              <strong>${line.quantity}</strong>
              <button data-inc="${line.id}">+</button>
            </div>
          </article>
        `
      )
      .join("") || `<article class="cart-item"><div><h3>Корзина пустая</h3><p>Добавьте уход из каталога</p></div></article>`;
  $("#cartTotal").textContent = money(lines.reduce((sum, line) => sum + line.total, 0));
  $$("[data-cart-count]").forEach((badge) => {
    badge.textContent = state.cart.reduce((sum, line) => sum + line.quantity, 0);
  });
  localStorage.setItem("demi_cart", JSON.stringify(state.cart));
}

function renderFavorites() {
  const favoriteIds = new Set(state.favorites.map(String));
  const products = state.products.filter((product) => favoriteIds.has(String(product.id)));
  const target = $("#favoriteProducts");
  if (target) {
    target.innerHTML =
      products.map(renderProductCard).join("") ||
      `<article class="empty-card"><h3>Избранного пока нет</h3><p>Нажмите сердечко в каталоге, чтобы сохранить средство.</p></article>`;
  }
  $$("[data-favorite-count]").forEach((badge) => {
    badge.textContent = products.length;
  });
  localStorage.setItem("demi_favorites", JSON.stringify(state.favorites));
}

function renderOrderHistory() {
  return (
    state.orders
      .slice(0, 4)
      .map((order) => `<article class="order-card"><div><h3>Заказ #${order.id}</h3><p>${order.status}</p></div><strong>${money(order.total)}</strong></article>`)
      .join("") || `<article class="order-card"><div><h3>Заказов нет</h3><p>Оформите первый заказ из корзины</p></div></article>`
  );
}

function renderConsultationHistory() {
  return (
    state.consultations
      .slice(0, 4)
      .map((item) => `<article class="timeline-item"><h3>${new Date(item.scheduled_at).toLocaleString("ru-RU", { dateStyle: "medium", timeStyle: "short" })}</h3><p>${item.status} · ${item.questionnaire?.concern || "подбор ухода"}</p></article>`)
      .join("") || `<article class="timeline-item"><h3>Истории нет</h3><p>Запишитесь на консультацию</p></article>`
  );
}

function renderProfile() {
  const profile = state.me?.client_profile || {};
  $("#profileName").textContent = state.me?.first_name || "Клиент";
  $("#profilePhone").textContent = state.me?.phone || "+996";
  $("#firstName").value = state.me?.first_name || "";
  $("#skinType").value = profile.skin_type || "";
  $("#skinConcerns").value = profile.skin_concerns || "";
  $("#bonusBalance").textContent = money(state.bonuses?.balance || 0);
  $("#homeBonus").textContent = Number(state.bonuses?.balance || 0).toLocaleString("ru-RU");
  const nextConsultation = state.consultations[0];
  $("#homeConsultTime").textContent = nextConsultation ? new Date(nextConsultation.scheduled_at).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }) : "—";
  $("#orderHistoryCount").textContent = `${state.orders.length} ${state.orders.length === 1 ? "заказ" : "заказов"}`;
  $("#consultHistoryCount").textContent = `${state.consultations.length} ${state.consultations.length === 1 ? "запись" : "записей"}`;
  $("#profileOrdersScreen").innerHTML = renderOrderHistory();
  $("#profileConsultationsScreen").innerHTML = renderConsultationHistory();
  $$(".theme-toggle button").forEach((button) => button.classList.toggle("is-active", button.dataset.theme === state.theme));
}

function renderConsultations() {
  const html =
    state.consultations
      .map(
        (item) => `
          <article class="timeline-item">
            <h3>${new Date(item.scheduled_at).toLocaleString("ru-RU", { dateStyle: "medium", timeStyle: "short" })}</h3>
            <p>${item.status} · консультант DemiResults</p>
            <p>Жалоба: ${item.questionnaire?.concern || "персональный подбор ухода"}</p>
          </article>
        `
      )
      .join("") || `<article class="timeline-item"><h3>Нет записей</h3><p>Выберите время и отправьте анкету</p></article>`;
  $("#consultationsList").innerHTML = html;
  $("#routineConsultationsList").innerHTML = html;
}

function renderRoutine() {
  if (!state.routine.length) {
    state.routine = defaultRoutine;
  }
  const done = state.routine.filter((item) => item.done).length;
  const progress = Math.round((done / state.routine.length) * 100);
  $("#routineProgressText").textContent = `${done} из ${state.routine.length} выполнено`;
  $("#homeRoutineDone").textContent = `${done}/${state.routine.length}`;
  $("#routineHeroProgress").textContent = `${done} из ${state.routine.length}`;
  $("#routineDate").textContent = new Date().toLocaleDateString("ru-RU", { weekday: "long", day: "numeric", month: "long" });
  ["#routineRing", "#routineRingLarge"].forEach((selector) => {
    const ring = $(selector);
    if (!ring) return;
    ring.textContent = `${progress}%`;
    ring.style.setProperty("--progress", `${progress}%`);
  });
  const groups = [...new Set(state.routine.map((step) => step.group))];
  $("#routineList").innerHTML = groups
    .map((group) => {
      const items = state.routine.filter((step) => step.group === group);
      const groupDone = items.filter((step) => step.done).length;
      return `
        <section class="routine-group">
          <header class="routine-group-head">
            <div class="step-icon">${items[0]?.icon || "◌"}</div>
            <h2>${group}</h2>
            <span>${groupDone}/${items.length} выполнено</span>
          </header>
          ${items
            .map(
              (step) => `
                <article class="routine-task ${step.done ? "is-done" : ""}" data-routine="${step.id}">
                  <button class="routine-dot" aria-label="Отметить">${step.done ? "✓" : ""}</button>
                  <h3>${step.title}</h3>
                  <span class="routine-time">${step.time}</span>
                </article>
              `
            )
            .join("")}
        </section>
      `;
    })
    .join("");
  localStorage.setItem("demi_routine", JSON.stringify(state.routine));
}

function renderAll() {
  renderCatalog();
  renderCart();
  renderFavorites();
  renderProfile();
  renderConsultations();
  renderRoutine();
}

function navigate(screen) {
  $$(".screen").forEach((item) => item.classList.toggle("is-active", item.dataset.screen === screen));
  const navScreen = {
    cart: "catalog",
    favorites: "catalog",
    consultations: "routine",
    "profile-orders": "profile",
    "profile-consultations": "profile",
  }[screen] || screen;
  $$(".bottom-nav button").forEach((item) => item.classList.toggle("is-active", item.dataset.nav === navScreen));
  updateNavLiquid(navScreen);
}

function updateNavLiquid(screen = "home") {
  const nav = $(".bottom-nav");
  const liquid = $(".nav-liquid");
  const activeButton = nav?.querySelector(`[data-nav="${screen}"]`);
  if (!nav || !liquid || !activeButton) return;
  const navRect = nav.getBoundingClientRect();
  const buttonRect = activeButton.getBoundingClientRect();
  liquid.style.width = `${buttonRect.width}px`;
  liquid.style.transform = `translate3d(${buttonRect.left - navRect.left - 8}px, 0, 0)`;
  nav.classList.add("is-moving");
  clearTimeout(updateNavLiquid.timer);
  updateNavLiquid.timer = setTimeout(() => nav.classList.remove("is-moving"), 560);
}

function addToCart(productId) {
  const existing = state.cart.find((item) => String(item.id) === String(productId));
  if (existing) existing.quantity += 1;
  else state.cart.push({ id: productId, quantity: 1 });
  renderCart();
  showToast("Добавлено в корзину");
}

function toggleFavorite(productId) {
  const id = String(productId);
  if (state.favorites.includes(id)) state.favorites = state.favorites.filter((item) => item !== id);
  else state.favorites.push(id);
  renderCatalog();
  renderFavorites();
}

function openProductDetail(productId) {
  const product = state.products.find((item) => String(item.id) === String(productId));
  if (!product) return;
  $("#productDetailBody").innerHTML = `
    <span class="brand-name">${product.brand?.name || "DemiResults"}</span>
    <h1>${product.name}</h1>
    <h2>${money(product.price)} <span class="rating-line">★★★★★ 4.9</span></h2>
    <div class="detail-tags"><span>Увлажнение</span><span>Акне</span><span>Комбинированная</span></div>
    <p class="eyebrow">О продукте</p>
    <p>${productDescription(product)}</p>
    <p class="eyebrow">Способ применения</p>
    <p>${product.usage_instructions || "Нанести на очищенную кожу лёгкими похлопывающими движениями."}</p>
    <button class="primary-btn" data-add="${product.id}">Добавить в корзину · ${money(product.price)}</button>
  `;
  $("#productModal").classList.add("is-visible");
  $("#productModal").setAttribute("aria-hidden", "false");
}

function closeProductDetail() {
  $("#productModal").classList.remove("is-visible");
  $("#productModal").setAttribute("aria-hidden", "true");
}

async function checkout() {
  if (!state.cart.length) {
    showToast("Корзина пустая");
    return;
  }
  try {
    const items = state.cart.map((line) => ({ product: Number(line.id), quantity: line.quantity }));
    const address = $("#deliveryAddress").value.trim();
    const card = $("#paymentCard").value;
    const order = await api("/api/me/orders/", { method: "POST", body: JSON.stringify({ items, comment: `Address: ${address || "not set"}; card: ${card}` }) });
    state.orders.unshift(order);
    state.cart = [];
    renderAll();
    showToast("Заказ создан");
  } catch {
    showToast("Не удалось оформить заказ");
  }
}

document.addEventListener("click", (event) => {
  const nav = event.target.closest("[data-nav]");
  const add = event.target.closest("[data-add]");
  const inc = event.target.closest("[data-inc]");
  const dec = event.target.closest("[data-dec]");
  const remove = event.target.closest("[data-remove]");
  const category = event.target.closest("[data-category]");
  const routineStep = event.target.closest("[data-routine]");
  const favorite = event.target.closest("[data-favorite]");
  const detail = event.target.closest("[data-detail]");
  const theme = event.target.closest("[data-theme]");

  if (nav) navigate(nav.dataset.nav);
  if (favorite) {
    event.stopPropagation();
    toggleFavorite(favorite.dataset.favorite);
    return;
  }
  if (add) addToCart(add.dataset.add);
  if (detail) openProductDetail(detail.dataset.detail);
  if (inc) {
    const item = state.cart.find((line) => String(line.id) === inc.dataset.inc);
    if (item) item.quantity += 1;
    renderCart();
  }
  if (dec) {
    const item = state.cart.find((line) => String(line.id) === dec.dataset.dec);
    if (item) item.quantity -= 1;
    state.cart = state.cart.filter((line) => line.quantity > 0);
    renderCart();
  }
  if (remove) {
    state.cart = state.cart.filter((line) => String(line.id) !== remove.dataset.remove);
    renderCart();
  }
  if (category) {
    state.category = category.dataset.category;
    renderCatalog();
  }
  if (routineStep) {
    const step = state.routine.find((item) => item.id === routineStep.dataset.routine);
    if (step) step.done = !step.done;
    renderRoutine();
  }
  if (theme) {
    state.theme = theme.dataset.theme;
    localStorage.setItem("demi_theme", state.theme);
    applyTheme();
    renderProfile();
  }
});

$("#catalogSearch").addEventListener("input", (event) => {
  state.search = event.target.value;
  renderCatalog();
});

$("#checkoutBtn").addEventListener("click", checkout);

$("#profileForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    state.me = await api("/api/me/", {
      method: "PATCH",
      body: JSON.stringify({
        first_name: $("#firstName").value,
        client_profile: {
          skin_type: $("#skinType").value,
          skin_concerns: $("#skinConcerns").value,
        },
      }),
    });
    renderProfile();
    showToast("Профиль сохранён");
  } catch {
    showToast("Не удалось сохранить");
  }
});

$("#consultForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const date = $("#consultDate").value;
  if (!date) return;
  try {
    const consultation = await api("/api/me/consultations/", {
      method: "POST",
      body: JSON.stringify({
        scheduled_at: new Date(date).toISOString(),
        questionnaire: { concern: $("#consultConcern").value },
      }),
    });
    state.consultations.unshift(consultation);
    renderConsultations();
    renderProfile();
    showToast("Запись создана");
    event.target.reset();
  } catch {
    showToast("Не удалось записаться");
  }
});

$("#aiForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = $("#aiInput");
  const text = input.value.trim();
  if (!text) return;
  $("#aiThread").insertAdjacentHTML("beforeend", `<article class="chat-bubble user">${text}</article>`);
  input.value = "";
  $("#aiThread").insertAdjacentHTML("beforeend", `<article class="chat-bubble ai typing">Анализирую skin card и каталог...</article>`);
  setTimeout(() => {
    $(".chat-bubble.typing")?.remove();
    const recommended = state.products.slice(0, 2);
    $("#aiThread").insertAdjacentHTML(
      "beforeend",
      `<article class="chat-bubble ai">Я проанализировала запрос. Рекомендую начать с этих средств:
        ${recommended
          .map(
            (product) => `
              <div class="chat-reco-card">
                <div class="mini-product-icon"></div>
                <div>
                  <strong>${product.name}</strong>
                  <span>ID ${product.id} · ${money(product.price)}</span>
                  <button type="button" data-add="${product.id}">Добавить в корзину →</button>
                </div>
              </div>
            `
          )
          .join("")}
      </article>`
    );
    $("#aiThread").lastElementChild.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, 520);
});

$("[data-action='refresh']").addEventListener("click", loadData);
$("#startOnboarding").addEventListener("click", () => {
  localStorage.setItem("demi_onboarded", "1");
  $("#onboarding").classList.remove("is-visible");
});
$("#closeProductModal").addEventListener("click", closeProductDetail);
$("#productModal").addEventListener("click", (event) => {
  if (event.target.id === "productModal") closeProductDetail();
});
$("#bindCardBtn").addEventListener("click", () => showToast("Локальная карта привязана"));
window.addEventListener("resize", () => updateNavLiquid(document.querySelector(".bottom-nav button.is-active")?.dataset.nav || "home"));

if (localStorage.getItem("demi_onboarded") === "1") {
  $("#onboarding").classList.remove("is-visible");
}
applyTheme();
loadData();
requestAnimationFrame(() => updateNavLiquid("home"));
