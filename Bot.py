import telebot
from telebot import types

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot_token = '8181858011:AAFtFMwUVPKWkVWyAz4vf-aN-SWVXRDMpAo'
bot = telebot.TeleBot(bot_token)

# URL дашборда
DASHBOARD_URL = 'http://127.0.0.1:8050/'

# Словарь для хранения задач
tasks = {}
task_id_counter = 1  # Счетчик для уникальных ID задач
manager_chat_id = None  # ID менеджера, куда будут отправляться отчеты
executors = {}  # Словарь для хранения исполнителей и их chat_id


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в бот управления проектами!")
    main_menu(message.chat.id)


def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🈺Добавить задачу🈺"),
        types.KeyboardButton("📜Просмотреть задачи📜"),
        types.KeyboardButton("✔️Завершить задачу✔️"),
        types.KeyboardButton("Назначить исполнителя"),
        types.KeyboardButton("Удалить задачу"),
        types.KeyboardButton("Очистить задачи"),
        types.KeyboardButton("Установить менеджера"),
        types.KeyboardButton("Зарегистрировать исполнителя"),
        types.KeyboardButton("📋Просмотреть исполнителей📋"),
        types.KeyboardButton("ПВЗ"),
    )
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Очистить задачи")
def delete_all_tasks(message):
    global tasks  # Объявляем, что мы будем использовать глобальную переменную
    tasks.clear()  # Очищаем словарь с задачами
    bot.send_message(message.chat.id, "Все задачи успешно удалены.")
    main_menu(message.chat.id)


# Просмотр дашборда
@bot.message_handler(func=lambda message: message.text == "ПВЗ")
def message_pvz(message):
    if message.chat.id != manager_chat_id:
        bot.send_message(message.chat.id, "Только менеджер может просматривать ПВЗ.")
        main_menu(message.chat.id)
        return
    else:
        # Отправка текста и изображений
        bot.send_message(message.chat.id, "Процент выполненных задач:")

        image_paths = [
            'задача А.PNG',
            'задача Б.PNG',
            'задача В.PNG'
        ]

        for image_path in image_paths:
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)

        markup = types.InlineKeyboardMarkup()
        pvz = types.InlineKeyboardButton('Посмотреть дашборд', url=DASHBOARD_URL)
        markup.row(pvz)
        bot.send_message(message.chat.id, 'Тыкай👇', parse_mode='html', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Удалить задачу")
def delete_task(message):
    bot.send_message(message.chat.id, "Введите ID задачи для удаления:")
    bot.register_next_step_handler(message, process_delete_task)


def process_delete_task(message):
    try:
        task_id = int(message.text)
        if task_id in tasks:
            del tasks[task_id]
            bot.send_message(message.chat.id, f"Задача ID: {task_id} успешно удалена.")
        else:
            bot.send_message(message.chat.id, "Задача с таким ID не найдена.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID задачи.")

    main_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "🈺Добавить задачу🈺")
def add_task(message):
    if message.chat.id != manager_chat_id:
        bot.send_message(message.chat.id, "Только менеджер может добавалять задачи.")
        main_menu(message.chat.id)
        return
    else:
        bot.send_message(message.chat.id, "Введите текст задачи:")
        bot.register_next_step_handler(message, process_add_task)


def process_add_task(message):
    global task_id_counter
    task_text = message.text
    tasks[task_id_counter] = {'text': task_text, 'status': 'назначена', 'assignee': None}
    bot.send_message(message.chat.id, f"Задача добавлена: {task_text} (ID: {task_id_counter})")
    task_id_counter += 1
    main_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "📜Просмотреть задачи📜")
def view_tasks(message):
    if tasks:
        task_list = "\n".join(
            f"ID: {task_id}, Задача: {task['text']}, Статус: {task['status']}, Исполнитель: {task['assignee'] if task['assignee'] else 'не назначен'}"
            for task_id, task in tasks.items())
        bot.send_message(message.chat.id, f"Список задач:\n{task_list}")
    else:
        bot.send_message(message.chat.id, "Нет активных задач.")
    main_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "✔️Завершить задачу✔️")
def complete_task(message):
    bot.send_message(message.chat.id, "Введите ID задачи для завершения:")
    bot.register_next_step_handler(message, process_complete_task)


@bot.message_handler(func=lambda message: message.text == "Установить менеджера")
def set_manager(message):
    bot.send_message(message.chat.id, "Введите ID менеджера:")
    bot.register_next_step_handler(message, process_set_manager)


def process_set_manager(message):
    global manager_chat_id
    try:
        manager_chat_id = int(message.text)
        bot.send_message(message.chat.id, f"Менеджер установлен с ID: {manager_chat_id}.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID менеджера.")

    main_menu(message.chat.id)


def process_complete_task(message):
    try:
        task_id = int(message.text)
        if task_id in tasks:
            tasks[task_id]['status'] = 'выполнено'
            assignee = tasks[task_id]['assignee'] if tasks[task_id]['assignee'] else "неизвестный исполнитель"
            report = f"Задача ID: {task_id} выполнена исполнителем {assignee}.\nОписание задачи: {tasks[task_id]['text']}"

            # Отправка отчета менеджеру, если его ID установлен
            if manager_chat_id:
                bot.send_message(manager_chat_id, report)

            bot.send_message(message.chat.id, f"Задача ID: {task_id} помечена как выполненная.")
        else:
            bot.send_message(message.chat.id, "Задача с таким ID не найдена.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID задачи.")

    main_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "Назначить исполнителя")
def assign_task(message):
    if message.chat.id != manager_chat_id:
        bot.send_message(message.chat.id, "Только менеджер может назначать исполнителей на задачи.")
        main_menu(message.chat.id)
        return

    if not tasks:
        bot.send_message(message.chat.id, "Нет доступных задач для назначения исполнителей.")
        main_menu(message.chat.id)
        return

    bot.send_message(message.chat.id, "Введите ID задачи для назначения исполнителя:")
    bot.register_next_step_handler(message, process_assign_task)


def process_assign_task(message):
    try:
        task_id = int(message.text)
        if task_id in tasks:
            # Отправляем список исполнителей
            executor_list = "\n".join(f"ID: {executor_id} - {username}" for executor_id, username in executors.items())
            if executor_list:
                bot.send_message(message.chat.id, f"Выберите исполнителя:\n{executor_list}\nВведите ID исполнителя:")
                bot.register_next_step_handler(message, lambda m: assign_executor(m, task_id))
            else:
                bot.send_message(message.chat.id, "Нет зарегистрированных исполнителей.")
                main_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Задача с таким ID не найдена.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID задачи.")


def assign_executor(message, task_id):
    executor_id = message.text.strip()

    # Проверка на наличие исполнителя в зарегистрированных
    if executor_id in executors:
        tasks[task_id]['assignee'] = executor_id
        bot.send_message(message.chat.id, f"Исполнитель с ID {executor_id} назначен на задачу ID {task_id}.")
    else:
        bot.send_message(message.chat.id, "Исполнитель с таким ID не найден. Пожалуйста, выберите из списка.")

    main_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "Зарегистрировать исполнителя")
def register_executor(message):
    bot.send_message(message.chat.id, "Введите ваш Telegram ID для регистрации:")
    bot.register_next_step_handler(message, process_register_executor)


def process_register_executor(message):
    executor_id = message.text.strip()

    # Регистрация исполнителя
    if executor_id not in executors.values():
        executors[message.from_user.username] = executor_id
        bot.send_message(message.chat.id, f"Исполнитель с ID {executor_id} зарегистрирован.")
    else:
        bot.send_message(message.chat.id, "Этот исполнитель уже зарегистрирован.")

    main_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "📋Просмотреть исполнителей📋")
def view_executors(message):
    if executors:
        executor_list = "\n".join(
            f"Имя пользователя: {username}, ID: {executor_id}" for username, executor_id in executors.items())
        bot.send_message(message.chat.id, f"Список зарегистрированных исполнителей:\n{executor_list}")
    else:
        bot.send_message(message.chat.id, "Нет зарегистрированных исполнителей.")

    main_menu(message.chat.id)


# Запуск бота
bot.polling(none_stop=True)
