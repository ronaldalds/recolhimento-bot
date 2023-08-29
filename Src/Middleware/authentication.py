from pyrogram import Client
from pyrogram.types import Message

# Verificação de autorização grupo
def authorization_group(ids_autorizados):
    def decorador(func):
        def verificacao(client: Client, message: Message):
            if message.chat.id in ids_autorizados:
                return func(client, message)
            else:
                message.reply_text("Você não está autorizado a usar este bot.")
        return verificacao
    return decorador

# Verificação de autorização adm
def authorization_adm(ids_autorizados):
    def decorador(func):
        def verificacao(client: Client, message: Message):
            if message.from_user.id in ids_autorizados:
                return func(client, message)
            else:
                message.reply_text("Você não está autorizado a usar este bot.")
        return verificacao
    return decorador