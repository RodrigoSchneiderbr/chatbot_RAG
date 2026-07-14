# 🤖 Assistente RAG Corporativo (Local & Privado)

Um assistente virtual inteligente capaz de ler, interpretar e responder perguntas sobre documentos corporativos (PDFs e Words) garantindo 100% de privacidade dos dados, rodando modelos de IA localmente.

## 🌟 Funcionalidades
* **100% Local e Privado:** Nenhum dado da sua empresa vai para a internet. O processamento é feito localmente usando [Ollama](https://ollama.com/).
* **Busca Híbrida (Híbrid Search):** Combina busca semântica (ChromaDB) com busca exata de palavras-chave (BM25) para encontrar códigos e siglas com precisão.
* **Memória de Conversação:** O agente lembra do contexto das perguntas anteriores através do `MemorySaver` do LangGraph.
* **Interface Web:** Interface amigável em chat construída com Streamlit, com suporte a upload de documentos direto pela tela.
* **Pronto para Docker:** Arquitetura empacotada em contêiner para fácil implantação.

## 🛠️ Tecnologias Utilizadas
* **Python 3.11+**
* **LangChain & LangGraph** (Orquestração do Agente e Grafo)
* **ChromaDB** (Banco de Dados Vetorial)
* **Ollama** (Motor de LLM Local - Llama 3 / Mistral)
* **Streamlit** (Interface Gráfica)
* **Docker** (Containerização)

---

## 🚀 Como instalar e rodar localmente

### 1. Pré-requisitos
* Ter o Python instalado.
* Ter o [Ollama](https://ollama.com/) instalado e rodando na sua máquina.

### 2. Configuração do Ambiente
Clone o repositório e crie um ambiente virtual:
```text
git clone [https://github.com/RodrigoSchneiderbr/chatbot_RAG.git](https://github.com/RodrigoSchneiderbr/chatbot_RAG.git)
cd chatbot_RAG
python -m venv venv
source venv/bin/activate### 3. Instalação das Dependências
```

Instalar as dependencias

```text
pip install -r requirements.txt
```

### 3. Baixar Modelo de IA

``` text
ollama pull llama3.1
ollama pull nomic-embed-text
```

### 4. Rodando Local

``` text
streamlit run app.py
```

### 5. 🐳 Como rodar com Docker

```
# 1. Construir a imagem
docker build -t assistente-rag .

# 2. Rodar o contêiner
docker run -p 8501:8501 -e OLLAMA_BASE_URL="[http://host.docker.internal:11434](http://host.docker.internal:11434)" assistente-rag
````

Acesse http://localhost:8501

Arquitetura e estrutura do projeto

``` text
chatbot_RAG/
├── .streamlit/             # Configurações da interface
├── banco_vetorial/         # Onde o ChromaDB salva os dados
├── documentos/             # Pasta para os PDFs e DOCXs
├── src/
│   ├── app.py              # Front-end (Streamlit)
│   ├── agente.py           # Orquestrador (LangGraph)
│   ├── nos.py              # Ferramentas do Agente (LLM)
│   ├── recuperador.py      # Busca Híbrida (BM25 + Vetorial)
│   ├── ingestao.py         # Processamento de PDFs
│   └── estado.py           # Definição de Memória
├── .gitignore
├── Dockerfile
└── requirements.txt
```
