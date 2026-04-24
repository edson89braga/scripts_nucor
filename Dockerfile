FROM python:3.12-slim

# Metadados
LABEL maintainer="Nucor / Correição Datas"
LABEL description="Calculadora de cruzamento de períodos — desconto de afastamentos sobre prazo do trabalho"

# Diretório de trabalho
WORKDIR /app

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY backend.py .
COPY app.py .

# Configuração do Streamlit (sem telemetria, sem auto-open de browser)
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
