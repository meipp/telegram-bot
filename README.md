# telegram-bot
Modular telegram bot with support for self updating messages

## How to run
You need a Telegram bot token from [@BotFather](https://t.me/BotFather).
Then you can start the bot by running
```bash
API_TOKEN=$YOUR_BOT_TOKEN python main.py
```

## Modules
You can enable/disable module by commenting out the import statements in `main.py`.
```python
# Disabled modules
# import modules.deepl
# import modules.exec

# Enabled modules
import modules.plots
import modules.tables
```
