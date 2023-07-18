from pyrogram import Client
from pyrogram.types import Message

# Verificação de autorização
def authorization(ids_autorizados):
    def decorador(func):
        def verificacao(client: Client, message: Message):
            if message.chat.id in ids_autorizados:
                return func(client, message)
            else:
                message.reply_text("Você não está autorizado a usar este bot.")
        return verificacao
    return decorador