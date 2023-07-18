import re
from datetime import datetime, timedelta

def formatar_data(data):
    try:
        return data.strftime("%d%m%Y")
    except:
        if (type(data) == float) or (type(data) == int):
            data = datetime(1899, 12, 30) + timedelta(days=int(data))
            return data.strftime("%d%m%Y")
        else:
            # regex data
            df = re.compile("([0-9]{2,4})[-]?[/]?([0-9]{2})[-]?[/]?([0-9]{2,4})")
            data = df.findall(data)[0]
            if len(data[2]) == 2:
                return f"{data[2]}{data[1]}{data[0]}"
            
            return f"{data[0]}{data[1]}{data[2]}"

def formatar_valor_multa(multa):
    if multa >= 0:
        return f"{float(multa):.2f}".replace(".", ",")
    else:
        return None

def formatar_int(num):
    try:
        num = int(num)
        if type(num) == int:
            return num
    except:
        return "test"

def formatar_incidencia(incidencia):
    # verifica se é S = a True ou N = a False
    if "S" == str(incidencia).strip():
        return True
    elif "N" == str(incidencia).strip():
        return False
    # retorna None em caso de um valor diferente de S ou N
    else:
        return None

def formatar_documento(doc):
    try:
        regex_cpf = re.compile("[0-9]{3}[.][0-9]{3}[.][0-9]{3}[-][0-9]{2}")
        cpf = regex_cpf.match(doc).group()
    except:
        cpf = "Não Encontrado"
    try:
        cod = str(doc).strip().split(" cod: ")[1]
    except:
        cod = "Não Encontrado"
        
    return {"cpf": cpf, "cod": cod}

    