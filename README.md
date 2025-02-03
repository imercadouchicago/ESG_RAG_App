# Sustainability RAG App

## Overview

A RAG chatbot application for answering questions regarding corporate sustainability reports.

## Technology Stack
- Python
- Makefile
- Docker
- Streamlit
- Ollama
- Langchain
- ChromaDB
- A variety of Python packages

## Project Structure
```
ESG_RAG_App/
├── chromadb/
├── data/
├── rag_app/
│   ├── generator.py
│   ├── preprocessing.py
│   ├── retriever.py
│   ├── reranker.py
│   ├── webscraper.js
├── app.py
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
└── README.md
```

## Setup

1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/

2. Clone the repository:

```bash
git clone https://github.com/yourusername/esg_rag_app.git
```

3. Interact with the Docker containers using the make commands contained in the Makefiles. See the section below for more information.

## Interacting with the Web Application
The Makefile within the root of the repository contains a command to run the web application. The make command "make streamlit" will run the docker-compose.yml file, which will build the ollama and streamlit containers on detached mode and run the web application on port 8501.

```bash
cd ESG_RAG_App
ESG_RAG_App $ make streamlit
```

## Note

This repository is currently under development. I am in the process of adapting the Playwright webscraper to scrape sustainability reports from the companies in the S&P 500 index and incorporating additional RAG techniques to improve the accuracy of the chatbot's responses.

## Data Sources
The sp500.csv file: 

- https://www.kaggle.com/datasets/andrewmvd/sp-500-stocks?resource=download&select=sp500_companies.csv

Sustainability reports:

- https://responsibilityreports.com

## Contact
Isabella Mercado - imercado@uchicago.edu

Project Link: https://github.com/imercadouchicago/esg_rag_app