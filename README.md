# Telegram Ads Hub Bot

A multi-niche Telegram bot for content delivery across Crypto, Brazil News, Sports, Banking, Storytelling, and Marketplace.

## Features
- 6 content niches with 8 topics each (48+ total topics)
- User preferences management
- Daily content delivery
- Reading history tracking
- 100% Telegram Ads friendly
- No third-party API keys required

## Deployment

### 1. Create a Bot on Telegram
- Message @BotFather
- Create a new bot with `/newbot`
- Copy your BOT_TOKEN

### 2. Deploy on Railway
1. Push code to GitHub
2. Connect repository to Railway
3. Add environment variable: `BOT_TOKEN=your_bot_token`
4. Deploy!

### 3. Deploy on GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/telegram-ads-bot.git
git push -u origin main
