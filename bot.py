import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Analysis Functions ---
def analyze_text(text):
    """Analyzes the text and returns a dictionary with counts."""
    word_count = len(text.split())
    char_count = len(text)
    char_count_no_space = len(text.replace(" ", ""))
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    paragraph_count = max(1, text.count('\n') + 1)
    
    # Calculate average word length
    words = text.split()
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_count_no_space": char_count_no_space,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_word_length": round(avg_word_length, 1)
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        "I am a Word Counter Bot. Send me any text, and I'll count words, "
        "characters, sentences, and paragraphs for you.\n\n"
        "You can also use these commands:\n"
        "/start - Start the bot\n"
        "/help - Get help\n"
        "/word_count - Count words in a replied message or text"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    await update.message.reply_text(
        "📝 **How to use this bot:**\n\n"
        "1. Send me any text, and I'll analyze it automatically.\n"
        "2. Use the command /word_count followed by text to analyze it.\n"
        "3. Reply to a message with /word_count to analyze that message.\n\n"
        "I'll count:\n"
        "• Words\n"
        "• Characters (with and without spaces)\n"
        "• Sentences\n"
        "• Paragraphs\n"
        "• Average word length"
    )

async def word_count_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /word_count command."""
    try:
        if update.message.reply_to_message:
            text_to_analyze = update.message.reply_to_message.text
            if not text_to_analyze:
                await update.message.reply_text("The replied message doesn't contain any text to analyze.")
                return
        elif context.args:
            text_to_analyze = " ".join(context.args)
        else:
            await update.message.reply_text(
                "Please provide some text to analyze.\n"
                "For example: /word_count This is my text.\n"
                "Or reply to a message with /word_count."
            )
            return
        
        counts = analyze_text(text_to_analyze)
        response = (
            f"📊 **Text Analysis Results:**\n\n"
            f"📝 **Words:** {counts['word_count']}\n"
            f"🔤 **Characters (with spaces):** {counts['char_count']}\n"
            f"🔤 **Characters (without spaces):** {counts['char_count_no_space']}\n"
            f"📄 **Sentences:** {counts['sentence_count']}\n"
            f"📑 **Paragraphs:** {counts['paragraph_count']}\n"
            f"📏 **Avg Word Length:** {counts['avg_word_length']} characters"
        )
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in word_count_command: {e}")
        await update.message.reply_text("Sorry, there was an error analyzing your text. Please try again.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Analyze any text message the bot receives."""
    try:
        text = update.message.text
        if not text:
            return
        
        counts = analyze_text(text)
        response = (
            f"📊 **I analyzed your text:**\n\n"
            f"📝 **Words:** {counts['word_count']}\n"
            f"🔤 **Characters (with spaces):** {counts['char_count']}\n"
            f"🔤 **Characters (without spaces):** {counts['char_count_no_space']}\n"
            f"📄 **Sentences:** {counts['sentence_count']}\n"
            f"📑 **Paragraphs:** {counts['paragraph_count']}\n"
            f"📏 **Avg Word Length:** {counts['avg_word_length']} characters"
        )
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("Sorry, there was an error analyzing your text. Please try again.")

def main() -> None:
    """Start the bot."""
    try:
        # Get the token from environment variables
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
            return
        
        # Create the Application with proper settings
        application = Application.builder().token(token).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("word_count", word_count_command))
        
        # Register a handler for any text message
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start the bot in polling mode
        logger.info("Bot started and polling for updates...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
