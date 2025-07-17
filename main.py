import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

TOKEN = "7785430147:AAF9ynpzPAa9aZ3eOxBDTt0MTGtTaylZP-w"
GROUP_CHAT_ID = -1002582699976
WAITING_FOR_ADDRESS = 1

logging.basicConfig(level=logging.INFO)

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Прийняв доставку", callback_data="accepted")],
        [InlineKeyboardButton("⏱ Затримуюсь", callback_data="delayed")],
        [InlineKeyboardButton("📍 Прибув", callback_data="arrived")],
        [InlineKeyboardButton("✅ Завершив доставку", callback_data="completed")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оберіть дію:", reply_markup=get_main_keyboard())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    username = query.from_user.full_name
    data = query.data

    if data == "accepted":
        context.user_data["courier_name"] = username
        await query.message.reply_text("Введіть адресу доставки:")
        return WAITING_FOR_ADDRESS

    messages = {
        "delayed": f"⚠️ Кур’єр затримується\n👤 {username}",
        "arrived": f"📍 Кур’єр прибув на місце\n👤 {username}",
        "completed": f"✅ Доставку завершено\n👤 {username}",
    }

    if data in messages:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=messages[data])
    return ConversationHandler.END

async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text
    courier = context.user_data.get("courier_name", "Невідомий")
    message = (
        f"🚚 Кур’єр прийняв доставку\n"
        f"📍 Адреса: {address}\n"
        f"👤 Кур’єр: {courier}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
    await update.message.reply_text("Адресу прийнято ✅")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Дію скасовано.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_button)],
        states={
            WAITING_FOR_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    main()
