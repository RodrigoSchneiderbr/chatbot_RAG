import os
import re
from collections import defaultdict
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document

# IMPORTAÇÕES OFICIAIS ATUALIZADAS
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

DIRETORIO_DOCS = "documentos"
DIRETORIO_CHROMA = "banco_vetorial/chroma_db"

url_ollama = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def normalizar_texto_artigos(texto: str) -> str:
    """
    Remove zeros à esquerda de números de artigos e padroniza a escrita.
    """
    # 1. Transforma "Art. 0X" ou "Art. X" em "Artigo X" e remove os zeros à esquerda
    texto_limpo = re.sub(r'(?i)\bart\.\s+0*(\d+)\b', r'Artigo \1', texto)
    
    # 2. Transforma "Artigo 0X" em "Artigo X" (remove os zeros à esquerda mantendo a palavra Artigo)
    texto_limpo = re.sub(r'(?i)\bartigo\s+0*(\d+)\b', r'Artigo \1', texto_limpo)
    
    return texto_limpo

def fatiar_por_artigo(texto_completo: str, nome_arquivo: str) -> list[Document]:
    """
    Divide o texto completo do documento usando os Artigos como divisores.
    Retorna uma lista de objetos Document com metadados ricos (como o número do artigo).
    """
    # Primeiro, aplicamos a normalização em todo o texto para garantir consistência
    texto_normalizado = normalizar_texto_artigos(texto_completo)
    
    # Expressão regular para encontrar "Artigo X" (captura o número no grupo 1)
    padrao_artigo = r'(?i)\bArtigo\s+(\d+)\b'
    
    # Encontra todas as ocorrências de artigos no texto
    artigos_encontrados = list(re.finditer(padrao_artigo, texto_normalizado))
    
    documentos_fatiados = []
    
    if not artigos_encontrados:
        # Se não encontrar nenhum artigo estruturado, trata o texto como um bloco único
        print(f"⚠️ Nenhum artigo estruturado encontrado em {nome_arquivo}. Salvando como bloco único.")
        return [Document(
            page_content=texto_normalizado, 
            metadata={"source": nome_arquivo, "tipo": "geral"}
        )]
    
    for i, match in enumerate(artigos_encontrados):
        numero_artigo = int(match.group(1)) # Pega o número do artigo (ex: 2)
        inicio_bloco = match.start()
        
        # O fim deste bloco é o início do próximo artigo (ou o fim do texto)
        fim_bloco = artigos_encontrados[i + 1].start() if i + 1 < len(artigos_encontrados) else len(texto_normalizado)
        
        # Extrai o texto completo do artigo correspondente
        texto_artigo = texto_normalizado[inicio_bloco:fim_bloco].strip()
        
        # Criamos o objeto Document do LangChain injetando o metadado do número do artigo
        doc = Document(
            page_content=texto_artigo,
            metadata={
                "source": nome_arquivo,
                "artigo": numero_artigo,
                "tipo": "artigo"
            }
        )
        documentos_fatiados.append(doc)
        
    return documentos_fatiados

def realizar_ingestao():
    print("--- INICIANDO INGESTÃO ESTRUTURADA DE DOCUMENTOS ---")
    
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

    # =====================================================================
    # 1. AGRUPAR PÁGINAS POR ARQUIVO PARA EVITAR CORTES NO MEIO DE ARTIGOS
    # =====================================================================
    print("Agrupando páginas por documento original...")
    conteudo_por_arquivo = defaultdict(list)
    for doc in documentos_brutos:
        origem = doc.metadata.get("source", "desconhecido")
        conteudo_por_arquivo[origem].append(doc.page_content)

    # =====================================================================
    # 2. FATIAR CADA ARQUIVO POR ARTIGO INTEIRO E INJETAR METADADOS
    # =====================================================================
    print("Fatiando documentos por artigos estruturados...")
    documentos_divididos = []
    for origem, paginas in conteudo_por_arquivo.items():
        # Junta todas as páginas do arquivo em uma única string de texto completo
        texto_completo = "\n\n".join(paginas)
        nome_arquivo = os.path.basename(origem)
        
        # Divide o documento completo em artigos estruturados
        chunks_do_arquivo = fatiar_por_artigo(texto_completo, nome_arquivo)
        documentos_divididos.extend(chunks_do_arquivo)

    print(f"Total de artigos individuais indexados: {len(documentos_divididos)}")

    # Configura os Embeddings (Ollama) usando a classe atualizada
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=url_ollama)

    # Salva o banco vetorial no disco
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