import asyncio
from typing import AsyncIterable, List
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

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

# Initialize vector database
vectorstore = Chroma(
    persist_directory="./chroma_data",
    embedding_function=SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2"),
)
retriever = vectorstore.as_retriever()

# Initialize LLM
llm = OllamaLLM(model="llama2:7b-chat")

# Prompt template
prompt_template = """You are a helpful assistant. Use the following chat history and retrieved information to answer the user's question.

Chat History:
{history}

Retrieved Information:
{context}

Question:
{question}

Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["history", "context", "question"])

# Define the gRPC Service using BetterProto
class ChatbotService(ChatbotBase):
    def __init__(self):
        self.chat_history: List[str] = []  # Global chat history

    async def chat(self, chat_request: ChatRequest) -> AsyncIterable[ChatReply]:
        print("we are in")
        user_query = chat_request.message

        # Check if the new_chat flag is True and reset the history
        if chat_request.new_chat:
            self.chat_history = []
        # Append user query to global chat history
        print(self.chat_history)

        # Retrieve relevant documents
        docs = retriever.invoke({"query": user_query})
        context_text = "\n".join([doc.page_content for doc in docs])

        # Prepare LLM input with history and retrieved context
        history_text = "\n".join(self.chat_history)
        llm_input = prompt.format(history=history_text, context=context_text, question=user_query)
        print("Tokens count:", len(llm_input.split()))
        print(llm_input)

        # Get response from the LLM
        response = llm.invoke(llm_input)

        # Append LLM response to global chat history
        self.chat_history.append(f"User: {user_query}")
        self.chat_history.append(f"Assistant: {response}")

        # Stream the response character by character
        for char in response:
            yield ChatReply(chatbot_reply=char)
            await asyncio.sleep(0.02)  # Simulate typing delay

async def llm_health_check():
    """
    Send a dummy request to the LLM to verify initialization and response.
    """
    try:
        dummy_history = ""
        dummy_context = ""
        dummy_question = "What is 2 + 2?"
        llm_input_dummy = prompt.format(
            history=dummy_history,
            context=dummy_context,
            question=dummy_question
        )
        response = llm.invoke(llm_input_dummy)
        if response:
            print("LLM health check passed: LLM is initialized and responsive.")
            print(response)
        else:
            print("LLM health check failed: No response from LLM.")
            exit(1)
    except Exception as e:
        print(f"LLM health check failed with an exception: {e}")
        exit(1)

async def serve():
    # Run the LLM health check before starting the server
    await llm_health_check()
    server = Server([ChatbotService()])
    host = "0.0.0.0"
    port = 50051
    print(f"gRPC server is running on {host}:{port}")
    await server.start(host, port)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(serve())
