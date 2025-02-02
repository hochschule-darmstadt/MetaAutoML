# Use the official Ollama image as the base
FROM ollama/ollama:latest


# Force Python to print logs
ENV PYTHONUNBUFFERED=1


# Install Python, pip, git, and other necessary tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    python3 \
    python3-pip \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Download the required Ollama model during the build phase
#RUN ollama serve & sleep 2 && ollama pull llama2:7b-chat && pkill -f ollama

# alternative possible LLM Models:
#RUN ollama serve & sleep 2 && ollama pull gemma2:2b && pkill -f ollama
RUN ollama serve & sleep 2 && ollama pull mistral:7b-instruct && pkill -f ollama

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . /app/

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Ensure ChromaDB persistence directory exists
RUN mkdir -p /app/chroma_data


# Expose only the gRPC port to the outside world
EXPOSE 50051

# Start Ollama and the gRPC server
ENTRYPOINT ["/bin/bash", "-c", \
    "nohup ollama serve > /tmp/ollama.log 2>&1 & \
    sleep 2 && python3 ingest_data.py && \
    exec python3 rag_pipeline.py | tee /dev/stderr"]
