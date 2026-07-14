import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import uuid
from langchain_core.messages import HumanMessage

# Importa o agente e a função de ingestão!
from src.agente import agente
from src.ingestao import realizar_ingestao

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="RAG Corporativo", page_icon="🤖")
st.title("🤖 Assistente de Documentos")
st.markdown("Faça perguntas sobre os documentos indexados na base de conhecimento.")

# ==========================================
# BARRA LATERAL (UPLOAD DE ARQUIVOS)
# ==========================================
with st.sidebar:
    st.header("📂 Gerenciar Documentos")
    st.write("Adicione novos arquivos para a IA ler.")
    
    # Componente de upload múltiplo
    arquivos_upados = st.file_uploader(
        "Faça upload de PDFs ou Words", 
        type=["pdf", "docx"], 
        accept_multiple_files=True
    )
    
    # Botão para iniciar o processamento
    if st.button("Processar Documentos"):
        if arquivos_upados:
            with st.spinner("Salvando e gerando base matemática... Isso pode demorar."):
                # 1. Garante que a pasta física existe
                os.makedirs("documentos", exist_ok=True)
                
                # 2. Salva os arquivos que vieram do navegador na pasta local
                for arquivo in arquivos_upados:
                    caminho_salvar = os.path.join("documentos", arquivo.name)
                    with open(caminho_salvar, "wb") as f:
                        f.write(arquivo.getbuffer())
                
                # 3. Chama a nossa função mágica de ingestão!
                realizar_ingestao()
                
                st.success("✅ Ingestão concluída!")
                st.info("⚠️ Dica: Como a busca por palavras-chave (BM25) fica na memória RAM, pare o aplicativo no terminal (Ctrl+C) e rode novamente para que ele leia os novos documentos.")
        else:
            st.warning("Selecione pelo menos um arquivo antes de processar.")

# ==========================================
# GERENCIAMENTO DE ESTADO (SESSÃO)
# ==========================================
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "mensagens_ui" not in st.session_state:
    st.session_state.mensagens_ui = []

# ==========================================
# RENDERIZAÇÃO DO HISTÓRICO NO CHAT
# ==========================================
for msg in st.session_state.mensagens_ui:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# CAPTURA DE ENTRADA E EXECUÇÃO DO AGENTE
# ==========================================
pergunta_usuario = st.chat_input("Digite sua pergunta...")

if pergunta_usuario:
    with st.chat_message("user"):
        st.markdown(pergunta_usuario)
    
    st.session_state.mensagens_ui.append({"role": "user", "content": pergunta_usuario})
    
    with st.chat_message("assistant"):
        with st.spinner("Analisando documentos..."):
            try:
                configuracao_memoria = {"configurable": {"thread_id": st.session_state.thread_id}}
                estado_entrada = {"mensagens": [HumanMessage(content=pergunta_usuario)]}
                
                resultado = agente.invoke(estado_entrada, config=configuracao_memoria)
                resposta_assistente = resultado["mensagens"][-1].content
                
                st.markdown(resposta_assistente)
                st.session_state.mensagens_ui.append({"role": "assistant", "content": resposta_assistente})
                
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")