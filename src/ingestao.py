import os
import re
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. IMPORTAÇÕES ATUALIZADAS E OFICIAIS
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

DIRETORIO_DOCS = "documentos"
DIRETORIO_CHROMA = "banco_vetorial/chroma_db"

url_ollama = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def normalizar_texto_artigos(texto: str) -> str:
    """
    Remove zeros à esquerda de números de artigos e padroniza a escrita.
    """
    texto_limpo = re.sub(r'(?i)\bart\.\s+0*(\d+)\b', r'Artigo \1', texto)
    texto_limpo = re.sub(r'(?i)\bartigo\s+0*(\d+)\b', r'Artigo \1', texto_limpo)
    return texto_limpo

def realizar_ingestao():
    print("--- INICIANDO INGESTÃO DE DOCUMENTOS ---")
    
    if not os.path.exists(DIRETORIO_DOCS):
        os.makedirs(DIRETORIO_DOCS)
        print(f"Pasta '{DIRETORIO_DOCS}' criada na raiz do projeto.")
        print("Por favor, coloque seus PDFs e Words dentro dela e rode este script novamente.")
        return

    documentos_brutos = []
    
    arquivos_na_pasta = os.listdir(DIRETORIO_DOCS)
    
    for arquivo in arquivos_na_pasta:
        caminho_completo = os.path.join(DIRETORIO_DOCS, arquivo)
        
        if arquivo.endswith(".pdf"):
            print(f"Lendo PDF: {arquivo}...")
            loader = PyPDFLoader(caminho_completo)
            documentos_brutos.extend(loader.load())
            
        elif arquivo.endswith(".docx"):
            print(f"Lendo Word: {arquivo}...")
            loader = Docx2txtLoader(caminho_completo)
            documentos_brutos.extend(loader.load())
            
    if not documentos_brutos:
        print(f"Nenhum arquivo .pdf ou .docx encontrado na pasta '{DIRETORIO_DOCS}'.")
        return

    print(f"\nTotal de páginas/seções extraídas: {len(documentos_brutos)}")

    # ==========================================
    # 2. APLICANDO A NORMALIZAÇÃO ANTES DE FATIAR (CORREÇÃO AQUI!)
    # ==========================================
    print("Padronizando numeração dos artigos (removendo zeros à esquerda)...")
    for doc in documentos_brutos:
        doc.page_content = normalizar_texto_artigos(doc.page_content)

    # Divide os documentos em pedaços (Chunks)
    print("Dividindo o texto em pedaços menores...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documentos_divididos = text_splitter.split_documents(documentos_brutos)
    print(f"Documentos divididos em {len(documentos_divididos)} pedaços.")

    # Configura os Embeddings (Ollama) usando a classe oficial
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=url_ollama)

    # Cria e salva o banco vetorial no disco (Persistência)
    print("\nGerando embeddings matemáticos e salvando no ChromaDB.")
    print("Aguarde, isso pode levar alguns minutos dependendo do tamanho dos PDFs...")
    
    Chroma.from_documents(
        documents=documentos_divididos,
        embedding=embeddings,
        persist_directory=DIRETORIO_CHROMA,
        collection_name="meu_rag_documentos"
    )
    
    print("\n--- INGESTÃO CONCLUÍDA COM SUCESSO! ---")
    print(f"Banco de dados salvo com segurança em: {DIRETORIO_CHROMA}")

if __name__ == "__main__":
    realizar_ingestao()