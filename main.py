import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from Src.Middleware.authentication import authorization
from Src.Controller.recolhimento_controller import handle_start_recolhimento, handle_stop_recolhimento, handle_status_recolhimento

load_dotenv()

app = Client(
    name="RECOLHIMENTO_BOT", 
    api_hash=os.getenv("API_HASH_TELEGRAM"),
    api_id=os.getenv("API_ID_TELEGRAM"),
    bot_token=os.getenv("BOT_TOKEN_TELEGRAM_RECOLHIMENTO")
    )

@app.on_message(filters.command("start"))
def start(client, message: Message):
    message.reply_text(f"""
/recolhimento - Setor Recolhimento
/chat - Informa seu chat_id
/chatgroup - Informa chat_id grupo
""")

@app.on_message(filters.command("recolhimento"))
@authorization()
def financeiro(client, message: Message):
    message.reply_text(f"""
/iniciar_recolhimento - Iniciar Recolhimento
/parar_recolhimento - Parar Recolhimento
/status_recolhimento - Status Recolhimento
""")

@app.on_message(filters.command("chatgroup"))
@authorization()
def handle_group_id(client: Client, message: Message):
    client.send_message(int(os.getenv("CHAT_ID_ADM")), message)

@app.on_message(filters.command("chat"))
def handle__id(client: Client, message: Message):
    text = f"{message.chat.first_name}.{message.chat.last_name} - ID:{message.from_user.id}"
    client.send_message(message.from_user.id, text)
    if int(os.getenv("CHAT_ID_ADM")) != message.from_user.id:
        client.send_message(int(os.getenv("CHAT_ID_ADM")), text)

# iniciar cancelamento
@app.on_message(filters.command("iniciar_recolhimento"))
@authorization()
def iniciar_recolhimento(client: Client, message: Message):
    handle_start_recolhimento(client, message)

# parar cancelamento
@app.on_message(filters.command("parar_recolhimento"))
@authorization()
def parar_recolhimento(client: Client, message: Message):
    handle_stop_recolhimento(client, message)

# status cancelamento
@app.on_message(filters.command("status_recolhimento"))
@authorization()
def status_recolhimento(client: Client, message: Message):
    handle_status_recolhimento(client, message)

# stop service
@app.on_message(filters.command("stop_service"))
@authorization()
def stop(client: Client, message: Message):
    print("Service Stopping")
    app.stop()

print("Service Telegram Up!")
app.run()

