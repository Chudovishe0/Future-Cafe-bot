from config import CURRENCY, DISCOUNT, MIN_SUM

# Меню кафе
MENU = {
    "🍕 Пицца Маргарита": 45,
    "🍔 Бургер": 38,
    "🌭 Хот-дог": 22,
    "🍟 Картофель фри": 18,
    "🥗 Салат": 25,
    "🥤 Кола": 10,
    "🧃 Сок": 12,
    "☕ Кофе": 15,
    "🍰 Чизкейк": 20,
    "🍦 Мороженое": 16
}

# Корзины пользователей
carts = {}


def create_cart(user_id):
    """Создать корзину, если её нет."""
    if user_id not in carts:
        carts[user_id] = []


def add_item(user_id, item):
    """Добавить товар в корзину."""
    create_cart(user_id)

    if item in MENU:
        carts[user_id].append(item)
        return True

    return False


def clear_cart(user_id):
    """Очистить корзину."""
    carts[user_id] = []


def get_cart(user_id):
    """Получить список товаров."""
    create_cart(user_id)
    return carts[user_id]


def get_total(user_id):
    """Подсчитать сумму заказа."""
    create_cart(user_id)

    total = 0

    for item in carts[user_id]:
        total += MENU[item]

    return total


def get_discount(total):
    """Рассчитать скидку."""

    if total >= MIN_SUM:
        return total * DISCOUNT / 100

    return 0


def get_final_price(user_id):
    """Получить итоговую стоимость."""

    total = get_total(user_id)
    discount = get_discount(total)

    return total - discount


def cart_text(user_id):
    """Красивый вывод корзины."""

    create_cart(user_id)

    if len(carts[user_id]) == 0:
        return "🛒 Корзина пуста."

    text = "🛒 Ваша корзина:\n\n"

    for item in carts[user_id]:
        text += f"{item} — {MENU[item]} {CURRENCY}\n"

    total = get_total(user_id)
    discount = get_discount(total)
    final_price = total - discount

    text += "\n"
    text += f"💰 Сумма: {total} {CURRENCY}\n"

    if discount > 0:
        text += f"🎁 Скидка: {discount:.1f} {CURRENCY}\n"

    text += f"💳 К оплате: {final_price:.1f} {CURRENCY}"

    return text


def menu_text():
    """Красивое меню."""

    text = "🍽 *Меню Future Cafe*\n\n"

    for item, price in MENU.items():
        text += f"{item} — {price} {CURRENCY}\n"

    return text
