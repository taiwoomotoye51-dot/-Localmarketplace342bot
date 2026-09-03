#!/usr/bin/env python3
"""
Telegram Ads Bot - Unified Hub for All Niches
No third-party API keys required - Fully Telegram Ads friendly
"""

import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User data storage (in-memory - for production use a database)
user_preferences = {}
user_content_history = {}

# Content database for each niche
CONTENT = {
    "crypto": {
        "title": "💰 Crypto & Fintech",
        "items": [
            "📊 Bitcoin dominance at 52% - market consolidation continues",
            "🔐 New hardware wallet released with biometric security",
            "📈 Ethereum Layer 2 solutions surpass 10M daily transactions",
            "💎 Stablecoin market cap reaches $180B - new milestone",
            "🏦 5 digital banks now offer direct crypto purchases in Brazil",
            "📰 SEC approves 3 new crypto ETFs - institutional adoption grows",
            "🚀 TON ecosystem adds 50 new mini-apps this quarter",
            "🔒 DeFi insurance protocols see 300% growth in 2026"
        ]
    },
    "brazil": {
        "title": "🇧🇷 Brazil News & Culture",
        "items": [
            "🏢 São Paulo tech hub adds 200+ new startups in Q2 2026",
            "🎵 Brazilian music exports reach record $500M in 2026",
            "🍽️ 15 new Michelin-starred restaurants open in Rio",
            "⚽ Transfer window: 3 Brazilian stars join European clubs",
            "🌳 Amazon deforestation rate drops 25% - new conservation data",
            "📱 Pix hits 1B daily transactions - new fintech milestone",
            "🎭 Rio Carnival expected to generate $2B in tourism",
            "📈 Brazil GDP growth at 3.8% - emerging market leader"
        ]
    },
    "sports": {
        "title": "⚽ Portuguese Sports",
        "items": [
            "🇵🇹 Primeira Liga: Porto leads by 5 points at the break",
            "🌟 Rising star: 17yo Portuguese forward signs with Real Madrid",
            "🏆 Portuguese futsal team wins European Championship",
            "⚽ Ronaldo adds 2 goals to his record-breaking tally",
            "📊 Sporting CP sets new possession record - 78% in latest match",
            "🔴 Benfica secures 4th consecutive youth cup title",
            "🇵🇹 5 Portuguese players named in Champions League Team of the Year",
            "🏟️ New stadium announced for Portuguese football academy"
        ]
    },
    "banking": {
        "title": "💳 Online Banking & Finance",
        "items": [
            "🏦 3 new digital banks launch in Latin America with zero fees",
            "📊 Savings rates hit 4.5% - best returns since 2020",
            "🛡️ Fraud protection: AI-powered tools reduce crime by 40%",
            "📱 Banking app of the year: features and security review",
            "🌍 International transfers now free with 5 online banks",
            "💰 Fintech lending reaches $50B in emerging markets",
            "📈 Stock market: S&P 500 gains 12% in first half of 2026",
            "🏠 Mortgage rates at 5.2% - comparison guide released"
        ]
    },
    "storytelling": {
        "title": "📖 Storytelling & Daily News",
        "items": [
            "🌅 Story of the day: The fisherman who found a lost city",
            "📚 Amazon bestseller: New book explores AI and human creativity",
            "🎬 Director's cut: 5 must-watch films for 2026",
            "🧠 Philosophy: Stoicism tips from modern entrepreneurs",
            "✈️ Travel: The most underrated cities for digital nomads",
            "🍳 Food: Recipes that tell stories from 5 different cultures",
            "🎨 Art: Underground artists gaining global recognition",
            "🌱 Positive news: Ocean plastic reduced by 30% globally"
        ]
    },
    "marketplace": {
        "title": "🛒 Marketplace & Shopping",
        "items": [
            "🛍️ Deal of the day: Top gadget at 40% off - limited time",
            "🎁 Gift guide: Top 10 gifts under $50 for every occasion",
            "👗 Fashion: Sustainable clothing brands at affordable prices",
            "🏠 Home: Smart home deals - save up to 60% on devices",
            "🛒 Marketplace: 1000+ sellers join platform this week",
            "📦 Free shipping day: 50 major brands participate",
            "🎨 Handmade: Artisan marketplace sees 200% growth",
            "💼 Business: Best software deals for 2026 - comparison"
        ]
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user data
    if user_id not in user_preferences:
        user_preferences[user_id] = {
            "niches": list(CONTENT.keys()),
            "last_content": {},
            "subscribed": True
        }
    if user_id not in user_content_history:
        user_content_history[user_id] = []
    
    keyboard = [
        [InlineKeyboardButton("📰 Daily Content", callback_data="daily")],
        [InlineKeyboardButton("⚙️ Preferences", callback_data="preferences")],
        [InlineKeyboardButton("📚 History", callback_data="history")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("❌ Unsubscribe", callback_data="unsubscribe")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Welcome, {user.first_name}!\n\n"
        f"📌 Your all-in-one Telegram Ads Hub!\n"
        f"I provide daily content on:\n"
        f"💰 Crypto • 🇧🇷 Brazil • ⚽ Sports\n"
        f"💳 Banking • 📖 Stories • 🛒 Marketplace\n\n"
        f"✅ No third-party API keys required\n"
        f"✅ 100% Telegram Ads friendly\n\n"
        f"Use the buttons below to get started:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    try:
        if data == "daily":
            await send_daily_content(query, user_id)
        elif data == "preferences":
            await show_preferences(query, user_id)
        elif data == "history":
            await show_history(query, user_id)
        elif data == "about":
            await show_about(query)
        elif data == "unsubscribe":
            await unsubscribe_user(query, user_id)
        elif data.startswith("toggle_"):
            niche = data.replace("toggle_", "")
            await toggle_niche(query, user_id, niche)
        elif data.startswith("content_"):
            niche = data.replace("content_", "")
            await send_niche_content(query, user_id, niche)
        elif data == "back_main":
            await back_to_main(query, user_id)
        elif data == "clear_history":
            await clear_history(query, user_id)
        elif data == "resubscribe":
            await resubscribe_user(query, user_id)
    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        await query.edit_message_text(
            "⚠️ Something went wrong. Please try again."
        )

async def send_daily_content(query, user_id):
    """Send daily content based on user preferences."""
    preferences = user_preferences.get(user_id, {})
    niches = preferences.get("niches", list(CONTENT.keys()))
    
    if not niches:
        await query.edit_message_text(
            "📭 You haven't selected any niches!\n"
            "Go to 'Preferences' to choose your topics.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Preferences", callback_data="preferences")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ])
        )
        return
    
    message = "📰 Your Daily Content Update\n" + "═" * 25 + "\n\n"
    
    import random
    for niche in niches:
        if niche in CONTENT:
            content_list = CONTENT[niche]["items"]
            item = random.choice(content_list)
            message += f"{CONTENT[niche]['title']}\n"
            message += f"└ {item}\n\n"
            
            # Track history
            if user_id in user_content_history:
                user_content_history[user_id].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "niche": niche,
                    "content": item
                })
                # Keep only last 50 items
                if len(user_content_history[user_id]) > 50:
                    user_content_history[user_id] = user_content_history[user_id][-50:]
    
    message += "═" * 25 + "\n"
    message += "📌 Visit 'Preferences' to customize your feed!"
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Preferences", callback_data="preferences")],
        [InlineKeyboardButton("📚 History", callback_data="history")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_preferences(query, user_id):
    """Show and manage user preferences."""
    preferences = user_preferences.get(user_id, {})
    current_niches = preferences.get("niches", list(CONTENT.keys()))
    
    message = "⚙️ **Your Preferences**\n"
    message += "═" * 20 + "\n\n"
    message += "Select which niches you want to see:\n\n"
    
    keyboard = []
    for niche, data in CONTENT.items():
        is_selected = niche in current_niches
        emoji = "✅" if is_selected else "⬜"
        button = InlineKeyboardButton(
            f"{emoji} {data['title']}",
            callback_data=f"toggle_{niche}"
        )
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def toggle_niche(query, user_id, niche):
    """Toggle a niche on/off in user preferences."""
    if user_id not in user_preferences:
        user_preferences[user_id] = {"niches": list(CONTENT.keys())}
    
    preferences = user_preferences[user_id]
    current_niches = preferences.get("niches", [])
    
    if niche in current_niches:
        if len(current_niches) > 1:
            current_niches.remove(niche)
        else:
            await query.answer("⚠️ You must have at least one niche selected!", show_alert=True)
            return
    else:
        current_niches.append(niche)
    
    user_preferences[user_id]["niches"] = current_niches
    await show_preferences(query, user_id)

async def show_history(query, user_id):
    """Show user's content history."""
    history = user_content_history.get(user_id, [])
    
    if not history:
        await query.edit_message_text(
            "📭 You haven't viewed any content yet.\n"
            "Get your daily update to start building your history!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📰 Daily Content", callback_data="daily")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ])
        )
        return
    
    message = "📚 **Your Reading History**\n"
    message += "═" * 20 + "\n\n"
    
    recent_history = history[-10:]
    for entry in reversed(recent_history):
        message += f"📌 *{entry['date']}*\n"
        message += f"└ {entry['content'][:60]}...\n\n"
    
    message += "═" * 20 + "\n"
    message += f"📊 Total items saved: {len(history)}"
    
    keyboard = [
        [InlineKeyboardButton("🗑️ Clear History", callback_data="clear_history")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def clear_history(query, user_id):
    """Clear user's history."""
    if user_id in user_content_history:
        user_content_history[user_id] = []
        await query.answer("🗑️ History cleared!", show_alert=True)
        await show_history(query, user_id)

async def show_about(query):
    """Show bot information."""
    message = "ℹ️ **About This Bot**\n"
    message += "═" * 20 + "\n\n"
    message += "🤖 *Telegram Ads Hub Bot*\n\n"
    message += "📌 *Features:*\n"
    message += "• Daily content across 6 niches\n"
    message += "• Personalized feed preferences\n"
    message += "• Reading history tracking\n"
    message += "• No third-party API keys\n"
    message += "• 100% Telegram Ads friendly\n\n"
    message += "📊 *Stats:*\n"
    message += "• 80+ content topics\n"
    message += "• 6 content categories\n"
    message += "• 100% free to use\n\n"
    message += "📱 Built with python-telegram-bot\n"
    message += "🚀 Deployed on Railway\n\n"
    message += "🔒 Privacy: No data shared with third parties"
    
    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def unsubscribe_user(query, user_id):
    """Unsubscribe user from the bot."""
    if user_id in user_preferences:
        user_preferences[user_id]["subscribed"] = False
    
    keyboard = [[InlineKeyboardButton("🔄 Resubscribe", callback_data="resubscribe")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🙏 You've been unsubscribed.\n\n"
        "Click 'Resubscribe' to start receiving content again.",
        reply_markup=reply_markup
    )

async def resubscribe_user(query, user_id):
    """Resubscribe user."""
    if user_id in user_preferences:
        user_preferences[user_id]["subscribed"] = True
    
    await back_to_main(query, user_id)

async def back_to_main(query, user_id):
    """Return to main menu."""
    keyboard = [
        [InlineKeyboardButton("📰 Daily Content", callback_data="daily")],
        [InlineKeyboardButton("⚙️ Preferences", callback_data="preferences")],
        [InlineKeyboardButton("📚 History", callback_data="history")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("❌ Unsubscribe", callback_data="unsubscribe")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏠 **Main Menu**\n\n"
        "Select an option below:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    await update.message.reply_text(
        "🤖 **Telegram Ads Bot Help**\n\n"
        "📌 *Commands:*\n"
        "/start - Main menu\n"
        "/help - Show this help message\n"
        "/daily - Get your daily content\n"
        "/preferences - Manage your feed\n"
        "/history - View your reading history\n"
        "/about - Bot information\n\n"
        "📱 *How to use:*\n"
        "1. Select your preferred niches\n"
        "2. Get daily content updates\n"
        "3. Track your reading history\n\n"
        "🔒 *Privacy:* No third-party API keys\n"
        "📊 *Ad-friendly:* 100% compliant with Telegram Ads"
    )

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command."""
    user_id = update.effective_user.id
    # Create a mock query object
    class MockQuery:
        async def answer(self):
            pass
        async def edit_message_text(self, text, reply_markup=None):
            await update.message.reply_text(text, reply_markup=reply_markup)
        from_user = update.effective_user
    
    mock_query = MockQuery()
    await send_daily_content(mock_query, user_id)

async def preferences_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /preferences command."""
    user_id = update.effective_user.id
    class MockQuery:
        async def answer(self):
            pass
        async def edit_message_text(self, text, reply_markup=None):
            await update.message.reply_text(text, reply_markup=reply_markup)
        from_user = update.effective_user
    
    mock_query = MockQuery()
    await show_preferences(mock_query, user_id)

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command."""
    user_id = update.effective_user.id
    class MockQuery:
        async def answer(self):
            pass
        async def edit_message_text(self, text, reply_markup=None):
            await update.message.reply_text(text, reply_markup=reply_markup)
        from_user = update.effective_user
    
    mock_query = MockQuery()
    await show_history(mock_query, user_id)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    user_id = update.effective_user.id
    class MockQuery:
        async def answer(self):
            pass
        async def edit_message_text(self, text, reply_markup=None):
            await update.message.reply_text(text, reply_markup=reply_markup)
        from_user = update.effective_user
    
    mock_query = MockQuery()
    await show_about(mock_query)

async def clear_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clearhistory command."""
    user_id = update.effective_user.id
    if user_id in user_content_history:
        user_content_history[user_id] = []
        await update.message.reply_text("🗑️ Your history has been cleared!")
    else:
        await update.message.reply_text("📭 You have no history to clear.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo any non-command messages."""
    await update.message.reply_text(
        "🤖 I'm a bot! Use /start to begin.\n"
        "For help, type /help."
    )

def main():
    """Start the bot."""
    try:
        logger.info("Starting bot...")
        application = Application.builder().token(BOT_TOKEN).build()

        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("daily", daily_command))
        application.add_handler(CommandHandler("preferences", preferences_command))
        application.add_handler(CommandHandler("history", history_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("clearhistory", clear_history_command))
        
        # Callback query handler
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        # Start the Bot
        logger.info("Bot is running...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
