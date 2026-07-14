from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Importações dos nossos próprios arquivos
from src.estado_do_agente import EstadoDoAgente
from src.nos import buscar_documentos, gerar_resposta

def construir_agente():
    print("Montando o grafo do LangGraph...")
    
    # Inicializa o Grafo passando o formato do Estado
    grafo = StateGraph(EstadoDoAgente)
    
    # Adiciona os Nós 
    grafo.add_node("buscar", buscar_documentos)
    grafo.add_node("gerar", gerar_resposta)
    
    # Define o Fluxo 
    grafo.set_entry_point("buscar")        
    grafo.add_edge("buscar", "gerar")      
    grafo.add_edge("gerar", END)           
    
    # Configura a Memória da Conversa
    # O MemorySaver guarda o estado localmente para permitir perguntas de acompanhamento
    memoria = MemorySaver()
    
    # 5. Compila o Agente final unindo o grafo e a memória
    agente_compilado = grafo.compile(checkpointer=memoria)
    
    return agente_compilado

# Cria a instância do agente pronta para ser usada no main.py
agente = construir_agente()