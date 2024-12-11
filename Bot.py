import telebot
import time

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot_token = '8181858011:AAFtFMwUVPKWkVWyAz4vf-aN-SWVXRDMpAo'
bot = telebot.TeleBot(bot_token)

# Словарь для хранения задач
tasks = {}
task_id_counter = 1  # Счетчик для уникальных ID задач
manager_chat_id = None  # ID менеджера, куда будут отправляться отчеты


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать в бот управления проектами! Используйте /help для получения списка команд.")


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "/add_task <задача> - Добавить новую задачу\n"
        "/assign_task <ID> <исполнитель> - Назначить исполнителя на задачу по ID\n"
        "/assign_executor <ID> <исполнитель_id> - Назначить исполнителя по его ID на задачу\n"
        "/view_tasks - Просмотреть все задачи\n"
        "/complete_task <ID> - Завершить задачу по ID и отправить отчет менеджеру\n"
        "/delete_task <ID> - Удалить задачу по ID\n"
        "/clear_tasks - Очистить все задачи\n"
        "/set_manager <ID> - Установить ID менеджера для получения отчетов\n"
    )
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['add_task'])
def add_task(message):
    global task_id_counter
    try:
        task_text = message.text.split('/add_task ', 1)[1]
        tasks[task_id_counter] = {'text': task_text, 'status': 'pending', 'assignee': None}
        bot.send_message(message.chat.id, f"Задача добавлена: {task_text} (ID: {task_id_counter})")
        task_id_counter += 1  # Увеличиваем счетчик ID задач
    except IndexError:
        bot.send_message(message.chat.id, "Пожалуйста, укажите текст задачи после команды /add_task.")


@bot.message_handler(commands=['assign_task'])
def assign_task(message):
    try:
        parts = message.text.split()
        task_id = int(parts[1])
        assignee = ' '.join(parts[2:])

        if task_id in tasks:
            tasks[task_id]['assignee'] = assignee
            bot.send_message(message.chat.id, f"Исполнитель {assignee} назначен на задачу ID: {task_id}.")
        else:
            bot.send_message(message.chat.id, "Задача с таким ID не найдена.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id,
                         "Пожалуйста, укажите корректный ID задачи и имя исполнителя после команды /assign_task.")


@bot.message_handler(commands=['assign_executor'])
def assign_executor(message):
    try:
        parts = message.text.split()
        task_id = int(parts[1])
        executor_id = int(parts[2])  # Предполагаем, что исполнитель имеет уникальный ID

        # Здесь вы можете добавить логику для проверки существования исполнителя по executor_id,
        # например, если у вас есть отдельный словарь исполнителей.

        if task_id in tasks:
            tasks[task_id]['assignee'] = f"Исполнитель с ID: {executor_id}"
            bot.send_message(message.chat.id, f"Исполнитель с ID: {executor_id} назначен на задачу ID: {task_id}.")
        else:
            bot.send_message(message.chat.id, "Задача с таким ID не найдена.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id,
                         "Пожалуйста, укажите корректный ID задачи и ID исполнителя после команды /assign_executor.")


@bot.message_handler(commands=['view_tasks'])
def view_tasks(message):
    if tasks:
        task_list = "\n".join(
            f"ID: {task_id}, Задача: {task['text']}, Статус: {task['status']}, Исполнитель: {task['assignee'] if task['assignee'] else 'не назначен'}"
            for task_id, task in tasks.items())
        bot.send_message(message.chat.id, f"Список задач:\n{task_list}")
    else:
        bot.send_message(message.chat.id, "Нет активных задач.")


@bot.message_handler(commands=['complete_task'])
def complete_task(message):
    try:
        task_id = int(message.text.split('/complete_task ', 1)[1])
        if task_id in tasks:
            tasks[task_id]['status'] = 'completed'
            assignee = tasks[task_id]['assignee'] if tasks[task_id]['assignee'] else "неизвестный исполнитель"
            report = f"Задача ID: {task_id} выполнена исполнителем {assignee}.\nОписание задачи: {tasks[task_id]['text']}"

            # Отправка отчета менеджеру, если его ID установлен
            if manager_chat_id:
                bot.send_message(manager_chat_id, report)

            bot.send_message(message.chat.id, f"Задача ID: {task_id} помечена как выполненная.")
        else:
            bot.send_message(message.chat.id, "Задача с таким ID не найдена.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Пожалуйста, укажите корректный ID задачи после команды /complete_task.")


@bot.message_handler(commands=['delete_task'])
def delete_task(message):
    try:
        task_id = int(message.text.split('/delete_task ', 1)[1])
        if task_id in tasks:
            del tasks[task_id]
            bot.send_message(message.chat.id, f"Задача ID: {task_id} удалена.")
        else:
            bot.send_message(message.chat.id, "Задача с таким ID не найдена.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Пожалуйста, укажите корректный ID задачи после команды /delete_task.")


@bot.message_handler(commands=['clear_tasks'])
def clear_tasks(message):
    tasks.clear()
    global task_id_counter
    task_id_counter = 1  # Сброс счетчика ID задач
    bot.send_message(message.chat.id, "Все задачи были очищены.")


@bot.message_handler(commands=['set_manager'])
def set_manager(message):
    global manager_chat_id
    try:
        manager_chat_id = int(message.text.split('/set_manager ', 1)[1])
        bot.send_message(message.chat.id, f"Менеджер установлен с ID: {manager_chat_id}.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Пожалуйста, укажите корректный ID менеджера после команды /set_manager.")


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)
