# Usa uma imagem leve do Python 3.11
FROM python:3.11-slim

# Define a pasta de trabalho dentro do container
WORKDIR /code

# Copia os requisitos e instala (aproveita cache do Docker)
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia o código da aplicação
COPY ./app /code/app

# Comando para iniciar o servidor na porta 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
