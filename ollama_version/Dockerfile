FROM python:3.12-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install "unstructured[md]"

WORKDIR /app/src

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]