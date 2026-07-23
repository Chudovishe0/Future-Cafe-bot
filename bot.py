import telebot
from telebot import types
from config import TOKEN
from logic import (
    get_balance, add_to_cart, confirm_order, 
    clear_cart, format_menu, format_cart, 
    format_receipt, get_user
)

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Хранилище состояний пользователей
user_states = {}

# ОБРАБОТЧИКИ

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    get_user(user_id)  # Инициализируем пользователя
    
    # Создаём клавиатуру
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_menu = types.KeyboardButton("Меню")
    btn_balance = types.KeyboardButton("Ваш баланс")
    btn_cart = types.KeyboardButton("Корзина")
    keyboard.add(btn_menu, btn_balance, btn_cart)
    
    welcome_text = (
        "*Привет! Я - кафе будущего!*\n\n"
        "Здесь ты можешь заказать блюда из нашего футуристического меню.\n"
        "У тебя на счету *$150* для старта.\n\n"
        "*С помощью кнопок ниже выбери интересующий тебя вопрос:*"
    )
    
    bot.send_message(
        user_id, 
        welcome_text, 
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == "Меню")
def show_menu(message):
    user_id = message.chat.id
    menu_text = format_menu()
    bot.send_message(
        user_id, 
        menu_text, 
        parse_mode='Markdown'
    )
    bot.send_message(
        user_id,
        "*Введите номера блюд через пробел, чтобы добавить их в корзину*\n\n"
        "_Например: 1 3 7_",
        parse_mode='Markdown'
    )
    user_states[user_id] = 'awaiting_order'

@bot.message_handler(func=lambda message: message.text == "Ваш баланс")
def show_balance(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    bot.send_message(
        user_id, 
        f"*Ваш текущий баланс: ${balance}*\n\n"
        f"_Деньги на счёте позволяют вам заказывать блюда из меню!_",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == "Корзина")
def show_cart(message):
    user_id = message.chat.id
    cart_text = format_cart(user_id)
    
    if "пуста" in cart_text:
        bot.send_message(
            user_id,
            "*Ваша корзина пуста! X_X*\n\n"
            "Выберите 'Меню', чтобы добавить блюда.",
            parse_mode='Markdown'
        )
        return
    
    # Создаём инлайн-клавиатуру для подтверждения
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_confirm = types.InlineKeyboardButton("Подтвердить заказ", callback_data="confirm_order")
    btn_clear = types.InlineKeyboardButton("Очистить корзину", callback_data="clear_cart")
    btn_menu_back = types.InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")
    keyboard.add(btn_confirm, btn_clear, btn_menu_back)
    
    bot.send_message(
        user_id, 
        cart_text + "\n\n*Нажмите кнопку ниже, чтобы подтвердить заказ*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text and message.text.replace(' ', '').isdigit())
def handle_order_input(message):
    user_id = message.chat.id
    
    # Проверяем, ожидаем ли мы ввод номера блюда
    if user_states.get(user_id) != 'awaiting_order':
        bot.send_message(
            user_id, 
            "Сначала выберите 'Меню' для заказа!"
        )
        return
    
    # Парсим номера блюд
    numbers = [int(num) for num in message.text.split() if num.isdigit()]
    
    if not numbers:
        bot.send_message(
            user_id, 
            "Пожалуйста, введите номера блюд через пробел\n"
            "_Например: 1 3 7_",
            parse_mode='Markdown'
        )
        return
    
    # Добавляем в корзину
    cart, total = add_to_cart(user_id, numbers)
    if not cart:
        bot.send_message(
            user_id, 
            "В меню нет таких номеров. Пожалуйста, проверьте список!"
        )
        return
    
    # Показываем корзину
    cart_text = format_cart(user_id)
    
    bot.send_message(
        user_id, 
        f"*Добавлено в корзину!*\n\n{cart_text}",
        parse_mode='Markdown'
    )
    bot.send_message(
        user_id,
        "*Чтобы просмотреть корзину и подтвердить заказ, нажмите кнопку 'Корзина'*",
        parse_mode='Markdown'
    )
    
    # Сбрасываем состояние
    user_states[user_id] = None

# INLINE CALLBACKS

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id
    
    if call.data == "confirm_order":
        # Подтверждаем заказ
        success, total, message_text = confirm_order(user_id)
        
        if success:
            # Отправляем красивый чек
            receipt = format_receipt(user_id)
            bot.send_message(
                user_id,
                f"```\n{receipt}\n```",
                parse_mode='Markdown'
            )
            
            # Отправляем дополнительное сообщение
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn_menu = types.KeyboardButton("Меню")
            btn_balance = types.KeyboardButton("Ваш баланс")
            btn_cart = types.KeyboardButton("Корзина")
            keyboard.add(btn_menu, btn_balance, btn_cart)
            
            bot.send_message(
                user_id,
                f"*Заказ подтверждён!*\n\n"
                f"Чек отправлен выше.\n"
                f"Ваш новый баланс: *${get_balance(user_id)}*\n\n"
                f"Хотите сделать новый заказ? Просто нажмите 'Меню'!",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        else:
            if "пуста" in message_text:
                bot.send_message(
                    user_id,
                    "*Корзина пуста!*\n\n"
                    "Добавьте блюда через меню.",
                    parse_mode='Markdown'
                )
            else:
                # Недостаточно средств
                bot.send_message(
                    user_id,
                    f"*У вас недостаточно средств на счету! X_X*\n\n"
                    f"Ваш баланс: *${get_balance(user_id)}*\n"
                    f"Нужно: *${total}*\n\n"
                    f"*Нажмите кнопку ниже, чтобы собрать заказ заново*",
                    parse_mode='Markdown'
                )
                
                # Кнопка для пересборки заказа
                keyboard = types.InlineKeyboardMarkup()
                btn_rebuild = types.InlineKeyboardButton("Пересобрать заказ", callback_data="rebuild_order")
                keyboard.add(btn_rebuild)
                bot.send_message(
                    user_id,
                    "Нажмите, чтобы начать новый заказ:",
                    reply_markup=keyboard
                )
    
    elif call.data == "clear_cart":
        # Очистить корзину
        clear_cart(user_id)
        bot.send_message(
            user_id,
            "*Корзина очищена! ^_^*\n\n"
            "Вы можете выбрать блюда заново через меню.",
            parse_mode='Markdown'
        )
        
        # Возвращаем обычную клавиатуру
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_menu = types.KeyboardButton("Меню")
        btn_balance = types.KeyboardButton("Ваш баланс")
        btn_cart = types.KeyboardButton("Корзина")
        keyboard.add(btn_menu, btn_balance, btn_cart)
        bot.send_message(
            user_id,
            "Выберите действие:",
            reply_markup=keyboard
        )
    
    elif call.data == "back_to_menu":
        # Возврат в меню
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_menu = types.KeyboardButton("Меню")
        btn_balance = types.KeyboardButton("Ваш баланс")
        btn_cart = types.KeyboardButton("Корзина")
        keyboard.add(btn_menu, btn_balance, btn_cart)
        
        bot.send_message(
            user_id,
            "*Возвращаемся в главное меню*",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
        # Убираем инлайн-клавиатуру
        try:
            bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except:
            pass
    
    elif call.data == "rebuild_order":
        # Пересобрать заказ (очищаем корзину и показываем меню)
        clear_cart(user_id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_menu = types.KeyboardButton("Меню")
        btn_balance = types.KeyboardButton("Ваш баланс")
        btn_cart = types.KeyboardButton("Корзина")
        keyboard.add(btn_menu, btn_balance, btn_cart)
        
        bot.send_message(
            user_id,
            "*Давайте соберём заказ заново! ^_^*\n\n"
            "Нажмите 'Меню', чтобы посмотреть доступные блюда.",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
        # Убираем инлайн-клавиатуру
        try:
            bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except:
            pass
    
    # Убираем инлайн-клавиатуру на старом сообщении
    try:
        bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except:
        pass

#ЗАПУСК

if __name__ == "__main__":
    print("Бот 'Кафе Будущего' запущен!")
    print("Нажми Ctrl+C для остановки")
    try:
        bot.polling(non_stop=True, interval=0)
    except Exception as e:
        print(f"Ошибка: {e}")
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )
