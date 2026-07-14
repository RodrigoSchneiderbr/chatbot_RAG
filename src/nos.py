from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage


from src.estado_do_agente import EstadoDoAgente
from src.recuperador import recuperador

# ==========================================
# CONFIGURAÇÃO DO LLM preciso testar melhores
# ==========================================
llm = Ollama(model="llama3.1", temperature=0) 

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
    print("--- NÓ: GERANDO RESPOSTA COM OLLAMA ---")
    
    documentos = estado["documentos"]
    historico = estado["mensagens"]
    pergunta_atual = historico[-1].content
    
    # Formata os documentos em um único grande bloco de texto
    contexto = "\n\n---\n\n".join(documentos)
    
    # Formata as mensagens anteriores (se houver) para o modelo ter memória da conversa
    historico_formatado = "\n".join([
        f"{'Usuário' if isinstance(m, HumanMessage) else 'Assistente'}: {m.content}" 
        for m in historico[:-1] # Ignora a última mensagem, pois é a pergunta atual
    ])
    
    # O Prompt Mestre que controla o comportamento do LLM
    prompt = f"""Você é um assistente corporativo especialista em analisar documentos.
Use EXCLUSIVAMENTE o "Contexto do Documento" abaixo para responder à "Pergunta Atual" do usuário.
Se a informação não estiver no contexto, diga claramente que não encontrou a resposta no documento. Não invente informações.
Use o "Histórico da Conversa" apenas se precisar de contexto sobre o que já foi falado.

Histórico da Conversa:
{historico_formatado if historico_formatado else "Esta é a primeira mensagem da conversa."}

Contexto do Documento:
{contexto}

Pergunta Atual: {pergunta_atual}

Resposta:"""
    
    # Chama o Ollama local para ler tudo e gerar o texto
    resposta_texto = llm.invoke(prompt)
    
    # Atualiza o estado: o 'operator.add' que configuramos no estado.py vai
    # anexar esta AIMessage ao final da lista de mensagens automaticamente
    return {"mensagens": [AIMessage(content=resposta_texto)]}