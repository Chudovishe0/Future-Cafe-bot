import telebot
from telebot import types

from config import TOKEN, BOT_NAME
import logic

bot = telebot.TeleBot(TOKEN)


def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 Меню", "🛒 Корзина")
    kb.row("🧾 Оформить заказ", "🗑 Очистить корзину")
    kb.row("ℹ️ О кафе")

    return kb


def menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for item in logic.MENU:
        kb.add(types.KeyboardButton(item))

    kb.add(types.KeyboardButton("🔙 Назад"))

    return kb


@bot.message_handler(commands=["start"])
def start(message):

    logic.create_cart(message.chat.id)

    text = (
        f"👋 Добро пожаловать в {BOT_NAME}!\n\n"
        "🍕 Здесь можно заказать еду.\n"
        "Используйте кнопки ниже."
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "📋 Меню")
def menu(message):

    bot.send_message(
        message.chat.id,
        logic.menu_text(),
        parse_mode="Markdown",
        reply_markup=menu_keyboard()
    )


@bot.message_handler(func=lambda m: m.text in logic.MENU)
def add_food(message):

    logic.add_item(
        message.chat.id,
        message.text
    )

    bot.send_message(
        message.chat.id,
        f"✅ {message.text} добавлено в корзину!"
    )


@bot.message_handler(func=lambda m: m.text == "🛒 Корзина")
def cart(message):

    bot.send_message(
        message.chat.id,
        logic.cart_text(message.chat.id),
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🗑 Очистить корзину")
def clear_cart(message):

    logic.clear_cart(message.chat.id)

    bot.send_message(
        message.chat.id,
        "🗑 Корзина очищена!",
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "🧾 Оформить заказ")
def order(message):

    cart = logic.get_cart(message.chat.id)

    if len(cart) == 0:
        bot.send_message(
            message.chat.id,
            "❌ Ваша корзина пуста.",
            reply_markup=main_keyboard()
        )
        return

    total = logic.get_total(message.chat.id)
    discount = logic.get_discount(total)
    final_price = logic.get_final_price(message.chat.id)

    text = "🧾 Ваш заказ\n\n"

    for item in cart:
        text += f"{item} — {logic.MENU[item]} ₪\n"

    text += "\n"
    text += f"💰 Сумма: {total} ₪\n"

    if discount > 0:
        text += f"🎁 Скидка: {discount:.1f} ₪\n"

    text += f"💳 К оплате: {final_price:.1f} ₪\n\n"
    text += "❤️ Спасибо за заказ!"

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )

    logic.clear_cart(message.chat.id)


@bot.message_handler(func=lambda m: m.text == "ℹ️ О кафе")
def about(message):

    text = (
        "🍽 Future Cafe\n\n"
        "⭐ Самое современное кафе.\n"
        "🍕 Вкусная еда.\n"
        "⚡ Быстрая доставка.\n\n"
        "Спасибо, что выбрали нас!"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )
