import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document

DIRETORIO_CHROMA = "banco_vetorial/chroma_db"
url_ollama = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def configurar_recuperador_hibrido():
    print("Conectando ao banco de dados e configurando buscadores...")
    
    #  Recria a função de Embeddings do Ollama
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=url_ollama)
    
    # Conecta ao ChromaDB existente no disco
    vectorstore = Chroma(
        persist_directory=DIRETORIO_CHROMA,
        embedding_function=embeddings,
        collection_name="meu_rag_documentos"
    )
    
    # Configura o Buscador Vetorial (Semântico)
    retriever_vetorial = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # Puxa os documentos do ChromaDB para configurar o BM25
    dados_chroma = vectorstore.get()
    textos = dados_chroma["documents"]
    metadados = dados_chroma.get("metadatas", [{}] * len(textos))
    
    # SE O BANCO ESTIVER VAZIO: Devolve apenas o buscador vetorial para não travar o app
    if not textos:
        print("⚠️ AVISO: O banco está vazio. A interface vai abrir, mas você precisa fazer o upload de documentos!")
        return retriever_vetorial

    # Se tiver textos, segue a vida normalmente criando o BM25...
    documentos_para_bm25 = [
        Document(page_content=txt, metadata=meta)
        for txt, meta in zip(textos, metadados)
    ]
    
    # Configura o Buscador por Palavras-Chave (BM25)
    retriever_bm25 = BM25Retriever.from_documents(documentos_para_bm25)
    retriever_bm25.k = 3
    
    #  Cria o Buscador Híbrido (Ensemble) configuração para respostas exatas, mais restritas, mas depende de teste
    retriever_hibrido = EnsembleRetriever(
        retrievers=[retriever_vetorial, retriever_bm25],
        weights=[0.5, 0.5]
    )
    
    return retriever_hibrido

# Instância pronta para ser importada por outros arquivos
recuperador = configurar_recuperador_hibrido()