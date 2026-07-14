import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.estado_do_agente import EstadoDoAgente
from src.recuperador import recuperador

# ==========================================
# CONFIGURAÇÃO DO LLM (Usando ChatOllama)
# ==========================================
url_ollama = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Usar ChatOllama melhora drasticamente a interpretação de prompts no Llama 3.1
llm = ChatOllama(model="llama3.1", temperature=0, base_url=url_ollama)

# ==========================================
# NÓ 1: BUSCAR DOCUMENTOS
# ==========================================
def buscar_documentos(estado: EstadoDoAgente):
    print("\n--- NÓ: BUSCANDO DOCUMENTOS (HÍBRIDO) ---")
    
    # Pega o texto da última mensagem enviada pelo usuário
    pergunta_atual = estado["mensagens"][-1].content
    
    # Usa o nosso buscador híbrido (Vetorial + Palavras-chave)
    docs_recuperados = recuperador.invoke(pergunta_atual)
    
    # Extrai apenas o texto útil dos documentos encontrados
    textos_docs = [doc.page_content for doc in docs_recuperados]
    print(f"[{len(textos_docs)} trechos recuperados do banco de dados]")
    
    # Atualiza o estado: substitui a lista de documentos antiga pela nova
    return {"documentos": textos_docs}

# ==========================================
# NÓ 2: GERAR RESPOSTA
# ==========================================
def gerar_resposta(estado: EstadoDoAgente):
    print("\n--- NÓ: GERANDO RESPOSTA COM OLLAMA ---")
    
    # Evita quebrar se a chave "documentos" não existir por algum motivo no estado
    documentos = estado.get("documentos", [])
    
    # 🔍 PRINT DE DIAGNÓSTICO IMPORTANTE:
    print(f"[DEBUG GERAÇÃO] Quantidade de documentos recebidos no estado: {len(documentos)}")
    if len(documentos) == 0:
        print("[ALERTA CRÍTICO] O nó de geração não recebeu nenhum documento do estado! Verifique o seu grafo/estado.")
    else:
        print("[DEBUG GERAÇÃO] Conteúdo do primeiro trecho enviado ao modelo:")
        print(f" >>> {documentos[0][:150]}...") # Printa os primeiros 150 caracteres para teste
    
    historico = estado["mensagens"]
    pergunta_atual = historico[-1].content
    
    # Formata os documentos em um único grande bloco de texto
    contexto = "\n\n---\n\n".join(documentos)
    
    # Formata as mensagens anteriores (se houver) para o modelo ter memória da conversa
    historico_formatado = "\n".join([
        f"{'Usuário' if isinstance(m, HumanMessage) else 'Assistente'}: {m.content}" 
        for m in historico[:-1] # Ignora a última mensagem, pois é a pergunta atual
    ])
    
    # Criamos as instruções do sistema de forma estruturada (SystemMessage)
    instrucoes_sistema = f"""Você é um assistente corporativo especialista em analisar documentos.
Use EXCLUSIVAMENTE o "Contexto do Documento" abaixo para responder à pergunta do usuário.
Se a informação não estiver descrita no contexto fornecido, diga exatamente: "Não encontrei essa informação no documento." Não tente inventar fatos ou usar conhecimento externo.

Histórico da Conversa:
{historico_formatado if historico_formatado else "Esta é a primeira mensagem da conversa."}

Contexto do Documento:
{contexto}"""

    # Enviamos como mensagens estruturadas para o Llama 3.1
    mensagens_para_o_llm = [
        SystemMessage(content=instrucoes_sistema),
        HumanMessage(content=pergunta_atual)
    ]
    
    # Invoca o modelo de chat
    resposta = llm.invoke(mensagens_para_o_llm)
    resposta_texto = resposta.content
    
    # Atualiza o estado anexando a resposta à lista de mensagens
    return {"mensagens": [AIMessage(content=resposta_texto)]}