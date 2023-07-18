import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from Src.Middleware.authentication import authorization
from Src.Controller.recolhimento_controller import handle_start_recolhimento, handle_stop_recolhimento, handle_status_recolhimento

load_dotenv()

version = "0.0.1"

app = Client(
    name=os.getenv("BOT_NAME_TELEGRAM"), 
    api_hash=os.getenv("API_HASH_TELEGRAM"),
    api_id=os.getenv("API_ID_TELEGRAM"),
    bot_token=os.getenv("BOT_TOKEN_TELEGRAM")
    )

chat_adm = [
    int(os.getenv("CHAT_ID_ADM")),
]

chat_group = [
    int(os.getenv("CHAT_ID_ADM")),
    int(os.getenv("CHAT_ID_GROUP_RECOLHIMENTO")),
]

@app.on_message(filters.command("start"))
def start(client, message: Message):
    message.reply_text(f"""
/recolhimento - Setor Recolhimento
/chat - Informa seu chat_id
/chatgroup - Informa chat_id grupo
""")

@app.on_message(filters.command("recolhimento"))
@authorization(chat_group)
def financeiro(client, message: Message):
    message.reply_text(f"""
/iniciar_recolhimento - Iniciar Recolhimento
/parar_recolhimento - Parar Recolhimento
/status_recolhimento - Status Recolhimento
""")

@app.on_message(filters.command("chatgroup"))
@authorization(chat_adm)
def handle_chatgroup_id(client: Client, message: Message):
    client.send_message(message.from_user.id, message)

@app.on_message(filters.command("chat"))
def handle_chat_id(client: Client, message: Message):
    text = f"{message.from_user.first_name}.{message.from_user.last_name} - ID:{message.from_user.id}"
    client.send_message(message.from_user.id, text)
    client.send_message(chat_adm[0], text)

# iniciar cancelamento
@app.on_message(filters.command("iniciar_recolhimento"))
@authorization(chat_group)
def iniciar_recolhimento(client: Client, message: Message):
    handle_start_recolhimento(client, message)

# parar cancelamento
@app.on_message(filters.command("parar_recolhimento"))
@authorization(chat_group)
def parar_recolhimento(client: Client, message: Message):
    handle_stop_recolhimento(client, message)

# status cancelamento
@app.on_message(filters.command("status_recolhimento"))
@authorization(chat_group)
def status_recolhimento(client: Client, message: Message):
    handle_status_recolhimento(client, message)

# stop service
@app.on_message(filters.command("stop_service"))
@authorization(chat_adm)
def stop(client: Client, message: Message):
    print("Service Stopping")
    app.stop()

print("Service Telegram Up!")
print(f"Version {version}")
app.run()

