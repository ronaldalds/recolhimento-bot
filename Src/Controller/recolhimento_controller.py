import os
import concurrent.futures
import pandas as pd
from dotenv import load_dotenv
from pyrogram.types import Message
from pyrogram import Client
from datetime import datetime, timedelta
from Src.Service.recolhimento_service import recolhimento
from Src.Util.formatador import formatar_documento

load_dotenv()

running = False

lojas_mk1 = {
    "LOJA ALCÂNTARAS": 2,
    "LOJA ANAPURUS": 2,
    "LOJA ARARENDÁ": 2,
    "LOJA BOA VIAGEM": 3,
    "LOJA CAMOCIM": 10,
    "LOJA CARIRÉ": 2,
    "LOJA CARNAUBAL": 2,
    "LOJA GUARACIABA DO NORTE": 5,
    "LOJA HIDROLÂNDIA": 2,
    "LOJA IBIAPINA": 2,
    "LOJA IPUEIRAS": 2,
    "LOJA ITATIRA": 2,
    "LOJA LISIEUX": 2,
    "LOJA MATA ROMA": 2,
    "LOJA MERUOCA": 2,
    "LOJA MONSENHOR TABOSA": 2,
    "LOJA NOVO ORIENTE": 3,
    "LOJA PEDRO II": 3,
    "LOJA PIRACURUCA": 3,
    "LOJA PIRIPIRI": 4,
    "LOJA RERIUTABA": 2,
    "LOJA SANTA QUITÉRIA": 3,
    "LOJA SÃO BERNARDO": 2,
    "LOJA TAMBORIL": 2,
    "LOJA UBAJARA": 2,
    "LOJA VARJOTA": 4,
}

lojas_mk3 = {
    "LOJA CASTANHAL": 8,
    "LOJA VIGIA": 5,
    "LOJA TERRA ALTA": 4,
    "LOJA ICOARACI": 5,
    "LOJA MARITUBA": 9,
    "LOJA VILA DOS CABANOS": 8,
    "LOJA BARCARENA": 4,
    "LOJA MAGUARI": 4,
    "LOJA ABAETETUBA": 12,
    "LOJA TUCURUI": 5,
    "LOJA TAILÂNDIA": 4,
    "LOJA MOJU": 4,
    "LOJA MOCAJUBA": 3,
    "LOJA BAIÃO": 2
}

def __limpa_lista(lista):
    # cria dict com todas as lojas que tem limite de O.S
    dicionario = dict(lojas_mk1, **lojas_mk3)
    lista_resultante = []
    # cria um dict com todos os valores 0 para contar as ocorrencias
    ocorrencias_dict = {chave: 0 for chave in dicionario}
    
    # percorre a lista de O.S de recolhimento que existe
    for item in lista:
        chave = item.get('Loja') # posicao da tupla onde esta o que voce quer contar a ocorrencia
        if chave in dicionario:
            valor_limite = dicionario[chave] # quantidade de O.S que pdoe ser abertas por loja
            if ocorrencias_dict[chave] < valor_limite:
                lista_resultante.append(item)
                ocorrencias_dict[chave] += 1
        else:
            # continua na lista as lojas que nao tiverem cadastrado um limite de O.S
            lista_resultante.append(item)

    return lista_resultante

def handle_start_recolhimento(client: Client, message: Message):
    global running
    if not running:
        # Verifique se a mensagem contém um documento e se o tipo MIME do documento é "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if message.document and message.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            running = True
            # Quantidade de itens na Pool
            limite_threads = 10

            # Baixe o arquivo XLSX
            file_path = message.download(in_memory=True)
            ajuste_gmt = timedelta(hours=3)
            hora = datetime.now() - ajuste_gmt
            file_name = hora.strftime("%S_%M_%H %Y-%m-%d.log")
            message.reply_text("Preparando arquivo XLSX")

            # caminho pasta de logs
            diretorio_logs = os.path.join(os.path.dirname(__file__), 'logs')

            # caminho pasta de docs
            diretorio_docs = os.path.join(os.path.dirname(__file__), 'docs')

            # cria pasta de logs em caso de nao existir
            if not os.path.exists(diretorio_logs):
                os.makedirs(diretorio_logs)

            # cria pasta de docs em caso de nao existir
            if not os.path.exists(diretorio_docs):
                os.makedirs(diretorio_docs)
            
            # Processar o arquivo XLSX conforme necessário
            try:
                try:
                    # Ler o arquivo XLSX usando pandas e especificar a codificação UTF-8
                    df = pd.read_excel(file_path, engine='openpyxl')

                    # Converter o dataframe para uma lista de dicionários
                    lista = df.to_dict(orient='records')

                    # Verificar se a chave 'MK' contém valor NaN
                    lista = [dados for dados in lista if not pd.isna(dados.get('MK'))]
                    
                    # Verificar se a chave Qtd Conexções é igual a 1 e OS Cancelamento ou Recolhimento é igual a N
                    lista = [dados for dados in lista if (str(dados.get('Qtd Conexoes')) == "1") and (dados.get('OS Cancelamento ou Recolhimento') == "N")]

                    # lista com todas as O.S
                    message.reply_text(f"Processando arquivo XLSX de recolhimento com {len(lista)} O.S...")

                    # lista com base na quantidade maxima de os que pode ser abertas por loja
                    lista = __limpa_lista(lista)
                    message.reply_text(f"Arquivo XLSX de recolhimento ajustado para {len(lista)} O.S...") 

                    # Criar aquivo de log com todos os contratos enviados para Recolhimento
                    with open(os.path.join(diretorio_docs, file_name), "a") as pedido:
                        for c,arg in enumerate(lista):
                            pedido.write(f"{(c + 1):03};Recolhimento;MK:{int(arg.get('MK'))};Contrato:{int(arg.get('Contrato'))};Grupo:{arg.get('Grupo Atendimento OS')};Agente:{message.from_user.first_name}.{message.from_user.last_name}\n")
                    
                    # Envia arquivo de docs com todos as solicitações de Recolhimento
                    with open(os.path.join(diretorio_docs, file_name), "rb") as enviar_docs:
                        client.send_document(os.getenv("CHAT_ID_ADM"),enviar_docs, caption=f"solicitações {file_name}", file_name=f"solicitações {file_name}")

                    
                    message.reply_text(f"Processando arquivo XLSX de Recolhimento com {len(lista)} contratos...")

                except pd.errors.ParserError:
                    message.reply_text("O arquivo fornecido não é um arquivo XLSX válido.")
                    running = False
                    return
                
                def executar(arg: dict):
                    if running:
                        try:
                            mk = int(arg.get("MK"))
                            contrato = int(arg.get("Contrato"))
                            conexao_associada = int(arg.get("Conexao Associada"))
                            cpf = formatar_documento(arg.get("Documento/Codigo"))['cpf']
                            cod = formatar_documento(arg.get("Documento/Codigo"))['cod']
                            tipo_da_os = arg.get("Tipo OS")
                            grupo_atendimento_os = arg.get("Grupo Atendimento OS")
                            detalhe_os = arg.get("Detalhe OS")
                            loja = arg.get("Loja")

                            return recolhimento(
                                mk = mk,
                                contrato = contrato,
                                conexao_associada = conexao_associada,
                                cpf = cpf,
                                cod = cod,
                                tipo_da_os = tipo_da_os,
                                grupo_atendimento_os = grupo_atendimento_os,
                                detalhe_os = detalhe_os,
                                loja = loja,
                                )
                            return mk, conexao_associada, contrato
                        except Exception as e:
                            print(f'Error executar na função Recolhimento:mk:{int(arg.get("MK"))} contrato:{int(arg.get("Contrato"))} {e}')
                    else:
                        message.reply_text(f'Recolhimento mk:{int(arg.get("MK"))} contrato:{int(arg.get("Contrato"))} parado.')
                
                # Criando Pool
                with concurrent.futures.ThreadPoolExecutor(max_workers=limite_threads) as executor:
                    resultados = executor.map(executar, lista)

            except Exception as e:
                print(f"Ocorreu um erro ao processar o arquivo XLSX: {e}")
                running = False
                return
            
            finally:
                # Criar aquivo de log com todos os resultados de Recolhimento
                with open(os.path.join(diretorio_logs, file_name), "a") as file:
                    if resultados:
                        for resultado in resultados:
                            file.write(f"{resultado}\n")

                # Envia arquivo de log com todos os resultados de Recolhimento
                with open(os.path.join(diretorio_logs, file_name), "rb") as enviar_logs:
                    message.reply_document(enviar_logs, caption=file_name, file_name=file_name)
                    client.send_document(os.getenv("CHAT_ID_ADM"), enviar_logs, caption=f"resultado {file_name}", file_name=f"resultado {file_name}")

                print("Processo Recolhimento concluído.")
                message.reply_text("O arquivo XLSX de Recolhimento foi processado com sucesso!")
                running = False
                return
                
        else:
            # Responder à mensagem do usuário com uma mensagem de erro
            message.reply_text("Por favor, envie um arquivo XLSX para processar.")
            return
    else:
        message.reply_text("Recolhimento em execução.")
        return

def handle_stop_recolhimento(client: Client, message: Message):
    global running
    if running:
        running = False
        message.reply_text("Pedido de parada iniciado...")
        return
    else:
        message.reply_text("Recolhimento parado")
        return
        
def handle_status_recolhimento(client: Client, message: Message):
    global running
    try:
        if running:
            message.reply_text("Recolhimento em execução")
            return
        else:
            message.reply_text("Recolhimento parado")
            return
    except:
        message.reply_text("Recolhimento parado")
        return