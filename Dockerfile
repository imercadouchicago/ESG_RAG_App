FROM python:3.12-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y nodejs npm
RUN npm install playwright \
                csv-parser \
                fuse.js
RUN npx playwright install
RUN npx playwright install-deps

WORKDIR /app/src

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
