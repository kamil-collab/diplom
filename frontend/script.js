let cart = [];

async function loadProducts() {
  try {
    const response = await fetch('/api/products');
    const products = await response.json();

    const container = document.getElementById('product-list');
    container.innerHTML = '';

    products.forEach(product => {
      const disabled = product.stock <= 0 ? 'disabled' : '';
      const card = document.createElement('div');
      card.className = 'product-card';
      card.innerHTML = `
        <img src="${product.image_path}" alt="${product.name}" class="product-image" />
        <h2>${product.name}</h2>
        <p><strong>Компания:</strong> ${product.company}</p>
        <p><strong>Цена:</strong> ${product.price} руб.</p>
        <p><strong>Остаток:</strong> <span id="stock-${product.id}">${product.stock}</span></p>
        <button onclick="addToCart(${product.id}, '${product.name}', ${product.price})" ${disabled}>Добавить в корзину</button>
      `;
      container.appendChild(card);
    });

  } catch (error) {
    console.error('Ошибка загрузки товаров:', error);
  }
}

function addToCart(id, name, price) {
  const existing = cart.find(item => item.id === id);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ id, name, price, quantity: 1 });
  }
  updateCart();
}

function updateCart() {
  const cartList = document.getElementById("cartItems");
  const total = document.getElementById("total");
  cartList.innerHTML = "";
  let sum = 0;

  cart.forEach((item, index) => {
    sum += item.price * item.quantity;
    const li = document.createElement("li");
    li.innerHTML = `${item.name} - ${item.price}₽ x${item.quantity}
      <button onclick="removeFromCart(${index})">✖</button>`;
    cartList.appendChild(li);
  });

  total.textContent = sum;
  localStorage.setItem("cart", JSON.stringify(cart));
}

function removeFromCart(index) {
  cart.splice(index, 1);
  updateCart();
}

async function buyCart() {
  if (cart.length === 0) {
    alert("Корзина пуста");
    return;
  }

  try {
    const res = await fetch('/api/buy-cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: cart })
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Не удалось оформить заказ");
      return;
    }

    alert("Спасибо за покупку!");
    cart = [];
    updateCart();
    loadProducts();

  } catch (err) {
    console.error("Ошибка при покупке:", err);
    alert("Не удалось оформить заказ");
  }
}

function loadCartFromStorage() {
  const saved = localStorage.getItem("cart");
  if (saved) {
    cart = JSON.parse(saved);
    updateCart();
  }
}

async function loadClientInfo() {
  try {
    const res = await fetch('/api/client-info');
    const info = await res.json();
    document.title = info.company_name;
    document.getElementById('company-name').textContent = info.company_name;
    document.getElementById('contact-info').innerHTML = `
      <p>контактный телефон: ${info.phone}</p>
      <p>контактная почта: ${info.email}</p>
    `;
  } catch (e) {
    console.error("Ошибка загрузки информации о компании", e);
  }
}

loadProducts();
loadCartFromStorage();
