.PHONY: build interactive \
		streamlit streamlit-gpu down

build:
	docker compose build

interactive: build
	docker compose run --rm streamlit /bin/bash

streamlit:
	docker compose up -d && \
	docker compose exec ollama ollama pull nomic-embed-text:latest && \
	docker compose exec ollama ollama pull llama3.2:3b

streamlit-gpu: build
	docker compose --profile gpu up

down:
	docker compose down -v