# Sustainability RAG App

## Overview

A RAG chatbot application for answering questions regarding corporate sustainability reports. The RAG pipeline incorporates query augmentation, reciprocal rank fusion, and cross-encoder reranking to improve the accuracy of the chatbot's responses. The Playwright webscraper uses JavaScript to scrape sustainability reports for the companies in the S&P 500 index.

## Technology Stack
- Python
- Makefile
- Docker
- Streamlit
- Ollama
- Langchain
- ChromaDB
- Playwright
- A variety of Python packages

## Project Structure
```
ESG_RAG_App/
├── chromadb/
├── data/
│   └──SP500.csv
├── rag_app/
│   ├── downloads/
│   ├── calculation.js
│   ├── webscraper.js
│   ├── webscraper.log
│   ├── preprocessing.py
│   ├── fusion.py
│   ├── retriever.py
│   ├── reranking.py
│   └── generator.py
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

## Interacting with the Docker Container

```bash
cd ESG_RAG_App
ESG_RAG_App $ make interactive
```

## Note

This repository is currently under development. I am in the process of increasing webscraper efficiency and accuracy. Currently, the webscraper is able to scrape 2,695 sustainability reports for 446 of the companies in the S&P 500 index.

## Data Sources
The sp500.csv file: 

- https://www.kaggle.com/datasets/andrewmvd/sp-500-stocks?resource=download&select=sp500_companies.csv

Sustainability reports:

- https://responsibilityreports.com

## Contact
Isabella Mercado - imercado@uchicago.edu

Project Link: https://github.com/imercadouchicago/esg_rag_app