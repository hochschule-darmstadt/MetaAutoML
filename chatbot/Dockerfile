# Use the official Ollama image as the base
FROM ollama/ollama:latest

# Set environment variables
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

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Ensure ChromaDB persistence directory exists
RUN mkdir -p /app/chroma_data

# Download the required Ollama model during the build phase
RUN ollama serve & sleep 2 && ollama pull llama2:7b-chat && pkill -f ollama

# Expose only the gRPC port to the outside world
EXPOSE 50051

# Start Ollama and the gRPC server
ENTRYPOINT ["/bin/bash", "-c", \
    "ollama serve & \
    sleep 2 && python3 ingest_data.py && \
    python3 rag_pipeline.py && wait"]
