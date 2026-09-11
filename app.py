import os
import streamlit as st
import pandas as pd
import re
from datetime import datetime
import unicodedata
import io

# ====================================================
# Configuração Nativa do Tema Claro
# ====================================================
os.makedirs(".streamlit", exist_ok=True)
config_path = os.path.join(".streamlit", "config.toml")
config_content = """[theme]
base = "light"
primaryColor = "#460988"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3EEF9"
textColor = "#343334"
"""
if not os.path.exists(config_path) or open(config_path, encoding="utf-8").read() != config_content:
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

st.set_page_config(
    page_title="Painel de Segmentação de Eleitores",
    page_icon="📊",
    layout="wide"
)

# ====================================================
# Estilização Visual: Forçar Amarelo + Roxo nas Tags
# ====================================================
st.markdown("""
<style>
    :root {
        color-scheme: light !important;
    }
    
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8F9FA !important;
        color: #343334 !important;
    }
    
    h1, h2, h3, h4, h5, h6, span, p, label {
        color: #343334;
    }
    h1, h2, h3 {
        color: #460988 !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #F3EEF9 !important;
        border-right: 2px solid #DCD0ED !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #460988 !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important;
        border: 2px dashed #460988 !important;
        border-radius: 10px !important;
        color: #343334 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: #460988 !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    input, textarea {
        background-color: #FFFFFF !important;
        color: #343334 !important;
        border-color: #DCD0ED !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #FFFFFF !important;
        color: #460988 !important;
        border-color: #DCD0ED !important;
    }

    /* ========================================================================== */
    /* SOBREPOSIÇÃO BLINDADA: TAG SELECIONADA EM AMARELO #F8AE11 COM FONTE ROXA   */
    /* ========================================================================== */
    [data-testid="stSidebar"] [data-baseweb="tag"],
    [data-testid="stSidebar"] span[data-baseweb="tag"],
    [data-testid="stSidebar"] div[data-baseweb="tag"],
    div[data-testid="stMultiSelect"] [data-baseweb="tag"],
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"],
    div[data-testid="stMultiSelect"] div[data-baseweb="tag"],
    [data-baseweb="select"] [data-baseweb="tag"],
    [data-baseweb="tag"] {
        background-color: #F8AE11 !important;
        background: #F8AE11 !important;
        border: 1px solid #E29B05 !important;
        border-radius: 6px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] *,
    [data-testid="stSidebar"] span[data-baseweb="tag"] *,
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] *,
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] *,
    [data-baseweb="select"] [data-baseweb="tag"] *,
    [data-baseweb="tag"] * {
        color: #460988 !important;
        fill: #460988 !important;
        font-weight: 800 !important;
        font-size: 0.88rem !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] svg,
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] svg,
    [data-baseweb="tag"] svg {
        fill: #460988 !important;
        color: #460988 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] svg:hover,
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] svg:hover,
    [data-baseweb="tag"] svg:hover {
        fill: #24044A !important;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        padding: 16px;
        border-radius: 10px;
        border-left: 6px solid #460988 !important;
        box-shadow: 0 2px 8px rgba(70, 9, 136, 0.08);
    }
    [data-testid="stMetricLabel"] {
        color: #666666 !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #460988 !important;
        font-weight: 800 !important;
    }

    .stButton > button {
        background-color: #460988 !important;
        color: #FFFFFF !important;
        border: 2px solid #460988 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
    }
    .stButton > button:hover {
        background-color: #5B0EB0 !important;
        border-color: #F8AE11 !important;
        color: #FFFFFF !important;
    }

    [data-testid="stDownloadButton"] > button {
        background-color: #F8AE11 !important;
        color: #2D2505 !important;
        border: 2px solid #F8AE11 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 8px 20px !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #E29B05 !important;
        border-color: #460988 !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ====================================================
# Motor de Identificação de Sexo / Gênero
# ====================================================

EXCECOES_FEMININAS = {
    'ABADIA', 'ALICE', 'BEATRIZ', 'CARMEM', 'CARMEN', 'CLEIDE', 'CLOE', 'DAIANE', 'DAIANI',
    'DAYANE', 'DAYANI', 'DENISE', 'DIANE', 'DORIS', 'EDITE', 'EDITH', 'ELEN', 'ELIS', 'ELIZABETH',
    'ELIZETE', 'EMANUELLE', 'ESTER', 'ESTHER', 'EUNICE', 'FRANCOISE', 'GLEICE', 'GLEICI',
    'GRACE', 'HELEN', 'HELOISE', 'INEZ', 'INÊS', 'IRIS', 'ISABEL', 'ISABELE', 'ISABELLA',
    'ISABELLE', 'IVETE', 'IVONE', 'JAQUELINE', 'JANETE', 'JOCELENE', 'JOCELYN', 'JOELMA',
    'JOSIANE', 'JOYCE', 'JUDITE', 'JULIANE', 'KAREN', 'KATIA', 'KELLY', 'LAIS', 'LARISSA',
    'LEIDE', 'LIDIANE', 'LILIAN', 'LILIANE', 'LIS', 'LIZ', 'LOURDES', 'LUCIANE', 'LUCIELE',
    'LUCIENE', 'LUCIMAR', 'LUDMILA', 'LUZIA', 'MADALENA', 'MAIRA', 'MANUELA', 'MARA',
    'MARCELA', 'MARCIA', 'MARGARETE', 'MARI', 'MARIA', 'MARIENE', 'MARILENE', 'MARILU',
    'MARINA', 'MARISA', 'MARISTELA', 'MARIZE', 'MARLENE', 'MARLI', 'MARLY', 'MIRIAM',
    'MIRIAN', 'MONICA', 'NADIR', 'NAIR', 'NAIRA', 'NEIDE', 'NICOLE', 'NOEMI', 'RAQUEL',
    'REGINA', 'ROBERTA', 'ROSE', 'ROSEANE', 'ROSELI', 'ROSEMARY', 'ROSILENE', 'RUTE', 'RUTH',
    'SALETE', 'SHIRLEY', 'SIMONE', 'SIRLEI', 'SIRLENE', 'SOLANGE', 'SONIA', 'SUELI', 'SUELY',
    'SUZANA', 'TAIS', 'THAIS', 'TATIANE', 'TEREZA', 'VALDENICE', 'VALERIA', 'VANDETE',
    'VANESSA', 'VERA', 'VIVIAN', 'VIVIANE', 'YASMIN', 'ZILDA', 'ZILMA', 'ZULEICA', 'ZULEIDE'
}

EXCECOES_MASCULINAS = {
    'JEAN', 'LUCA', 'LUKA', 'SASHA', 'ANDRE', 'ALEXANDRE', 'FELIPE', 'GUILHERME', 'HENRIQUE',
    'JORGE', 'VICENTE', 'VALDIR', 'WAGNER', 'VAGNER', 'ALTAIR', 'ADEMIR', 'VALMIR', 'WALMIR',
    'MOACIR', 'MOACYR', 'ODAIR', 'ELIEZER', 'VALTER', 'WALTER', 'HEITOR', 'VICTOR', 'VITOR',
    'IGOR', 'ARTHUR', 'ARTUR', 'CESAR', 'CEZAR', 'EDER', 'ELDER', 'JUNIOR', 'LUCAS', 'MATHEUS',
    'MATEUS', 'MARCOS', 'VINICIUS', 'LUIS', 'LUIZ', 'CARLOS', 'ELIAS', 'JONAS', 'TOMAS', 'THOMAS',
    'NILSON', 'EDILSON', 'ADILSON', 'GILSON', 'JAILSON', 'DENILSON', 'CLEITON', 'CLAYTON',
    'WELLINGTON', 'WASHINGTON', 'EVERTON', 'EMERSON', 'EDSON', 'ANDERSON', 'JEFFERSON', 'ROBSON',
    'ALISON', 'ALISSON', 'GABRIEL', 'RAFAEL', 'DANIEL', 'SAMUEL', 'MICHAEL', 'MIGUEL', 'MANOEL',
    'MANUEL', 'JOEL', 'NOEL', 'URIEL', 'ISMAEL', 'ISRAEL', 'NATANIEL', 'EZEQUIEL', 'MARCELLUS',
    'ABENDEGO', 'TIAGO', 'THIAGO', 'DIOGO', 'RODRIGO', 'DIEGO', 'HUGO', 'BRUNO', 'LEONARDO'
}

def classificar_genero(nome_completo, valor_coluna_sexo=None):
    if valor_coluna_sexo is not None and pd.notna(valor_coluna_sexo):
        v = str(valor_coluna_sexo).strip().upper()
        if v in ['M', 'MASC', 'MASCULINO', 'HOMEM']:
            return "Masculino"
        if v in ['F', 'FEM', 'FEMININO', 'MULHER']:
            return "Feminino"

    if not nome_completo or pd.isna(nome_completo):
        return "Não Identificado"
        
    partes = remover_acentos(nome_completo).split()
    if not partes:
        return "Não Identificado"
        
    p_nome = partes[0]
    
    if p_nome in EXCECOES_MASCULINAS:
        return "Masculino"
    if p_nome in EXCECOES_FEMININAS:
        return "Feminino"
        
    if p_nome in ['MARIA', 'ANA']:
        return "Feminino"
    if p_nome in ['JOAO', 'JOSE', 'FRANCISCO']:
        return "Masculino"
        
    if p_nome.endswith(('INA', 'ANA', 'ELA', 'AIA', 'ARA', 'ETE', 'ICE', 'ISE', 'ELLE', 'IELE', 'IA', 'CA', 'DA', 'GA', 'LA', 'MA', 'NA', 'PA', 'RA', 'SA', 'TA', 'VA', 'ZA', 'A')):
        return "Feminino"
        
    if p_nome.endswith(('O', 'OS', 'OR', 'ER', 'EL', 'ON', 'SON', 'TON', 'IO', 'DO', 'TO', 'US', 'ES', 'EU', 'AO', 'IM', 'UR', 'IR', 'AS', 'IS', 'UZ')):
        return "Masculino"
        
    return "Não Identificado"

# ====================================================
# Motor de Filtragem de Telefones (Apenas Celulares)
# ====================================================

def padronizar_telefone_candidato(tel_str, ddd_padrao="63"):
    if not tel_str:
        return None
    digitos = re.sub(r'\D', '', str(tel_str))
    if not digitos:
        return None
        
    if len(digitos) in (12, 13) and digitos.startswith('55'):
        digitos = digitos[2:]
        
    if len(digitos) == 8:
        if digitos[0] in ['2', '3', '4', '5']:
            return None # Fixo
        if digitos[0] in ['6', '7', '8', '9']:
            return f"{ddd_padrao}9{digitos}"
            
    elif len(digitos) == 9:
        if digitos.startswith('9'):
            return f"{ddd_padrao}{digitos}"
        return None
        
    elif len(digitos) == 10:
        ddd = digitos[:2]
        corpo = digitos[2:]
        if corpo[0] in ['2', '3', '4', '5']:
            return None # Fixo com DDD
        if corpo[0] in ['6', '7', '8', '9']:
            return f"{ddd}9{corpo}"
            
    elif len(digitos) == 11:
        if digitos[2] == '9':
            return digitos
        return None
        
    return None

def selecionar_celular(valor_celula, ddd_padrao="63"):
    if pd.isna(valor_celula) or not str(valor_celula).strip():
        return ""
        
    candidatos = re.split(r'[,;/|\n\\]', str(valor_celula))
    for cand in candidatos:
        resultado = padronizar_telefone_candidato(cand.strip(), ddd_padrao)
        if resultado:
            return resultado
            
    return ""

# ====================================================
# Motor de Filtragem de Bairros (Corte em Q + Unificação)
# ====================================================

def remover_acentos(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', texto).strip().upper()

def cortar_em_q(cand):
    if not cand:
        return ""
    cand = str(cand).strip()
    cand = re.split(r'\b[Qq][a-zA-Z0-9]*\b', cand)[0]
    cand = re.split(r'[,;/]|(?:\b(?:lt\.?|lote|n[º°.]?|num|numero|número|casa|ap|apt|apto|bloco|bl|s/n|sn)\b)', cand, flags=re.IGNORECASE)[0]
    cand = re.split(r'\b(?:entre|esq\.?|esquina|pr[oó]x(?:imo)?|ao\s+lado|em\s+frente)\b', cand, flags=re.IGNORECASE)[0]
    cand = re.split(r'\b\d+\b', cand)[0]
    return cand.strip(" ,-.;/\\")

UNIFICACOES_USUARIO = {
    "Jardim Boulevard": ["Jardim Boilevard", "Jardim Bolevar", "Jardim Boulevard", "Setor Bouleva", "Setor Boulevard", "Setor Jardim Boulevard", "Setor Jd Boulevard"],
    "Jardim América": ["Jardim Am", "Jardim América", "Setor Jardim Am", "Jardim America"],
    "Jardim da Luz": ["Jardim Dsa Luz", "Jardim da Luz", "Jardim da Luz Q", "Jardim da Luz Qd07 Lt02", "Jardim da Luz Qd17 Lt04", "Residencial Jardim da Luz", "Jardim Luz", "Setor Jardim da Luz", "Setor Jd da Luz"],
    "Jardim Eldorado": ["Jardim Eldorado", "Jardim Eldorado Q", "Residencial Dourado", "Setor Eldorado", "Setor Jardim Eldorado", "Setor Praca da Biblia"],
    "Jardim Guanabara": ["Jardim Guanaba", "Jardim Guanabara", "Jardim Guanabara Jd", "Jardim Guanabara Q05 L", "Jardim Guanabara Qd09", "Jardim Guanabara S", "Setor Guanabara", "Setor Guanabara Qd12 Lt07", "Setor Jardim Guabanara", "Setor Jardim Guanabara", "Setor Jd Guanabara"],
    "Jardim Medeiros": ["Jardim Medeiros", "Jardim Medeiros Q", "Setor Jardim Medeiros"],
    "Jardim Pauliceia": ["Jardim Pauliceia", "Jardim Pauliceia Qd7 Lt11", "Residencial Pauliceia", "Setor Pauliceia", "Setor Paulista"],
    "Jardim Flamboyant": ["Jardim Flamboian", "Jardim Flamboiant", "Jardim Flamboyan", "Jardim Flamboyant"],
    "Jardim Sevilha": ["Jardim Servilha", "Jardim Servilha Q", "Jardim Sevilha", "Setor Jardim Sevilha"],
    "Parque Res. Atalaia": ["Jardim Atalaia", "Parque Res Atalaia", "Parque Res Atalaya", "Parque Residencial A", "Parque Residencial Atalai", "Parque Residencial Atalaia", "Residencial Atalaia", "Residencial Atalaia Q", "Residencial Atalaya", "Setor Atalaia"],
    "Jardim Tocantins": ["Jardim Tocantins", "Jardim do Tocantins Av", "Setor Jardim Tocantins"],
    "Jardim Tocantins II": ["Jardim Tocantins II", "Jardim do Tocantins II", "Setor Jardim Tocantins II"],
    "Parque das Acacias": ["Parque das", "Parque das Ac", "Parque das Acacias", "Parque das Acacias Q", "Setor das Acacias", "Setor Parque das Acacias"],
    "Campo Bello": ["Residencial Campo Bello", "Residencial Campo Belo", "Residencial Campos Belos", "Setor Campo Belo"],
    "Residencial Daniela": ["Residencial Daneila", "Residencial Danele", "Residencial Daniela", "Residencial Daniela Q", "Residencial Daniela Qd01", "Residencial Daniela Qd01 Lt05", "Setor Daniela", "Setor Residencial Daniela"],
    "Setor Cajueiro": ["Residencial Cajueiro", "Residencial Cajueiros", "Parque Residencial Cajueiros", "Setor Cajueiro", "Setor Cajueiro Q", "Setor Cajueiros", "Setor Res Cajueiro"],
    "Setor Casego": ["Setor Casego", "Setor Cazego"],
    "Setor Alvorada": ["Setor Alvorada I", "Setor Alvorada II", "Residencial Alvorada", "Parque Alvorada", "Setor Alvorada"],
    "Setor Canaa": ["Setor Cana", "Setor Canaa", "Setor Canaa II - Pr", "Setor Cann", "Parque Residencial Cana", "Setor Canaã"],
    "Setor Aeroporto": ["Setor Aeroporto", "Setor Aeroporto Caixa Postal", "Setor Aeroporto Cx", "Setor Aeroporto III", "Setor Sol Aeroporto"],
    "Setor dos Funcionarios": ["Setor dos Funcion", "Setor dos Funcionários", "Setor dos Funcionarios Q", "Vila Funcion", "Vila Funcionários", "Setor Funcionários", "Setor Vila dos Funcion", "Vila dos Funcin", "Vila dos Funcion", "Vila dos Funcionário", "Vila dos Funcionarios", "Vila dos Funcionarios Q"],
    "Setor Cruzeiro": ["Setor Cruzeiro"],
    "Alto da Boa Vista": ["Setor Alto da Boa Vista", "Alto da Boa Vista"],
    "Park dos Buritis": ["Residencial Park dos Buriti", "Residencial Park dos Buritis", "Residencial Parque dos Buruti", "Park dos Buritis"],
    "Setor Inacio Loyola": ["Setor In", "Setor Inacio de Loiola", "Setor Inacio de Loyola", "Setor Inacio de Loyola Qd8 Lt32", "Setor Inacio Loyola"],
    "Centro": ["Setor Central", "Centro", "Bairro Central"],
    "Sol Nascente": ["Parque Residencial S", "Parque S", "Parque de Exposi", "Setor Pq Res S", "Setor Sol Nascente", "Setor Sol Nascente Qd13 Lt08", "Sol Nascente"],
    "Setor Industrial": ["Parque Agroindustrial", "Parque Industrial", "Setor Industrial"],
    "Setor Joao Lisboa da Cruz": ["Setor Jo", "Setor Joao L", "Setor Joao Lisboa da Cruz"],
    "Setor Jardim dos Buritis": ["Setor Jardim Buritis", "Setor Jardim dos Buritis"],
    "Setor Bom Sossego": ["Setor Bom Sossego", "Setor Bom Sossego Qr"],
    "Setor Boa Esperanca": ["Setor Boa Esperan", "Setor Boa Esperança", "Setor Boa Esperanca"],
    "Residencial Vale Verde": ["Residencial Vila Verde", "Residencial Vila Verde Q184 L", "Residencial Vl Verde", "Residencial Vale Verde", "Setor Vila Verde", "Setor Vila Verde Q", "Vila Verde", "Vale Verde"],
    "Setor Madrid": ["Residencial Madrid", "Setor Madrid"],
    "Residencial Sao Paulo": ["Residencial Sao Paulo", "Residencial Sao Paulo Q"],
    "Setor Sul II": ["Residencial Setor Sul II S", "Setor Sul II", "Setor Sul II Rua"],
    "Setor Sul": ["Setor Sul", "Setor Sul Qd2", "Setor Sul Qd30lt03"],
    "Setor Leste": ["Setor Leste", "Setor Leste C17 Q"],
    "Setor Malvinas": ["Setor Malvina", "Setor Malvinas", "Vila Malvinas"],
    "Setor Morada do Sol": ["Setor Morada do So", "Setor Morada do Sol", "Setor Morada do Sol Qwd", "Setor Morada do Sol Rua S", "Setor Morado do Sol"],
    "Setor Vale do Sol": ["Setor Vale do Sol", "Setor Vale do Sol Chac", "Setor Vale dos Sol"],
    "Setor Nova Fronteira": ["Setor Nova Fronteira", "Parque Residencial Nova Fronteira"],
    "Setor Paulo de Tarso": ["Setor Paulo de Tarso", "Setor Paulo de Tarso Atr", "Setor Paulo de Tarso Pr"],
    "Setor Jardim Tropical": ["Setor T", "Setor Tropical II", "Setor Jardim Tropical", "Jardim Tropical"],
    "Setor Santa Rita de Cassia": ["Setor Sta", "Setor Sta Rita", "Setor Sta Rita C", "Setor Sta Rita Cassia", "Setor Sta Rita de C", "Setor Sta Rita de Cassia", "Setor Sta Rita de Cassia Q", "Setor Santa Rita", "Setor Santa Rita C", "Setor Santa Rita Cassia", "Setor Santa Rita de C", "Setor Santa Rita de Cassia", "Setor Santa Rita de Cassia P", "Setor Santa Rita de Cassia Q", "Setor Santa Rita de Cassis", "Vila Sta Rita", "Setor Rita", "Setor Rita de C", "Setor Rita de Cassia", "Setor Sant Rita de Cass", "Setor Sant Rita de Cassia", "Setor Santa de Cassia", "Setor Jardim Santa Rita de Cassia"],
    "Vila Sao Jose": ["Setor Sao Jorge", "Setor Sao Jose", "Setor Sao Jose II", "Vila Sao Jos", "Vila Sao Jose", "Setor Vl Sao Jose", "Setor Vila Sao Jose"],
    "Setor Pedroso": ["Setor Pedroso", "Setor Pedroso Qd18 Lt10", "Setor Vila Pedroso", "Vila Pedroso"],
    "Setor Waldir Lins": ["Setor Valdir Lins", "Setor Waldir Lins"],
    "Vila Independencia": ["Vila Indeped", "Vila Indepencia", "Vila Independ", "Vila Independencia", "Vila Independencia Q", "Vila Independencia Qd08 Lt15", "Setor Vila Independ", "Setor Vila Independencia"],
    "Vila Nova": ["Vila Nova", "Vila Nova Q08", "Vila Nova Q14 L2", "Vila Nova Q22 L", "Vila Nova Sa", "Setor Vila Nova", "Setor Vila Nova Q20 Lt9", "Setor Vl Nova"],
    "Vila Colorin": ["Vila Colorin", "Vila Colorin Km"],
    "Vila Guaracy": ["Vila Guaraci", "Vila Guaracy", "Setor Vila Guaracy"],
    "Setor Matilde": ["Setor Matilde Qd13 Lt19", "Setor Matilde"],
    "Setor Novo Horizonte": ["Setor Novo Horizon", "Setor Novo Horizonte"],
    "Setor Santa Cruz": ["Setor Sant Acruz", "Setor Santa Cruz", "Setor Sata Cruz"],
    "Jardim Sao Lucas": ["Setor Jardim Sao Lucas", "Setor Sao Lucas", "Jardim Sao Lucas"],
    "Vila Alagoana": ["Setor Vila Alagoana", "Vila Alagoana", "Vila Alagona", "Vila Alogoana"],
    "Vila Pedestre": ["Vila Prdestre", "Vila Pedestre"],
    "Vila Iris": ["Setor Vila Iris", "Vila Iris"],
    "Setor Uniao": ["Setor Vila Uni", "Setor Uniao", "Vila Uniao", "St Uniao", "Setor Uniao V", "St. Uniao", "St Uniao V"],
    "Vila Paulista": ["Vila Paulista", "Vila Paulista Final Av", "Setor Vila Paulista"],
    "Vila Esperanca": ["Vila Esperan", "Vila Esperanca"],
    "Vila Mariano": ["Vila Mariano Qdd", "Vila Mariano"]
}

UNICOS = [
    "Vila Dom Pedro I", "Vila Militar", "Vila Minas", "Parque Residencial Sao Paulo",
    "Setor Santa Maria", "Setor Santa Rosa", "Setor Muniz Santana", "Setor Nossa Senhora da Abadia",
    "Setor Mansao do Cerrado", "Setor Condominio Santa Luzia", "Residencial Sao Jose", "Setor Aguas Claras",
    "Setor Alto dos Buritis", "Setor Antonio de Padua", "Setor Bela Vista", "Parque Primavera", "Setor Jardim Oriente"
]

RESIDENCIAIS = [
    "Residencial Alphaville", "Residencial Amazônia", "Residencial Bella Housing", "Residencial Buritis",
    "Residencial Galize", "Residencial Mineiro Apart", "Residencial Monte Sinai", "Residencial Morada das Flores",
    "Residencial Morada Verde", "Residencial Portal do Sol", "Residencial Portinari", "Residencial Rhuskaya",
    "Residencial Santa Catarina", "Residencial Senhor", "Residencial Solar Apartamento", "Residencial Vale do Sol",
    "Residencial Veneza", "Residencial Vit"
]

NAO_IDENTIFICADOS_TERMOS = [
    "Vila II", "Setor S", "Vila Res", "Setor Q Cl", "Setor Qcl", "Setor Res", "Setor Parq",
    "Residencial S", "Jardim S", "Parque", "Parque Q", "Parque Q 31l L", "Parque Q83 Lt20",
    "Parque R", "Parque Res", "Parque Residencial A", "Residencial", "Residencial de F",
    "Residencial Jo", "Setor J", "Setor Jad", "Setor Jd"
]

AVENIDAS_CENTRAIS_GURUPI = [
    'GOIAS', 'MARANHAO', 'PERNAMBUCO', 'PARA', 'PIAUI', 'CEARA', 'SANTA CATARINA',
    'RIO GRANDE DO SUL', 'RIO GRANDE DO NORTE', 'MINAS GERAIS', 'SAO PAULO', 'MATO GROSSO',
    'AMAZONAS', 'ALAGOAS', 'SERGIPE', 'GUANABARA', 'BRASILIA', 'BAHIA', 'RIO DE JANEIRO',
    'ESPIRITO SANTO', 'PARAIBA', 'ACRE', 'RONDONIA', 'RORAIMA'
]
RUAS_CENTRAIS_GURUPI = [
    'GETULIO VARGAS', 'JUSCELINO KUBITSCHEK', 'JK', 'CASTELO BRANCO', 'PEDRO LUDOVICO',
    'BERNARDO SAYAO', 'ALFREDO NASSER', 'ANTONIO LISBOA', 'EURIDICE RODRIGUES', 'ADELMO AIRES',
    'DEPUTADO JOSE DE ASSIS'
]

mapa_final = {}
todos_padroes_ordenados = []

for target, aliases in UNIFICACOES_USUARIO.items():
    t_norm = remover_acentos(target)
    mapa_final[t_norm] = target
    t_cut = cortar_em_q(target)
    if t_cut and len(t_cut) >= 3:
        mapa_final[remover_acentos(t_cut)] = target
        
    for a in aliases:
        a_norm = remover_acentos(a)
        mapa_final[a_norm] = target
        a_cut = cortar_em_q(a)
        if a_cut and len(a_cut) >= 3:
            mapa_final[remover_acentos(a_cut)] = target

for u in UNICOS:
    u_norm = remover_acentos(u)
    mapa_final[u_norm] = u
    u_cut = cortar_em_q(u)
    if u_cut and len(u_cut) >= 3:
        mapa_final[remover_acentos(u_cut)] = u

vistos_padroes = set()
for chave, target in mapa_final.items():
    if len(chave) >= 3 and chave not in vistos_padroes:
        vistos_padroes.add(chave)
        esc = re.escape(chave).replace(r'\ ', r'\s+')
        todos_padroes_ordenados.append((len(chave), re.compile(rf'\b{esc}\b', re.IGNORECASE), target))

todos_padroes_ordenados.sort(key=lambda x: x[0], reverse=True)

set_residenciais = {remover_acentos(r): r for r in RESIDENCIAIS}
set_nao_id = {remover_acentos(n) for n in NAO_IDENTIFICADOS_TERMOS}

mapeador_avs = [re.compile(rf'\b(?:AV\.?|AVENIDA)?\s*{re.escape(av)}\b', re.IGNORECASE) for av in AVENIDAS_CENTRAIS_GURUPI]
mapeador_ruas = [re.compile(rf'\b(?:RUA|R\.?)?\s*{re.escape(r)}\b', re.IGNORECASE) for r in RUAS_CENTRAIS_GURUPI]

def processar_bairro(endereco_raw):
    if not endereco_raw or not str(endereco_raw).strip():
        return "Não Identificado"
    
    end = str(endereco_raw).strip()
    end_limpo = re.sub(r'[\(\)\[\]\{\}\"\']', ' ', end)
    end_norm = remover_acentos(end_limpo)
    
    if re.search(r'\b(?:FAZENDA|FAZ\.?|FAZ\b|ZONA\s+RURAL|SITIO|CHACARA|CH\.?|GLEBA|ASSENTAMENTO|POVOADO)\b', end_norm):
        if not re.search(r'\b(?:SETOR|ST\.?|BAIRRO|JARDIM|JD\.?|RESIDENCIAL|RES\.?)\s+(?:CHACARA|FAZENDA)', end_norm):
            return "Zona Rural"
            
    cand = ""
    m = re.search(r'\b(?:bairro|st\.?|setor|jardim|jd\.?|pq\.?|parque|vila|vl\.?|res\.?|residencial)\s+([A-Za-z0-9\s\-]+)', end_limpo, re.IGNORECASE)
    if m:
        cand = m.group(0).strip(" ,-.;/\\")
    else:
        if re.search(r'(?:^|[,;\-\/\s])centro(?:\s*[,;\-\/]|\s*$)', end_limpo, re.IGNORECASE):
            if not re.search(r'\bcentro\s+(?:comunit[aá]rio|de\s+sa[uú]de|social|esp[ií]rita|comercial|cultural|m[eé]dico)\b', end_limpo, re.IGNORECASE):
                cand = "Centro"
        else:
            cand = end_limpo
            
    cand_cut = cortar_em_q(cand)
    cand_norm = remover_acentos(cand_cut)
    
    end_cut = cortar_em_q(end_limpo)
    end_cut_norm = remover_acentos(end_cut)
    
    res_bairro = None
    
    if cand_norm in mapa_final:
        res_bairro = mapa_final[cand_norm]
    elif cand_norm:
        for length, pat, target in todos_padroes_ordenados:
            if pat.search(cand_norm):
                res_bairro = target
                break
                
    if not res_bairro:
        if end_cut_norm in mapa_final:
            res_bairro = mapa_final[end_cut_norm]
        else:
            for length, pat, target in todos_padroes_ordenados:
                if pat.search(end_cut_norm):
                    res_bairro = target
                    break
                    
    if not res_bairro:
        for length, pat, target in todos_padroes_ordenados:
            if pat.search(end_norm):
                res_bairro = target
                break
                
    if not res_bairro:
        for r_norm, r_nome in set_residenciais.items():
            if r_norm in end_norm:
                res_bairro = r_nome
                break
                
    if res_bairro and remover_acentos(res_bairro) in set_nao_id:
        res_bairro = None
    if cand_norm in set_nao_id or end_cut_norm in set_nao_id:
        res_bairro = None

    eh_residencial = (res_bairro and remover_acentos(res_bairro) in set_residenciais)
    
    if not res_bairro or eh_residencial:
        for pat in mapeador_avs:
            if pat.search(end_norm):
                return "Centro [Estimado]"
        for pat in mapeador_ruas:
            if pat.search(end_norm):
                return "Centro [Estimado]"
        if re.search(r'\bBEIRA\s+RIO\b', end_norm):
            return "Setor Uniao [Estimado]"
        if re.search(r'\bGUAPORE\b', end_norm):
            return "Setor Leste [Estimado]"
            
    if res_bairro:
        return res_bairro
        
    return "Não Identificado"

# ====================================================
# Demais Funções de Processamento
# ====================================================

def calcular_idade_exata(data_nasc):
    if pd.isna(data_nasc):
        return None
    try:
        data = pd.to_datetime(data_nasc, dayfirst=True, errors='coerce')
        if pd.isna(data): return None
        hoje = datetime.now()
        idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
        if 0 <= idade <= 125:
            return int(idade)
        return None
    except:
        return None

@st.cache_data
def carregar_e_limpar(arquivo):
    if arquivo.name.endswith('.csv'):
        df = pd.read_csv(arquivo, dtype=str)
    else:
        df = pd.read_excel(arquivo, dtype=str)

    total_inicial = len(df)

    col_tel = next((c for c in df.columns if 'TELEFONE' in c.upper()), None)
    col_end = next((c for c in df.columns if 'ENDERE' in c.upper()), 'ENDEREÇO ELEITOR')
    col_nasc = next((c for c in df.columns if 'NASC' in c.upper()), 'DATA NASCIMENTO ELEITOR')
    col_nome = next((c for c in df.columns if 'NOME ELEITOR' in c.upper() or ('NOME' in c.upper() and 'MÃE' not in c.upper() and 'MAE' not in c.upper())), 'NOME ELEITOR')
    col_prof = next((c for c in df.columns if 'PROFIS' in c.upper()), 'PROFISSÃO ELEITOR')
    col_sexo = next((c for c in df.columns if 'SEXO' in c.upper() or 'GENERO' in c.upper() or 'GÊNERO' in c.upper()), None)

    # 1. Seleção Inteligente de Celular
    if col_tel:
        df['TELEFONE_HIGIENIZADO'] = df[col_tel].apply(selecionar_celular)
        df = df[df['TELEFONE_HIGIENIZADO'] != ""].copy()
    else:
        df['TELEFONE_HIGIENIZADO'] = ""

    total_com_celular = len(df)
    descartados = total_inicial - total_com_celular

    # 2. Exclusão das colunas solicitadas
    colunas_excluir = ['NUMERO ZONA', 'MUNICIPIO', 'NOME DA MÃE DO ELEITOR', 'NOME DA MAE DO ELEITOR', 'CPF ELEITOR']
    df = df.drop(columns=[col for col in colunas_excluir if col in df.columns], errors='ignore')

    # 3. Processamento dos Bairros
    if col_end in df.columns:
        df['BAIRRO_SETOR'] = df[col_end].apply(processar_bairro)
    else:
        df['BAIRRO_SETOR'] = "Não Identificado"

    # 4. Idade Numérica e Profissão
    if col_nasc in df.columns:
        df['IDADE'] = df[col_nasc].apply(calcular_idade_exata)
    else:
        df['IDADE'] = None

    if col_prof in df.columns:
        df['PROFISSÃO ELEITOR'] = df[col_prof].fillna('NÃO INFORMADO').str.strip().str.upper()
    else:
        df['PROFISSÃO ELEITOR'] = 'NÃO INFORMADO'

    if col_nome in df.columns and col_nome != 'NOME ELEITOR':
        df['NOME ELEITOR'] = df[col_nome]

    # 5. Classificação de Sexo / Gênero
    if col_sexo:
        df['SEXO'] = df.apply(lambda r: classificar_genero(r['NOME ELEITOR'], r[col_sexo]), axis=1)
    else:
        df['SEXO'] = df['NOME ELEITOR'].apply(classificar_genero)

    return df, total_inicial, descartados

# ====================================================
# Interface Visual (Streamlit)
# ====================================================
st.title("🎯 Painel de Segmentação & Filtro de Contatos")
st.markdown("Filtre contatos com precisão, consulte estatísticas em tempo real e exporte listas prontas.")

arquivo_upload = st.file_uploader("Selecione sua base de dados (.xlsx ou .csv):", type=['xlsx', 'csv'])

if arquivo_upload is not None:
    with st.spinner("Filtrando celulares válidos, classificando gênero e aplicando Mapeador de Gurupi..."):
        df, total_bruto, total_sem_telefone = carregar_e_limpar(arquivo_upload)

    # Indicadores
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Linhas no Arquivo", f"{total_bruto:,}")
    m2.metric("Contatos com Celular Válido", f"{len(df):,}")
    m3.metric("Descartados (Fixos / Sem Tel.)", f"{total_sem_telefone:,}")

    # Diagnóstico dos Bairros
    with st.expander("📍 Diagnóstico: Ver, Copiar ou Baixar Lista de Bairros Processados", expanded=False):
        df_bairros = df['BAIRRO_SETOR'].value_counts().reset_index()
        df_bairros.columns = ['Bairro / Região', 'Total de Contatos']
        
        col_tabela, col_copia = st.columns([1, 1])
        with col_tabela:
            st.dataframe(df_bairros, use_container_width=True, height=320)
            buf_bairros = io.BytesIO()
            with pd.ExcelWriter(buf_bairros, engine='openpyxl') as w:
                df_bairros.to_excel(w, index=False, sheet_name="Bairros")
            buf_bairros.seek(0)
            st.download_button(
                label="📥 Baixar Lista de Bairros em Excel (.xlsx)",
                data=buf_bairros,
                file_name="diagnostico_bairros_gurupi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col_copia:
            texto_copia = "\n".join([f"{r['Bairro / Região']} -> {r['Total de Contatos']} contatos" for _, r in df_bairros.iterrows()])
            st.text_area("Copie a relação completa abaixo:", value=texto_copia, height=320)

    # Filtros Laterais
    st.sidebar.header("🔍 Filtros de Segmentação")

    # Filtro de Bairro
    bairros_ordenados = sorted([b for b in df['BAIRRO_SETOR'].unique() if b not in ["Não Identificado", "Zona Rural", "Centro", "Centro [Estimado]"]])
    if "Centro" in df['BAIRRO_SETOR'].values:
        bairros_ordenados.insert(0, "Centro")
    if "Centro [Estimado]" in df['BAIRRO_SETOR'].values:
        bairros_ordenados.insert(1, "Centro [Estimado]")
    if "Zona Rural" in df['BAIRRO_SETOR'].values:
        bairros_ordenados.insert(2, "Zona Rural")
    if "Não Identificado" in df['BAIRRO_SETOR'].values:
        bairros_ordenados.append("Não Identificado")

    sel_bairros = st.sidebar.multiselect("Bairro / Região:", options=bairros_ordenados)

    # Filtro de Sexo / Gênero
    opcoes_sexo = [s for s in ['Feminino', 'Masculino', 'Não Identificado'] if s in df['SEXO'].values]
    sel_sexo = st.sidebar.multiselect("Sexo / Gênero:", options=opcoes_sexo)

    # Filtro de Profissão
    profissoes_disponiveis = sorted(df['PROFISSÃO ELEITOR'].unique())
    sel_profissoes = st.sidebar.multiselect("Profissão:", options=profissoes_disponiveis)

    # Filtro Numérico de Idade
    st.sidebar.subheader("🎂 Filtro por Idade")
    idades_validas = df['IDADE'].dropna()
    min_sistema = int(idades_validas.min()) if not idades_validas.empty else 16
    max_sistema = int(idades_validas.max()) if not idades_validas.empty else 100

    col_id_ini, col_id_fim = st.sidebar.columns(2)
    with col_id_ini:
        idade_inicial = st.number_input("Idade Inicial:", min_value=0, max_value=120, value=min_sistema, step=1)
    with col_id_fim:
        idade_final = st.number_input("Idade Final:", min_value=0, max_value=120, value=max_sistema, step=1)

    ativar_filtro_idade = st.sidebar.checkbox("Ativar filtro de idade", value=False)
    incluir_sem_idade = st.sidebar.checkbox("Incluir contatos sem data informada", value=False)

    termo_busca = st.sidebar.text_input("Buscar por Nome do Eleitor:")

    # Aplicação dos Filtros
    df_filtrado = df.copy()

    if sel_bairros:
        df_filtrado = df_filtrado[df_filtrado['BAIRRO_SETOR'].isin(sel_bairros)]
    if sel_sexo:
        df_filtrado = df_filtrado[df_filtrado['SEXO'].isin(sel_sexo)]
    if sel_profissoes:
        df_filtrado = df_filtrado[df_filtrado['PROFISSÃO ELEITOR'].isin(sel_profissoes)]

    if ativar_filtro_idade:
        if idade_inicial > idade_final:
            st.sidebar.error("A Idade Inicial não pode ser maior que a Final.")
        else:
            condicao_idade = (df_filtrado['IDADE'] >= idade_inicial) & (df_filtrado['IDADE'] <= idade_final)
            if incluir_sem_idade:
                df_filtrado = df_filtrado[condicao_idade | df_filtrado['IDADE'].isna()]
            else:
                df_filtrado = df_filtrado[condicao_idade]

    if termo_busca:
        df_filtrado = df_filtrado[df_filtrado['NOME ELEITOR'].str.contains(termo_busca, case=False, na=False)]

    st.markdown("---")

    # Resumo Estatístico
    c1, c2, c3 = st.columns(3)
    c1.metric("Base Ativa com Celular", f"{len(df):,} contatos")
    c2.metric("Total Selecionado", f"{len(df_filtrado):,} contatos")
    pct = (len(df_filtrado) / len(df)) * 100 if len(df) > 0 else 0
    c3.metric("Representatividade", f"{pct:.2f}%")

    if ativar_filtro_idade:
        if idade_inicial == idade_final:
            st.info(f"📊 Filtrando eleitores com exatamente **{idade_inicial} anos**: **{len(df_filtrado)} pessoas** encontradas.")
        else:
            st.info(f"📊 Filtrando eleitores de **{idade_inicial} a {idade_final} anos**: **{len(df_filtrado)} pessoas** encontradas.")

    # Tabela Prévia
    st.subheader("📋 Prévia dos Registros Filtrados")
    df_preview = df_filtrado[['NOME ELEITOR', 'SEXO', 'TELEFONE_HIGIENIZADO', 'PROFISSÃO ELEITOR', 'BAIRRO_SETOR', 'IDADE']].copy()
    df_preview['IDADE'] = df_preview['IDADE'].apply(lambda x: f"{int(x)} anos" if pd.notna(x) else "Não informada")
    st.dataframe(df_preview.head(100), use_container_width=True)

    # Seção de Exportação Personalizada
    st.markdown("---")
    st.subheader("📤 Exportar Lista Segmentada")

    col_nome_lista, col_marcador = st.columns(2)
    with col_nome_lista:
        nome_lista_input = st.text_input("Qual o nome desta LISTA? (Ex: mulheres_vila_nova, advogados, etc.):", value="")
    with col_marcador:
        st.text_input("MARCADOR:", value="ListaE", disabled=True)

    if st.button("Gerar Arquivo para Download"):
        if not nome_lista_input.strip():
            st.warning("Informe o nome da LISTA antes de baixar a planilha.")
        elif len(df_filtrado) == 0:
            st.error("Nenhum contato encontrado com os filtros atuais.")
        else:
            df_exportar = pd.DataFrame({
                'NOME': df_filtrado['NOME ELEITOR'].values,
                'TELEFONE 1': df_filtrado['TELEFONE_HIGIENIZADO'].values,
                'TELEFONE 2': [''] * len(df_filtrado),
                'TELEFONE 3': [''] * len(df_filtrado),
                'LISTA': nome_lista_input.strip(),
                'MARCADOR': 'ListaE'
            })

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_exportar.to_excel(writer, index=False, sheet_name="Contatos")
            buffer.seek(0)

            st.success(f"Tudo pronto! {len(df_exportar)} contatos preparados.")
            st.download_button(
                label=f"⬇️ Baixar Planilha ({nome_lista_input.strip()}.xlsx)",
                data=buffer,
                file_name=f"{nome_lista_input.strip().lower().replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Suba sua planilha acima para visualizar os dados, filtros e estatísticas.")