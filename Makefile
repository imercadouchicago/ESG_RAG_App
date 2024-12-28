IMAGE_NAME=langchain-rag-app
LOCAL_HOST_DIR = $(shell pwd)
CONTAINER_SRC_DIR = /app/src
DATA_DIR_PATH = $(CONTAINER_SRC_DIR)/data

.PHONY: build interactive pull-models \
		streamlit down

# build:
# 	docker build -t $(IMAGE_NAME) .

# interactive: build
# 	docker run -it \
# 	-v "$(LOCAL_HOST_DIR):$(CONTAINER_SRC_DIR)" \
# 	$(IMAGE_NAME) /bin/bash

# streamlit: build
# 	docker run \
# 	-v "$(LOCAL_HOST_DIR):$(CONTAINER_SRC_DIR)" \
#	-e $(DATA_DIR_PATH) \
# 	-p 8501:8501 -p 11434:11434 $(IMAGE_NAME)

# ollama:
# 	docker-compose up

.PHONY: build interactive streamlit pull-models

build:
	docker compose build

interactive: build
	docker compose run --rm streamlit /bin/bash

pull-models:
	docker compose run --rm ollama ollama pull nomic-embed-text:latest
	docker compose run --rm ollama ollama pull llama2:latest

streamlit: build pull-models
	docker compose up

down:
	docker compose down -v