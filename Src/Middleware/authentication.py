import os
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import Message

load_dotenv()

# Verificação de autorização grupo
def authorization():
    def decorador(func):
        chat = [
            int(os.getenv("CHAT_ID_ADM")),
            int(os.getenv("CHAT_ID_GROUP_RECOLHIMENTO")),
        ]
        def verificacao(client: Client, message: Message):
            if message.chat.id in chat:
                return func(client, message)
            else:
                message.reply_text("Você não está autorizado a usar este bot.")
        return verificacao
    return decorador
