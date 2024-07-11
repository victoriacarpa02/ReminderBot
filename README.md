# Reminder Bot

## Overview
The Reminder Bot is a Telegram bot designed to help users manage their tasks and reminders. Users can sign up, log in, and add reminders with specific titles, descriptions, and notification times. The bot also allows users to view all their tasks and delete specific tasks.

## Features
- User Authentication: Users can sign in or log in with a unique username and password.
- Task Management: Users can add, view, and delete tasks.
- Persistent Storage: User information and tasks are stored in an SQLite database.

## Technologies Used
- Python
- Telebot (Python Telegram Bot API)
- SQLite3
- Hashlib (for password hashing)

## Setup
1. Clone the repository:
```
git clone <repository_url>
cd <repository_directory>
```
2. Install required packages:
```
pip install pyTelegramBotAPI
```
3. Create and configure the SQLite database: The database is automatically created and configured when the bot is 
   started for the first time.
4. Update the bot token: Replace 'YOUR_BOT_TOKEN_HERE' in the code with your actual Telegram bot token.

## Running the Bot
Run the bot script:
```
python bot.py
```
The bot will start polling for messages.

## Bot Functions
### /start

**Description**: Initializes the bot and sets up the SQLite database.

**How it works**: The function creates the necessary tables if they do not exist and then prompts the user to sign in or log in.

### options
**Description**: Handles the user's choice to sign in or log in.
    
**How it works**: Prompts the user to enter their username and password, then directs them to the appropriate function (add_user or verify_user).

### add_user
**Description**: Registers a new user.
    
**How it works**: Takes the user's input (username and password), hashes the password, and stores the user in the database. If the username already exists, prompts the user to choose a different username.

### verify_user
**Description**: Logs in an existing user.

**How it works**: Takes the user's input (username and password), hashes the password, and checks the database for a matching record. If successful, logs the user in.

### create_actions_keyboard
**Description**: Creates a keyboard with options for task management.
   
**How it works**: Returns a keyboard with buttons for adding a reminder, checking all tasks, deleting a task, and exiting.

### actions
**Description**: Handles user actions after logging in.
    
**How it works**: Responds to user inputs to add a reminder, check tasks, delete a task, or exit. Directs the user to the appropriate function based on their choice.

### print_tasks
**Description**: Retrieves and displays all tasks for the logged-in user.
    
**How it works**: Queries the database for tasks associated with the logged-in user and formats them for display. Currently, tasks are displayed with their database ID instead of a sequential number.

### delete_task
**Description**: Deletes a specified task.

**How it works**: Takes the task ID input from the user and deletes the corresponding task from the database.

### set_title
**Description**: Sets the title for a new reminder.

**How it works**: Stores the user's input as the reminder title and prompts for a description.

### set_description
**Description**: Sets the description for a new reminder.

**How it works**: Stores the user's input as the reminder description and prompts for the time and date.

### set_timedate
**Description**: Sets the time and date for a new reminder.

**How it works**: Stores the user's input as the reminder time and date and asks for confirmation.

### is_correct
**Description**: Confirms the reminder details.

**How it works**: If the user confirms, stores the reminder in the database. If not, returns to the action selection.

## Current Limitations and Future Work
- Reminder Notifications: The reminder notification feature is not yet implemented.
- Task Display: Tasks are displayed with their database ID instead of a sequential number.

## Contributing
Feel free to fork the repository and make contributions. Pull requests are welcome.

### Note: This application is currently under development. Some features might not work as expected. 
