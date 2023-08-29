import time
from Src.Api.mk.mk_driver import Mk
from Src.Api.mk.coin.coin import Workspace
from Src.Api.mk.aside.aside_workspace import OsPainel
from selenium.webdriver.common.keys import Keys
from Src.Api.mk.mk_select import (
    TIPO_DA_OS,
    NIVEL_DE_SLA,
    GRUPO_DE_ATENDIMENTO_MK01,
    GRUPO_DE_ATENDIMENTO_MK03
)
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta

load_dotenv()

def recolhimento(
        mk,
        contrato,
        conexao_associada,
        cpf,
        cod,
        tipo_da_os,
        grupo_atendimento_os,
        detalhe_os,
        loja
        ):
    ajuste_gmt = timedelta(hours=3)
    hora = datetime.now() - ajuste_gmt
    print(f'Iniciou recolhimento {hora.strftime("%d/%m/%Y %H:%M")} MK{mk:02} contrato:{contrato} cpf:{cpf} loja:{loja}')
    error = f"\033[91mERROR\033[0m;RECOLHIMENTO;{hora.strftime('%d/%m/%Y %H:%M')}"
    warning = f"\033[93mWARNING\033[0m;RECOLHIMENTO;{hora.strftime('%d/%m/%Y %H:%M')}"
    sucess = f"\033[92mSUCESS\033[0m;RECOLHIMENTO;{hora.strftime('%d/%m/%Y %H:%M')}"

    prefixo_log_recolhimento = f'MK:{mk:02};contrato:{contrato};conexão:{conexao_associada};cpf:{cpf}'

    valor_nivel_sla = NIVEL_DE_SLA['Preventivo']
    valor_tipo_de_os = TIPO_DA_OS[tipo_da_os]
    if mk == 1:
        instance = Mk(
            username=os.getenv('USERNAME_MK1'),
            password=os.getenv('PASSWORD_MK1'),
            url=os.getenv('URL_MK1'),
        )
        valor_grupo_atendimento = GRUPO_DE_ATENDIMENTO_MK01[grupo_atendimento_os]
    elif mk == 3:
        instance = Mk(
            username=os.getenv('USERNAME_MK3'),
            password=os.getenv('PASSWORD_MK3'),
            url=os.getenv('URL_MK3'),
        )
        valor_grupo_atendimento = GRUPO_DE_ATENDIMENTO_MK03[grupo_atendimento_os]

    else:
        txt = f'{error};{prefixo_log_recolhimento};Não foi possível criar instancia do mk...'
        print(txt)
        return txt
    
    
    workspace = Workspace()
    ospainel = OsPainel()

    # login no sistema mk
    try:
        instance.login()
    except:
        txt = f'{error};{prefixo_log_recolhimento};Failed to login.'
        instance.close()
        print(txt)
        return txt

    # instance.minimizeChat()

    # fechar tela de complete seu cadastro
    try:
        instance.iframeMain()
        instance.click('//div[@class="OptionClose"]')
    except:
        pass

    # click na moeda workspace
    instance.iframeCoin()
    instance.click(workspace.xpath())

    # click aside O.S - Painel
    instance.iframeAsideCoin(workspace)
    instance.click(ospainel.xpath())

    # click criar nova O.S
    instance.iframePainel(workspace, ospainel)
    instance.click('//*[@title="Criar Nova O.S."]')

    # Identificador O.S Nome / Documento / Código
    try:
        instance.iframeForm()
        instance.click('//*[@title="Este campo informa qual é o cliente associado a esta Ordem de Serviço."]/div/button')
        instance.write('//input[@id="lookupSearchQuery"]', f"{cpf}" + Keys.ENTER)
        instance.click(f'//option[@value="{cod}"]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Identificador O.S Nome / Documento / Código.'
        instance.close()
        print(txt)
        return txt

    # Avançar no assistente de O.S primeira tela
    try:
        instance.click('//div[@class="HTMLTabContainer"]/div[2]//button[@title="Avançar no assistente de O.S."]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Avançar no assistente de O.S primeira tela.'
        instance.close()
        print(txt)
        return txt
    
    # Escolha de conexão Conexão Associada
    try:
        instance.iframeForm()
        instance.click('//*[@title="Neste campo é informado para qual conexão foi aberta esta Ordem de Serviço."]/div/button')
        instance.write('//input[@id="lookupSearchQuery"]', f"{conexao_associada}" + Keys.ENTER)
        instance.click(f'//option[@value="{conexao_associada}"]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Escolha de conexão Conexão Associada.'
        instance.close()
        print(txt)
        return txt
    
    # Escolha nivel de SLA se habilitado
    try:
        time.sleep(5)
        instance.iframeForm()
        instance.click('//*[@title="Escolhe o nível de prioridade deste serviço."]/div/button')
        instance.write('//input[@id="lookupSearchQuery"]', "Preventivo" + Keys.ENTER)
        instance.click(f'//option[@value="{valor_nivel_sla}"]')
    except:
        txt = f'{warning};{prefixo_log_recolhimento};Escolha nivel de SLA se habilitado.'
        print(txt)

    # Avançar no assistente de O.S segunda tela
    try:
        instance.click('//div[@class="HTMLTabContainer"]/div[3]//button[@title="Avançar no assistente de O.S."]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Avançar no assistente de O.S segunda tela.'
        instance.close()
        print(txt)
        return txt

    # Escolha tipo de O.S
    try:
        instance.iframeForm()
        instance.click('//*[@title="Informa qual o tipo da Ordem de Serviço."]/div/button')
        instance.write('//input[@id="lookupSearchQuery"]', f"{tipo_da_os}" + Keys.ENTER)
        instance.click(f'//option[@value="{valor_tipo_de_os}"]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Escolha tipo de O.S.'
        instance.close()
        print(txt)
        return txt

    # Escrever Relato do problema
    try:
        instance.iframeForm()
        instance.write('//textarea[@title="Neste campo é informado o relato do cliente perante a abertura da Ordem de Serviço."]', detalhe_os)
    except:
        txt = f'{error};{prefixo_log_recolhimento};Escrever Relato do problema.'
        instance.close()
        print(txt)
        return txt

    # Avançar no assistente de O.S terceira tela
    try:
        instance.click('//div[@class="HTMLTabContainer"]/div[4]//button[@title="Avançar no assistente de O.S."]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Avançar no assistente de O.S terceira tela.'
        instance.close()
        print(txt)
        return txt
    
    # Avançar no assistente de O.S quarta tela
    try:
        instance.click('//div[@class="HTMLTabContainer"]/div[8]//button[@title="Avançar no assistente de O.S."]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Avançar no assistente de O.S quarta tela.'
        instance.close()
        print(txt)
        return txt


    # Escolha Grupo de atendimento
    try:
        instance.iframeForm()
        instance.click('//div[@class="HTMLTabContainer"]/div[9]//div[@class="HTMLLookup"]/div[2]/div/button')
        instance.write('//input[@id="lookupSearchQuery"]', f"{grupo_atendimento_os}" + Keys.ENTER)
        instance.click(f'//option[@value="{valor_grupo_atendimento}"]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Escolha Grupo de atendimento.'
        instance.close()
        print(txt)
        return txt

    # Avançar no assistente de O.S quinta tela
    try:
        instance.click('//div[@class="HTMLTabContainer"]/div[9]//button[@title="Avançar no assistente de O.S."]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Avançar no assistente de O.S quinta tela.'
        instance.close()
        print(txt)
        return txt

    # Avançar no assistente de O.S sexta tela
    try:
        instance.click('//div[@class="HTMLTabContainer"]/div[10]//button[@title="Clique para efetivar a criação desta O.S.."]')
    except:
        txt = f'{error};{prefixo_log_recolhimento};Avançar no assistente de O.S sexta tela.'
        instance.close()
        print(txt)
        return txt

    # alert concluir O.S recolhimento
    instance.include()

    # log recolhimento de contrato conluído
    time.sleep(5)
    instance.close()
    txt = f'{sucess};{prefixo_log_recolhimento};recolhimento de contrato conluído'
    return txt
