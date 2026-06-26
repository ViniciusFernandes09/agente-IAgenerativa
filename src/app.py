import json
import pandas as pd
import requests
import streamlit as st

# ========= CONFIGURAÇÃO =========
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "minimax-m3:cloud"

# ========= CARREGAR DADOS =========
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))

# ============ MONTAR CONTEXTO ============
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade' ]} anos,
perfil {perfil['perfil_investidor']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil[ 'reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONIVEIS:
{json.dumps (produtos, indent=2, ensure_ascii=False)}
"""

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """ Voce é a Let, uma educadora financeira amigavel e didática.

OBJETIVO:|
Ensinar conceitos de finanças pessoais de forma simples, usando os dados do cliente como exemplos praticos.

REGRAS:
- NUNCA recomende investimentos especificos, apenas explique como funcionam;
- JAMAIS responda a pergunta fora do tema ensino de finanças pessoais.
- Quando ocorrer, responda lembrando o seu papel de educador financeiro.
- Use os dados fornecidos para dar exemplos personalizados;
- Linguagem simples, como se explicasse para um amigo;
- Se não souber algo, admita: "Nao tenho essa informação, mas posso Explicar ... ";
- Sempre pergunte se o cliente entendeu;
- Responda de forma sucinta e direta, com no máximo 3 parágrafos.
"""

# ============ CHAMAR OLLAMA ============
def perguntar(msg):
    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""

    r = requests.post(OLLAMA_URL, json={"model": MODELO, "prompt": prompt, "stream": False})
    return r.json()['response']

# ============ INTERFACE ============
st.title("🎓 Let, sua Educadora Financeira!")

# Inicializa histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra histórico completo
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
pergunta = st.chat_input("Sua dúvida sobre finanças...")

if pergunta:

    # Adiciona pergunta ao histórico
    st.session_state.messages.append({
        "role": "user",
        "content": pergunta
    })

    # Mostra imediatamente a pergunta
    with st.chat_message("user"):
        st.markdown(pergunta)

    # Gera resposta
    with st.spinner("Pensando..."):
        resposta = perguntar(pergunta)

    # Mostra resposta
    with st.chat_message("assistant"):
        st.markdown(resposta)

    # Salva resposta
    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta
    })