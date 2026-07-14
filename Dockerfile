# Usa uma imagem oficial do Python (versão slim para ficar mais leve)
FROM python:3.11-slim

# Instala dependências do sistema necessárias para compilar bibliotecas de IA/C++
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Define a pasta de trabalho dentro do contêiner
WORKDIR /app

# Copia a lista de dependências primeiro (isso otimiza o tempo de build do Docker)
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do seu código para dentro do contêiner
COPY . .

# Expõe a porta que o Streamlit usa por padrão
EXPOSE 8501

# Comando para iniciar o Streamlit quando o contêiner ligar
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]