import io
import qrcode
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import database

TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

database.init_db()

def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🎟 Мой билет (QR-код)"), KeyboardButton("🤝 Найти собеседника"))
    markup.row(KeyboardButton("📝 Заполнить/Изменить анкету"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "🚀 **Привет! Я бот IT-митапа.**\n\n"
        "Я помогу тебе пройти регистрацию, получить электронный билет с QR-кодом "
        "и найти интересных людей для нетворкинга на мероприятии.\n\n"
        "Нажми **«📝 Заполнить/Изменить анкету»**, чтобы начать!"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "📝 Заполнить/Изменить анкету")
def start_survey(message):
    msg = bot.send_message(message.chat.id, "Как тебя зовут? (Имя и Фамилия)")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    full_name = message.text.strip()
    msg = bot.send_message(message.chat.id, "Укажи свой стек технологий или специальность:\n*(Например: Python, Django, SQL)*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_stack, full_name)

def process_stack(message, full_name):
    tech_stack = message.text.strip()
    msg = bot.send_message(message.chat.id, "Какая у тебя главная цель на митапе?\n*(Например: Найти работу, найти проект, нетворкинг)*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_goal, full_name, tech_stack)

def process_goal(message, full_name, tech_stack):
    goal = message.text.strip()
    username = message.from_user.username or "без_юзернейма"
    
    database.save_participant(message.from_user.id, username, full_name, tech_stack, goal)
    
    bot.send_message(
        message.chat.id, 
        "✅ **Анкета успешно сохранена!**\nТеперь тебе доступен QR-код билета и нетворкинг.",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "🎟 Мой билет (QR-код)")
def send_qr_ticket(message):
    user = database.get_participant(message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, "⚠️ Сначала заполни анкету, нажав **«📝 Заполнить/Изменить анкету»**.", parse_mode="Markdown")
        return

    user_id, _, full_name, tech_stack, _ = user
    
    qr_data = f"MEETUP_TICKET|ID:{user_id}|NAME:{full_name}"
    
    qr_img = qrcode.make(qr_data)
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    caption = (
        f"🎟 **Электронный билет на митап**\n\n"
        f"👤 **Участник:** {full_name}\n"
        f"💻 **Стек:** {tech_stack}\n"
        f"🆔 **ID билета:** `{user_id}`\n\n"
        f"_Покажи этот QR-код на входе для сканирования._"
    )
    
    bot.send_photo(message.chat.id, photo=img_buffer, caption=caption, parse_mode="Markdown")


@bot.message_handler(func=lambda msg: msg.text == "🤝 Найти собеседника")
def find_partner(message):
    user = database.get_participant(message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, "⚠️ Сначала заполни анкету, чтобы другие участники тоже могли узнать о тебе!", parse_mode="Markdown")
        return

    partner = database.get_random_partner(message.from_user.id)
    if not partner:
        bot.send_message(message.chat.id, "😔 Похоже, пока нет других зарегистрированных участников. Попробуй чуть позже!")
        return

    _, partner_username, partner_name, partner_stack, partner_goal = partner
    
    contact_info = f"@{partner_username}" if partner_username != "без_юзернейма" else "Юзернейм не указан"
    
    text = (
        f"🎯 **Собеседник найден!**\n\n"
        f"👤 **Имя:** {partner_name}\n"
        f"💻 **Стек:** {partner_stack}\n"
        f"🎯 **Цель:** {partner_goal}\n"
        f"💬 **Контакт:** {contact_info}\n\n"
        f"Напиши прямо сейчас и предложи выпить кофе во время перерыва! ☕️"
    )
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == '__main__':
    print("Бот IT-митапа запущен...")
    bot.infinity_polling()