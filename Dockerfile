# Dockerfile

# Use a imagem base do Python
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt requirements.txt

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código-fonte para o diretório de trabalho
COPY . .

# CMD especifica o comando a ser executado quando o contêiner for iniciado
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
