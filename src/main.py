import uuid
from langchain_core.messages import HumanMessage

from src.agente import agente

def iniciar_chat():
    print("="*60)
    print("🤖 ASSISTENTE RAG CORPORATIVO (Ollama + ChromaDB)")
    print("="*60)
    print("Digite sua pergunta sobre os documentos.")
    print("Para sair, digite 'sair', 'quit' ou 'exit'.\n")

    # Criamos um ID de conversa (thread_id) aleatório para esta sessão.
    id_sessao = str(uuid.uuid4())
    configuracao_memoria = {"configurable": {"thread_id": id_sessao}}

    # Inicia o loop infinito do chat
    while True:
        #  Captura a pergunta do usuário
        pergunta_usuario = input("👤 Você: ")
        
        # Verifica se o usuário quer sair
        if pergunta_usuario.lower() in ['sair', 'quit', 'exit']:
            print("\nEncerrando o assistente. Até logo!")
            break
            
        # Ignora envios vazios (se o usuário apertar Enter sem querer)
        if not pergunta_usuario.strip():
            continue

        print("\n⏳ Assistente analisando documentos...")
        
        try:
            # Monta o estado inicial e aciona o agente
            estado_entrada = {"mensagens": [HumanMessage(content=pergunta_usuario)]}
            
            # O invoke processa todo o LangGraph e retorna o estado atualizado
            resultado_final = agente.invoke(estado_entrada, config=configuracao_memoria)
            
            # Extrai a última mensagem adicionada (que é a AIMessage do Ollama)
            resposta = resultado_final["mensagens"][-1].content
            
            print(f"\n🤖 Assistente:\n{resposta}\n")
            print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ Ocorreu um erro durante a execução: {e}\n")

if __name__ == "__main__":
    iniciar_chat()