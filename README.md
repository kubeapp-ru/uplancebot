# Uplancebot official chatbot
Telegram bot for job notifications

Add me in telegram: [Uplancebot]

Set a feed url -> Get a messages with new jobs

## How to start own chatbot

### Prerequisites 
  
- docker
- docker-compose

### Deploy 

1. Clone repo
2. Copy `bot.env.sample` to `bot.env` 
3. Change `BOT_TOKEN` in that file to your chat bot token (create new chatbot from @BotFather)
4. Add your chat_id into `ADMINS` list. (Get chat_id from @userinfobot)
5. Run from repo: `docker-compose up -d`
6. Check chatbot logs that it's working `docker-compose logs uplancebot`

Here is example of logs:

```
🤖  Running in debug mode with live reloading
    (don't forget to disable it for production)
    (watching /opt/bot)
```


### Chatbot Commands

- /start - Start bot
- /add - Add new RSS feed
- /list - List all RSS feeds
- /delete - Delete RSS feed
- /period - Change period for updates
- /upwork_status_on - Enable Upwork website status
- /upwork_status_off - Disable Upwork website status
- /help - Get help
- /stop - Stop bot


Follow for updates in twitter: [@uplancebot]

[@uplancebot]:https://twitter.com/uplancebot
[Uplancebot]:https://t.me/uplancebot
