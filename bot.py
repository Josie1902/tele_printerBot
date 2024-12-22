import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

printers = {
    "Printer A": {"status": "🟢 Working", "down_counter": 0, "comment": None},
    "Printer B": {"status": "🟢 Working", "down_counter": 0, "comment": None},
}

# Dictionary to track user state for comments
user_comment_state = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Send a welcome message with available commands."""
    bot.send_message(message.chat.id,
                     "Welcome! Use /status to check printer statuses or /update to update printer statuses.",
                     )


@bot.message_handler(commands=['status'])
def show_status(message):
    """Show the status of all printers."""
    printer_statuses = "\n\n".join(
        f"""<b>{name}</b>
        Status: {info['status']} {'(down counter: ' + str(info['down_counter']) + ')' if info['status'] == '🔴 Down' else ''}
        Latest Comment: {info['comment'] if info['comment'] else '-'}"""
        for name, info in printers.items()
    )
    status_message = "🖨️ <b>PRINTER STATUS</b>\n\n" + printer_statuses
    bot.send_message(message.chat.id, status_message, parse_mode='HTML')


@bot.message_handler(commands=['update'])
def choose_printer(message):
    """Show a list of printers for the user to choose from."""
    markup = InlineKeyboardMarkup()
    for printer_name in printers.keys():
        markup.add(InlineKeyboardButton(
            printer_name, callback_data=f"select|{printer_name}"))
    bot.send_message(
        message.chat.id, "🤔 Choose a printer to update:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("select|"))
def update_printer_status(call):
    """Allow users to set the status of a selected printer."""
    printer_name = call.data.split("|")[1]
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "Working", callback_data=f"status|{printer_name}|working"),
        InlineKeyboardButton(
            "Down", callback_data=f"status|{printer_name}|down"),
    )
    bot.edit_message_text(
        f"Update the status for {printer_name}:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("status|"))
def handle_status_update(call):
    """Update the status of the printer and ask if the user wants to leave a comment."""
    _, printer_name, status = call.data.split("|")
    if status == "working":
        printers[printer_name]["status"] = "🟢 Working"
        printers[printer_name]["down_counter"] = 0
    elif status == "down":
        printers[printer_name]["status"] = "🔴 Down"
        printers[printer_name]["down_counter"] += 1

    # Ask if the user wants to leave a comment
    user_comment_state[call.from_user.id] = {"printer_name": printer_name}
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "Yes", callback_data=f"comment|{printer_name}|yes"),
        InlineKeyboardButton("No", callback_data=f"comment|{printer_name}|no"),
    )
    message = f"{printer_name} updated to {status}. Do you want to leave a comment?\n<b>Your Telegram username will be displayed with your comment.</b>"
    bot.send_message(call.message.chat.id, message,
                     reply_markup=markup, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith("comment|"))
def handle_comment_choice(call):
    """Handle the user's choice to leave a comment or not."""
    _, printer_name, choice = call.data.split("|")
    if choice == "yes":
        user_comment_state[call.from_user.id]["leave_comment"] = True
        bot.send_message(call.message.chat.id, "Please send your comment:")
    else:
        bot.send_message(call.message.chat.id, "No comment added.")
        del user_comment_state[call.from_user.id]


@bot.message_handler(func=lambda message: message.from_user.id in user_comment_state and user_comment_state[message.from_user.id].get("leave_comment"))
def handle_comment(message):
    """Save the latest comment for the printer along with the user's handle."""
    user_id = message.from_user.id
    user_data = user_comment_state[user_id]
    printer_name = user_data["printer_name"]
    comment = message.text

    # Get the user's handle
    username = message.from_user.username
    handle = f"@{username}" if username else message.from_user.first_name

    # Update the latest comment for the printer
    printers[printer_name]["comment"] = f"{comment} ({handle})"
    bot.send_message(
        message.chat.id, f"✅ Comment saved for {printer_name}: \"{comment} ({handle})\"")

    del user_comment_state[user_id]


bot.infinity_polling()
