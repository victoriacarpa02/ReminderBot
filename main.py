import telebot
import sqlite3
from telebot import types
import hashlib


bot = telebot.TeleBot('your_token')

uname = None
user_info = {}
tasks = ''


@bot.message_handler(commands=['start'])
def start(message):
    # connect with databases
    db_connection = sqlite3.connect('tasks.sql')
    cur = db_connection.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT,
        chat_id TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        reminder TEXT,
        description TEXT,
        remind_at TEXT, 
        notification_sent INTEGER DEFAULT 0,
        FOREIGN KEY (username) REFERENCES users(username)
    )
    ''')
    db_connection.commit()
    cur.close()
    db_connection.close()

    bot.send_message(message.chat.id, '<b>Hello!</b>\n\nWelcome to the <b>Reminder</b>! Let\'s start our '
                                'work.\nChoose an option below: ', parse_mode='html', reply_markup=create_keyboard())
    bot.register_next_step_handler(message, options)


def options(message):
    if message.text == 'Sign in':
        bot.send_message(message.chat.id, 'Enter your username (must be unique) and password separated by space: ')
        bot.register_next_step_handler(message, add_user)
    elif message.text == 'Log in':
        bot.send_message(message.chat.id, 'Enter your username and password separated by space: ')
        bot.register_next_step_handler(message, verify_user)
    else:
        bot.send_message(message.chat.id, 'Please choose a valid option')
        bot.register_next_step_handler(message, options)


def add_user(message):
    global uname
    keyboard = create_actions_keyboard()
    try:
        uname, password = message.text.split()
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
    except ValueError:
        bot.send_message(message.chat.id, 'Please enter your username and password separated by a space.')
        bot.register_next_step_handler(message, add_user)
        return

    db_connection = sqlite3.connect('tasks.sql')
    cur = db_connection.cursor()
    try:
        cur.execute('''
        INSERT INTO users (username, password_hash, chat_id)
        VALUES (?, ?, ?)
        ''', (uname, pass_hash, message.chat.id))
        db_connection.commit()
        bot.send_message(message.chat.id, f'User {uname} has been added')
        bot.send_message(message.chat.id, f'Welcome, {uname}! What do you want to do?', reply_markup=keyboard)
        bot.register_next_step_handler(message, actions)
    except sqlite3.IntegrityError:
        bot.send_message(message.chat.id, f'User {uname} already exists. Please enter a different username.')
        bot.register_next_step_handler(message, add_user)
    finally:
        cur.close()
        db_connection.close()


def verify_user(message):
    global uname
    keyboard = create_actions_keyboard()
    try:
        uname, password = message.text.split()
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
    except ValueError:
        bot.send_message(message.chat.id, 'Please enter your username and password separated by a space.')
        bot.register_next_step_handler(message, verify_user)
        return

    db_connection = sqlite3.connect('tasks.sql')
    cur = db_connection.cursor()
    try:
        cur.execute('SELECT password_hash FROM users WHERE username = ?', (uname,))
        row = cur.fetchone()
        if row is None or row[0] != pass_hash:
            raise ValueError
        bot.send_message(message.chat.id, f'Welcome back, {uname}!\nWhat do you want to do?', reply_markup=keyboard)
        bot.register_next_step_handler(message, actions)
    except ValueError:
        bot.send_message(message.chat.id, 'User not found or incorrect password')
        bot.register_next_step_handler(message, options)
    finally:
        cur.close()
        db_connection.close()


def create_actions_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Add a reminder')
    button2 = types.KeyboardButton('Check all tasks')
    button3 = types.KeyboardButton('Delete a task')
    button4 = types.KeyboardButton('Exit')
    keyboard.add(button1, button2)
    keyboard.add(button3, button4)
    return keyboard


def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Sign in')
    btn2 = types.KeyboardButton('Log in')
    keyboard.row(btn1, btn2)
    return keyboard


@bot.message_handler(func=lambda callback: True)
def actions(message):
    global tasks
    keyboard = create_actions_keyboard()
    if message.text == 'Add a reminder':
        bot.send_message(message.chat.id, 'Give the reminder a title:')
        bot.register_next_step_handler(message, set_title)
    elif message.text == 'Check all tasks':
        tasks = print_tasks()
        bot.send_message(message.chat.id, f'<b>Here is all your tasks: </b>\n{tasks}', parse_mode='html',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, actions)
    elif message.text == 'Exit':
        bot.send_message(message.chat.id, 'OK, bye!\nType /start to continue')
        bot.register_next_step_handler(message, start)
    elif message.text == 'Delete a task':
        bot.send_message(message.chat.id, 'What specific task do you want to delete?\n(Type a number)')
        tasks = print_tasks()
        bot.send_message(message.chat.id, f'{tasks}')
        bot.register_next_step_handler(message, delete_task)
    else:
        bot.send_message(message.chat.id, 'Invalid action. Choose one option below:', reply_markup=keyboard)
        bot.register_next_step_handler(message, actions)


def print_tasks():
    db_connection = sqlite3.connect('tasks.sql')
    cur = db_connection.cursor()
    cur.execute('SELECT * FROM tasks WHERE username = ?', (uname,))
    info = cur.fetchall()
    if info:
        result = ''
        for el in info:
            result += f'{el[0]}. {el[2]}\n{el[3]}\nRemind at: {el[4]}\n'
    else:
        result = 'No tasks yet'
    cur.close()
    db_connection.close()
    return result


def delete_task(message):
    keyboard = create_actions_keyboard()
    db_connection = sqlite3.connect('tasks.sql')
    cur = db_connection.cursor()
    cur.execute('DELETE FROM tasks WHERE id = ?', (message.text,))
    db_connection.commit()
    bot.send_message(message.chat.id, 'Task has been successfully deleted!', reply_markup=keyboard)
    bot.register_next_step_handler(message, actions)


def set_title(message):
    global user_info
    user_info['title'] = message.text
    bot.send_message(message.chat.id, 'Give the reminder a description:')
    bot.register_next_step_handler(message, set_description)


def set_description(message):
    global user_info
    user_info['description'] = message.text
    bot.send_message(message.chat.id, 'Set a time and a date\n<i>Example: 2024-07-11 12:00</i>', parse_mode='html')
    bot.register_next_step_handler(message, set_timedate)


def set_timedate(message):
    global user_info
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Yes')
    btn2 = types.KeyboardButton('No')
    markup.row(btn1, btn2)

    user_info['remind_at'] = message.text
    bot.send_message(message.chat.id, f'Let\'s check!\n<b>{user_info["title"]}</b>\n'
                                      f'{user_info["description"]}\nRemind at {user_info["remind_at"]}\nCorrect?',
                     parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, is_correct)


def is_correct(message):
    keyboard = create_actions_keyboard()
    db_connection = sqlite3.connect('tasks.sql')
    cur = db_connection.cursor()
    if message.text == 'Yes':
        cur.execute('''
                        INSERT INTO tasks (username, reminder, description, remind_at)
                        VALUES (?, ?, ?, ?)
                        ''', (uname, user_info['title'], user_info['description'], user_info['remind_at']))
        db_connection.commit()
        bot.send_message(message.chat.id, 'Reminder has been added successfully!', reply_markup=keyboard)
        bot.register_next_step_handler(message, actions)
    elif message.text == 'No':
        bot.send_message(message.chat.id, 'Ok. What do you want to do?', reply_markup=keyboard)
        bot.register_next_step_handler(message, actions)
    else:
        bot.send_message(message.chat.id, 'Invalid action. Answer Yes or No')
        bot.register_next_step_handler(message, is_correct)


bot.polling(none_stop=True)
