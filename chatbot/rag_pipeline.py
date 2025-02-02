import asyncio
import time
from typing import AsyncIterable, List
from grpclib.server import Server
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer
from ChatbotBGRPC import ChatRequest, ChatReply, ChatbotBase
import warnings

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)

# Custom Embeddings class
class SentenceTransformersEmbeddings(Embeddings):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

# Initialize vector database

database_directory = "./chroma_data"

vectorstore = Chroma(
    persist_directory=database_directory,
    embedding_function=SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2"),
    collection_metadata={"hnsw:space": "l2"}
)
embeddings = SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2")
retriever = Chroma(persist_directory=database_directory, embedding_function=embeddings,collection_metadata={"hnsw:space": "l2"})

# Initialize LLM
llm = OllamaLLM(model="mistral:7b-instruct")
#llama2:7b-chat
#gemma2:2b
#mistral:7b-instruct

# Prompt template

prompt_template = (
    "Answer the following question based on the context and the Additional Metadata provided"
    "If there any related Videos, video link or URl or Page URL send it automaticly after answering the question even if the user didnt specificly asked"
    "If the context does not have sufficient information to answer the question or if there is no context retrieved, but the question is relevant to machine learning areas, then you can answer based on your own knowledge, if not,just respond with: 'Its not my speciality field."
    "If the answer is not related to Machine learning or OMA-ML, just respond with this sentense: 'I am not sure of the result:please create a support ticket'\n\n"
    "Context:\n{context}\n\n"
    "Additional Metadata:{metadata}\n\n"
    "Chat History:{history}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)


prompt = PromptTemplate(template=prompt_template, input_variables=["history", "context", "metadata", "question"])

# Function to format retrieved documents and metadata
def query_vector_store_with_metadata(query, retriever, top_k=3):
    results = retriever.similarity_search_with_relevance_scores(query, k=top_k, score_threshold=0.3)
    docs = []

    video_links = set()  # Store all video links with their respective titles
    all_video_metadata = set() # Store video links separately for metadata inclusion
    first_page_link = None   # Store only the first available page link
    related_tooltips = set()
    related_sections = set()

    for doc, score in results:
        print(f"Retrieved Score: {score}")  # Debugging: Check retrieval scores

        doc_content = doc.page_content
        metadata = doc.metadata

        #print(f"Retrieved Document Content: {doc_content}")  # Debugging: Verify document content
        #print(f"Retrieved Metadata: {metadata}")  # Debugging: Verify metadata exists

        # Store all video links with their respective subsection/section titles
        if "video_url" in metadata and metadata["video_url"]:
            video_url = f"https://dev.oma-ml.ai/{metadata['video_url']}"
            video_title = "Video"  # Default title if no subsection found

            if "parent_subsection_text" in metadata and metadata["parent_subsection_text"]:
                video_title = metadata["parent_subsection_text"]
            elif "parent_section_text" in metadata and metadata["parent_section_text"]:
                video_title = metadata["parent_section_text"]
            if video_url not in video_links:
                video_links.add(video_url)
                video_entry = f"🎥 **{video_title}:** {video_url}"
                all_video_metadata.add(video_entry)  # Include in metadata separately

        # Store first available page link from the highest-scoring document
        if first_page_link is None and "page_url" in metadata and metadata["page_url"]:
            full_link = f"https://dev.oma-ml.ai/{metadata['page_url']}"
            page_title = metadata.get("title", "this page")
            first_page_link = f"📄 **{page_title} page:**({full_link})"

        # Continue collecting other metadata (tooltips, sections, etc.)
        if "related_tooltips" in metadata and metadata["related_tooltips"]:
            related_tooltips.update(metadata["related_tooltips"].split(", "))

        if "parent_section_text" in metadata and metadata["parent_section_text"]:
            related_sections.add(f"**Section:** {metadata['parent_section_text']}")

        if "parent_subsection_text" in metadata and metadata["parent_subsection_text"]:
            related_sections.add(f"**Subsection:** {metadata['parent_subsection_text']}")

        # Store document content
        docs.append(doc_content)

    # Handling metadata formatting
    additional_metadata = "".join(
        [
            f"\n📚 **Related Sections and Subsections to the topic:** {' '.join(related_sections)}" if related_sections else "",
            f"\n💡 **Helpful Tooltips with their button location in a format of page.subpage.button and its usage as text:** {' '.join(related_tooltips)}" if related_tooltips else "",
            f"\n""🎥 **usefull videos to guide thorugh the process" + "\n".join(all_video_metadata) if all_video_metadata else "",  # ✅ Include all video links separately in metadata
            f"\n📄 **Helpful Page:** {first_page_link}" if first_page_link else ""  # ✅ Page link remains first retrieved one
        ]
    )
    return docs, additional_metadata


# Define the gRPC Service
class ChatbotService(ChatbotBase):
    async def chat(self, chat_request: ChatRequest) -> AsyncIterable[ChatReply]:
        user_query = chat_request.message
        chat_history = chat_request.history
        print(chat_history)
        retrieval_start = time.time()
        docs, additional_metadata= query_vector_store_with_metadata(user_query, retriever, top_k=3)
        retrieval_time = time.time() - retrieval_start

        generation_start = time.time()
        context_text = "\n".join(docs)
        metadata_info = additional_metadata
        print("context",context_text)
        print("Meta",additional_metadata)
        llm_input = prompt.format(history=chat_history,context=context_text, metadata=metadata_info, question=user_query)
        print(f"Query Token Count: {len(llm_input.split())}")
        response = llm.invoke(llm_input)
        generation_time = time.time() - generation_start
        print(f"Total Retrieval Time: {retrieval_time:.4f} seconds")
        print(f"Total Generation Time: {generation_time:.4f} seconds")
        print(f"Overall Processing Time: {retrieval_time + generation_time:.4f} seconds")

        for char in response:
            yield ChatReply(chatbot_reply=char)
            #await asyncio.sleep(0.02)

async def llm_health_check():
    try:
        dummy_question = "What is 2 + 2?"
        llm_input_dummy = prompt.format(history="", context="", metadata="", question=dummy_question)
        response = llm.invoke(llm_input_dummy)
        if response:
            print("LLM health check passed: LLM is initialized and responsive.")
        else:
            print("LLM health check failed: No response from LLM.")
            exit(1)
    except Exception as e:
        print(f"LLM health check failed with an exception: {e}")
        exit(1)

async def serve():
    await llm_health_check()
    server = Server([ChatbotService()])
    host = "0.0.0.0"
    port = 50051
    print(f"gRPC server is running on {host}:{port}")
    await server.start(host, port)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(serve())
