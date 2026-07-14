import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

DIRETORIO_DOCS = "documentos"
DIRETORIO_CHROMA = "banco_vetorial/chroma_db"

url_ollama = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def realizar_ingestao():
    print("--- INICIANDO INGESTÃO DE DOCUMENTOS ---")
    
    # 1. Verifica se a pasta de documentos existe, se não, cria.
    if not os.path.exists(DIRETORIO_DOCS):
        os.makedirs(DIRETORIO_DOCS)
        print(f"Pasta '{DIRETORIO_DOCS}' criada na raiz do projeto.")
        print("Por favor, coloque seus PDFs e Words dentro dela e rode este script novamente.")
        return

    documentos_brutos = []
    
    #Varre a pasta lendo todos os arquivos suportados
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

    # Divide os documentos em pedaços (Chunks)
    print("Dividindo o texto em pedaços menores...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documentos_divididos = text_splitter.split_documents(documentos_brutos)
    print(f"Documentos divididos em {len(documentos_divididos)} pedaços.")

    # Configura os Embeddings (Ollama)
    embeddings = OllamaEmbeddings(model="nomic-embed-text",base_url=url_ollama)

    # Cria e salva o banco vetorial no disco (Persistência)
    print("\nGerando embeddings matemáticos e salvando no ChromaDB.")
    print("Aguarde, isso pode levar alguns minutos dependendo do tamanho dos PDFs...")
    
    # O parâmetro persist_directory é o que garante que os dados serão salvos na pasta
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