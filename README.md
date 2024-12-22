# tele_printerBot

This project allows you to update and check printer statuses in a school environment using a Telegram bot.

## Getting Started

Follow these steps to set up and run the bot:

1. Clone the Project: Clone the repository to your local machine

```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a Virtual Environment: Create a Python virtual environment to manage dependencies

```bash
python3 -m venv venv/
```

Activate the virtual environment:

On macOS/Linux: `source venv/bin/activate`

On Windows: `venv\Scripts\activate`

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Create Telegram token

Search for @botfather in Telegram and create a token. Update the token variable under .env file

```bash
export BOT_TOKEN="apitoken here"
```

## Available Commands

Once the bot is running, you can use the following commands:

- /start: Initializes the bot and lists available commands.
- /help: Displays a list of available commands with descriptions.
- /status: Displays the current status of all printers (e.g., working or down).
- /update: Updates the status of a printer.

## Bot Behavior and Logic

- /update: Updates the printer status. If the printer is marked as "down," the global down counter will be incremented by 1. Users can also leave a comment along with the status update.
