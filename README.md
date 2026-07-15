# 🤖 Assistente RAG Corporativo (Local & Privado)

Um assistente virtual inteligente capaz de ler, interpretar e responder perguntas sobre documentos corporativos (PDFs e Words) garantindo 100% de privacidade dos dados, rodando modelos de IA localmente.

## 🌟 Funcionalidades
* **100% Local e Privado:** Nenhum dado da sua empresa vai para a internet. O processamento é feito localmente usando [Ollama](https://ollama.com/).
* **Busca Híbrida (Híbrid Search):** Usando chunks para cada artigo, ou seja para procedimento melhorando a procura.
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
.\venv\Scripts\Activate.ps1
```
### 3. Instalação das Dependências


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
docker-compose up -d --build
````

Acesse http://localhost:8501

Arquitetura e estrutura do projeto

``` text
chatbot_RAG/
├── .streamlit/             # Configurações da interface (Streamlit)
├── banco_vetorial/         # Onde o ChromaDB salva os dados (persistência)
├── documentos/             # Pasta para os PDFs e DOCXs de entrada
├── src/
│   ├── __init__.py         # Torna a pasta 'src' um pacote Python (evita erros de importação)
│   ├── app.py              # Front-end (Streamlit)
│   ├── agente.py           # Orquestrador do fluxo (LangGraph)
│   ├── nos.py              # Definição dos nós do grafo (LLM & Prompt)
│   ├── recuperador.py      # Busca Híbrida (BM25 + Vetorial no Chroma)
│   ├── ingestao.py         # Ingestão estruturada e fatiamento por artigos
│   └── estado.py           # Definição do esquema de estado/memória do agente
├── .gitignore              # Ignora arquivos como a venv, banco local e chaves
├── docker-compose.yml      # Orquestração do Docker (variáveis de ambiente, portas e volumes)
├── Dockerfile              # Receita de build da imagem Docker do app
└── requirements.txt        # Dependências do Python
```
