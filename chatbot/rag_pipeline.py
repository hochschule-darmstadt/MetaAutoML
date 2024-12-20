import asyncio
from typing import AsyncIterable
from grpclib.server import Server
from langchain.vectorstores import Chroma
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from ChatbotBGRPC import ChatRequest, ChatReply, ChatbotBase

# Embeddings class
class SentenceTransformersEmbeddings(Embeddings):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]

# Initialize vector database
vectorstore = Chroma(
    persist_directory="./chroma_data",
    embedding_function=SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2"),
)
retriever = vectorstore.as_retriever()

# Initialize LLM
llm = OllamaLLM(model="llama2:7b-chat")

prompt_template = """You are a helpful assistant. Use the following retrieved information to answer the user's question.

Retrieved Information:
{context}

Question:
{question}

Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])


# Define the gRPC Service using BetterProto
class ChatbotService(ChatbotBase):
    async def chat(self, chat_request: ChatRequest) -> AsyncIterable[ChatReply]:
        user_query = chat_request.message

        # Retrieve relevant documents
        docs = retriever.invoke({"query": user_query})

        # Combine retrieved documents into context
        context_text = "\n".join([doc.page_content for doc in docs])

        # Prepare the final input for the LLM
        llm_input = prompt.format(context=context_text, question=user_query)

        # Get the response from the LLM
        response = llm.invoke(llm_input)

        # Stream the response character by character
        for char in response:
            yield ChatReply(reply=char)
            await asyncio.sleep(0.02)  # Simulate typing delay


async def serve():
    # Initialize the server with your service
    server = Server([ChatbotService()])
    host = "0.0.0.0"
    port = 50051
    print(f"gRPC server is running on {host}:{port}")

    # Start serving
    await server.start(host, port)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(serve())
