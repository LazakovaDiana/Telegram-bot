import telebot
import logging
from telebot import types

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = '7628002072:AAEAGCml8FjnYhyZ28fsLooOHBxeURRqKlU'  # Замените на ваш токен
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения задач и отзывов
tasks = {}
feedbacks = {}

# Список членов команды (замените на реальные chat_id)
team_members = ['2017269192', '6333621563']  # Добавьте сюда chat_id членов команды
project_manager_chat_id = '1319913577'  # Замените на реальный chat_id проектного менеджера


# Функция для создания главного меню
def create_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Добавить задачу"))
    keyboard.add(types.KeyboardButton("Обновить статус задачи"))
    keyboard.add(types.KeyboardButton("Собрать обратную связь"))
    return keyboard


@bot.message_handler(commands=['start'])
def start_message(message):
    """Обрабатывает команду /start и отправляет приветственное сообщение."""
    bot.send_message(message.chat.id, "Привет! Я бот для управления проектами.", reply_markup=create_main_menu())


@bot.message_handler(func=lambda message: message.text == "Добавить задачу")
def prompt_add_task(message):
    """Запрашивает у пользователя ввод новой задачи."""
    bot.send_message(message.chat.id, "Введите задачу:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_task)


def save_task(message):
    """Сохраняет новую задачу и уведомляет проектного менеджера."""
    task = message.text
    tasks[message.chat.id] = tasks.get(message.chat.id, []) + [task]

    # Подтверждение получения запроса
    bot.send_message(message.chat.id, f"Запрос на новую задачу '{task}' принят!", reply_markup=create_main_menu())

    # Уведомление проектного менеджера о новом запросе
    notify_project_manager(task)


def notify_project_manager(task):
    """Уведомляет проектного менеджера о новой задаче."""
    bot.send_message(project_manager_chat_id, f"Новая задача: {task}")


@bot.message_handler(func=lambda message: message.text == "Обновить статус задачи")
def prompt_update_status(message):
    """Запрашивает у пользователя номер задачи для обновления статуса."""
    user_tasks = tasks.get(message.chat.id, [])

    if not user_tasks:
        bot.send_message(message.chat.id, "У вас нет задач для обновления.", reply_markup=create_main_menu())
        return

    # Показать все существующие задачи
    tasks_list = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(user_tasks)])
    bot.send_message(message.chat.id,
                     f"Ваши текущие задачи:\n{tasks_list}\nВведите номер задачи для обновления статуса:",
                     reply_markup=types.ReplyKeyboardRemove())

    bot.register_next_step_handler(message, update_status)


def update_status(message):
    """Обновляет статус задачи и уведомляет членов команды."""
    try:
        task_index = int(message.text) - 1  # Получаем индекс задачи из введенного номера
        user_tasks = tasks.get(message.chat.id, [])

        if task_index < 0 or task_index >= len(user_tasks):
            raise ValueError("Неверный номер задачи.")

        task_completed = f"Задача '{user_tasks[task_index]}' завершена."

        # Уведомление всех членов команды и проектного менеджера о завершении задачи
        for member in team_members:
            bot.send_message(member, task_completed)

        bot.send_message(project_manager_chat_id, task_completed)
        bot.send_message(message.chat.id,
                         f"Статус задачи '{user_tasks[task_index]}' обновлен. Уведомлены все члены команды.",
                         reply_markup=create_main_menu())

        # Удаляем завершенную задачу из списка
        del user_tasks[task_index]
        tasks[message.chat.id] = user_tasks

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер задачи.",
                         reply_markup=create_main_menu())


@bot.message_handler(func=lambda message: message.text == "Собрать обратную связь")
def collect_feedback(message):
    """Запрашивает обратную связь от членов команды."""
    logging.info("Запрос на сбор обратной связи отправлен.")

    for member in team_members:
        bot.send_message(member, "Пожалуйста, дайте обратную связь по завершению этапа выполнения задачи.")

    bot.send_message(message.chat.id, "Обратная связь собирается. Пожалуйста, ожидайте.",
                     reply_markup=create_main_menu())


@bot.message_handler(func=lambda m: m.chat.id in team_members)
def handle_feedback(feedback_message):
    """Обрабатывает отзывы от членов команды."""
    logging.info(f"Получен отзыв от {feedback_message.chat.id}: {feedback_message.text}")

    feedbacks[feedback_message.chat.id] = feedback_message.text
    bot.send_message(feedback_message.chat.id, "Спасибо за ваш отзыв!")

    # Проверка на количество собранных отзывов
    if len(feedbacks) == len(team_members):
        feedback_summary = "\n".join([f"От {member}: {feedbacks[member]}" for member in feedbacks])
        bot.send_message(project_manager_chat_id, f"Собранные отзывы:\n{feedback_summary}")
        feedbacks.clear()


@bot.message_handler(func=lambda message: True)
def handle_unrecognized_message(message):
    """Обрабатывает неизвестные сообщения."""
    logging.info(f"Неизвестное сообщение от {message.chat.id}: {message.text}")
    bot.send_message(message.chat.id, "Пожалуйста, выберите действие из меню.", reply_markup=create_main_menu())


if __name__ == "__main__":
    logging.info("Бот запущен.")
    bot.polling()