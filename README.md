# Telegram Channel Tracker Bot

This is a Telegram bot that allows users to track and manage a list of channels. The bot has several features, including the ability to add and remove channels, track channels for a specific period of time, and list all the channels that are currently being tracked.

## Features

* Add and remove channels to the list of channels to track
* Track channels for a specific period of time (1 day, 1 week, 1 hour, or 2 hours)
* List all the channels that are currently being tracked
* Send messages from the tracked channels to the user
* Cache messages to improve performance

## Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/telegram-channel-tracker-bot.git
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Create a new Telegram bot using the BotFather bot on Telegram.

4. Replace the `api_id`, `api_hash`, and `bot_token` variables in the code with your own API ID, API hash, and bot token.

## Usage

1. Run the bot:

```
python singletone.py
```

2. Start the bot on Telegram by searching for it by its username or by clicking on the following link: [https://t.me/your_bot_username](https://t.me/your_bot_username)

3. Use the bot's commands to add, remove, and track channels, and to list the channels that are currently being tracked.

## Caching

The bot uses a simple caching mechanism to improve performance. When a user requests messages from a channel for a specific period of time, the bot first checks if the messages are already in the cache. If the messages are in the cache, the bot returns them immediately. If the messages are not in the cache, the bot fetches the messages, stores them in the cache, and returns them.

The cache is implemented using a dictionary, where the keys are tuples containing the channel name and the period of time, and the values are lists of messages.

## Contributing

Contributions are welcome! If you find any bugs or have any suggestions for new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
