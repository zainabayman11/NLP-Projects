import telebot
from langchain_ollama import OllamaLLM
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from prompts import CHAT_PROMPT
from config import BOT_TOKEN, MODEL_NAME

bot = telebot.TeleBot(BOT_TOKEN)
llm = OllamaLLM(model=MODEL_NAME)

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain = CHAT_PROMPT | llm

chat_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = str(message.chat.id)
    user_input = message.text.strip()

    response = chat_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": chat_id}}
    )

    bot.send_message(chat_id, response)

bot.delete_webhook(drop_pending_updates=True)
bot.infinity_polling(skip_pending=True)
