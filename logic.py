from config import MENU, INITIAL_BALANCE

# Хранилище данных пользователей (в реальном проекте - БД)
user_data = {}

def get_user(user_id):
    """Получить данные пользователя или создать новые"""
    if user_id not in user_data:
        user_data[user_id] = {
            'balance': INITIAL_BALANCE,
            'cart': [],
            'order_confirmed': False
        }
    return user_data[user_id]

def get_balance(user_id):
    """Получить баланс пользователя"""
    return get_user(user_id)['balance']

def add_to_cart(user_id, item_numbers):
    """Добавить товары в корзину по номерам"""
    user = get_user(user_id)
    cart = []
    total = 0
    
    for num in item_numbers:
        if num in MENU:
            item = MENU[num].copy()
            cart.append(item)
            total += item['price']
    
    user['cart'] = cart
    user['order_confirmed'] = False
    return cart, total

def get_cart_total(user_id):
    """Получить общую сумму корзины"""
    user = get_user(user_id)
    return sum(item['price'] for item in user['cart'])

def confirm_order(user_id):
    """Подтвердить заказ и списать средства"""
    user = get_user(user_id)
    total = get_cart_total(user_id)
    
    if total == 0:
        return False, 0, "Корзина пуста!"
    
    if user['balance'] >= total:
        user['balance'] -= total
        user['order_confirmed'] = True
        return True, total, "Заказ подтверждён!"
    else:
        return False, total, "Недостаточно средств! X_X"

def clear_cart(user_id):
    """Очистить корзину"""
    user = get_user(user_id)
    user['cart'] = []
    user['order_confirmed'] = False

def format_menu():
    """Отформатировать меню для вывода"""
    text = "⋆ ˚｡⋆୨♡୧⋆ ˚｡⋆ *НАШЕ МЕНЮ* ⋆ ˚｡⋆୨♡୧⋆ ˚｡⋆\n\n"
    for num, item in MENU.items():
        text += f"`{num}.` {item['name']} — *${item['price']}*\n"
    text += "\n *Чтобы сделать заказ, отправьте номера блюд через пробел*"
    text += "\n_Например: 1 3 7_"
    return text

def format_cart(user_id):
    """Отформатировать корзину для вывода"""
    user = get_user(user_id)
    if not user['cart']:
        return "Ваша корзина пуста X_X"
    
    text = "*Ваш заказ:*\n\n"
    for i, item in enumerate(user['cart'], 1):
        text += f"{i}. {item['name']} — *${item['price']}*\n"
    
    total = get_cart_total(user_id)
    text += f"\n*Итого: ${total}*"
    text += f"\nВаш баланс: *${user['balance']}*"
    
    return text

def format_receipt(user_id):
    """Создать красивый чек"""
    user = get_user(user_id)
    total = get_cart_total(user_id)
    
    receipt = "╔══════════════════════════════╗\n"
    receipt += "║       ✮КАФЕ БУДУЩЕГО✮       ║\n"
    receipt += "╠══════════════════════════════╣\n"
    receipt += "║         ЧЕК ОПЛАТЫ          ║\n"
    receipt += "╠══════════════════════════════╣\n"
    
    for item in user['cart']:
        name = item['name'][:20]  # Обрезаем длинные названия
        price = f"${item['price']}"
        receipt += f"║ {name:<20} {price:>6} ║\n"
    
    receipt += "╠══════════════════════════════╣\n"
    receipt += f"║ ИТОГО:                      ║\n"
    receipt += f"║         ${total:>20} ║\n"
    receipt += "╠══════════════════════════════╣\n"
    receipt += f"║ ОПЛАЧЕНО:     ${total:>13} ║\n"
    receipt += f"║ ОСТАТОК:      ${user['balance']:>13} ║\n"
    receipt += "╠══════════════════════════════╣\n"

    receipt += "║   ⨳ ЗАКАЗ ПОДТВЕРЖДЁН ⨳   ║\n"
    receipt += "║   Спасибо за покупку!     ║\n"
    receipt += "╚══════════════════════════════╝\n"
    
    return receipt
