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
import re
import logging

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatbotService")

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
llm = OllamaLLM(model="gemma2:2b")
#llama2:7b-chat
#gemma2:2b
#mistral:7b-instruct

# Prompt template

prompt_template = (
    "You are an AI assistant helping users navigate and get informations about a website called  OMA-ML(stands for AutoML platform that automates complex tasks in machine learning (ML) and generates ML pipelines), a data science platform."
    "Your goal is to provide clear and precise answers based on the provided context and metadata and to answers Quetion related  machine learning (ML) and AI."

    "  **Answering User Questions:**"
    "- Answer the question based on the provided context and metadata whenever possible."
    "- If the question is related to OMA-ML, but no relevant context is retrieved, respond with:\n"
    "'I can't answer this question.' and stop there."
    "- If the question is related to general machine learning (ML) concepts and no relevant context is retrieved, "
    "you may answer based on your own knowledge."
    "- **DO NOT mention OMA-ML or reference its help section when answering a general ML question unless metadata explicitly confirms its relevance.**"
    "- If the question is NOT related to machine learning or OMA-ML, respond ONLY with:\n"
    "'I can't answer this question.' and NOTHING ELSE."
    "- **Do not provide additional explanations, suggestions, or alternative topics after this response.**"

    " **Handling OMA-ML Navigation Questions:**"
    "- If the question is about navigating the OMA-ML platform or website, also refer the user at the end of the answer "
    "to the help section and tell them that it is useful for more information ONLY IF THE QUESTION is related to OMA-ML: "
    "(https://dev.oma-ml.ai/help)."
    "- If the user asks 'How do I find X in OMA-ML?', provide step-by-step instructions based on metadata."
    "- Format navigation paths in this format: 'Click on **[First Level]**, then go to **[Second Level]**, then select **[Third Level]**.'"
    "- **Only provide navigation paths if the question is specifically about finding something and if metadata exists abot it.**"

    " **Handling Informational Questions (Concept Explanations):**"
    "- If the user asks for details about a feature, a page, or how something works, prioritize a clear explanation first."
    "- Use the **Context** and **Related Sections and Subsections to the topic** to provide a comprehensive answer."
    "- Structure your answer logically, listing the key components or functions first, then how to use them."
    "- **DO NOT generate or assume any links, videos, or documents unless they are explicitly provided in the retrieved metadata.**"
    "- If no relevant metadata exists, respond without adding links."
    "- If there are related videos, URLs, or pages in the context or metadata, include them after your response."
    "- **If the user is asking about an OMA-ML-related concept and the Help section is available, refer them to it for additional guidance:** "
    "(https://dev.oma-ml.ai/help)."
    "- **DO NOT refer to the OMA-ML Help section for general ML questions unless metadata explicitly mentions OMA-ML in relation to the topic.**"

    " **Handling Conversation History for Contextual Responses:**"
    "- The chat history contains previous interactions and may help clarify ambiguous or follow-up questions."
    "- Use relevant parts of the history to maintain context, but do not repeat previous answers verbatim."
    "- If the current question references something previously discussed, respond as if part of an ongoing conversation."
    "- **If history is irrelevant to the current question, ignore it and respond based on the new query alone.**"

    " **Handling Out-of-Scope Questions:**"
    "- If the question is NOT related to machine learning or OMA-ML, respond ONLY with:\n"
    "'I can't answer this question.' and NOTHING ELSE."
    "- DO NOT assume a navigation answer exists if no relevant metadata is available."
    "- DO NOT include the OMA-ML Help link unless the question is explicitly about OMA-ML."
    "- DO NOT generate an answer if you are unsure or if the topic is outside ML or OMA-ML."
    "- **Do NOT speculate or generate an answer if the topic is outside ML or OMA-ML or if you are not sure of the answer.**"

    "  **Strict Rules for Using Links, Videos, and Navigation Paths:**"
    "- **Only use links that exist in the retrieved metadata. DO NOT generate fake links.**"
    "- **Only provide navigation paths if explicitly retrieved from metadata.**"
    "- **Only include videos and URLs if they are present in metadata. DO NOT assume they exist.**"

    "\n\nContext:\n{context}\n\n"
    "Additional Metadata:\n{metadata}\n\n"
    "Chat History:\n{history}\n\n"
    "User Question:\n{question}\n\n"
    "Answer:"
)





prompt = PromptTemplate(template=prompt_template, input_variables=["history", "context", "metadata", "question"])

import re

def extract_ui_tooltips(tooltip_text):
    """Extracts and reformats UI navigation tooltips from raw metadata."""
    formatted_tooltips = set()  # Store reformatted tooltips (avoid duplicates)

    for tooltip in tooltip_text.split(", "):
        # Remove unnecessary prefixes (handles both "Tooltip location and text:" & "Tooltip navigation_path :")
        tooltip = re.sub(r"Tooltip (location and text|navigation_path) ?: ?", "", tooltip)

        # Detect UI paths (e.g., Home.Datasets.Dataset.CreateNewTraining)
        raw_path_match = re.search(r'([A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*)', tooltip)

        if raw_path_match:
            raw_path = raw_path_match.group(1)  # Extract UI path
            formatted_path = " ➝ ".join([f"**{step}**" for step in raw_path.split(".")])  # Convert to step format

            # Extract description (if available)
            tooltip_description = tooltip.split(" - ", 1)[1] if " - " in tooltip else "No additional description."

            # Format tooltip
            formatted_tooltip = f"🔹 **Navigate to:** {formatted_path}\n➡️ {tooltip_description}"
            formatted_tooltips.add(formatted_tooltip)  # Avoid duplicates

    return formatted_tooltips


def query_vector_store_with_metadata(query, retriever, top_k=5):
    """Retrieves relevant documents from vector storage and processes metadata for LLM."""
    results = retriever.similarity_search_with_relevance_scores(query, k=top_k, score_threshold=0.2)
    docs = []

    video_links = set()  # Store all video links with their respective titles
    all_video_metadata = set()  # Store video links separately for metadata inclusion
    first_page_link = None  # Store only the first available page link
    formatted_tooltips = set()  # Store reformatted tooltips (avoid duplicates)
    related_sections = set()

    for doc, score in results:
        metadata = doc.metadata
        doc_content = doc.page_content

        # Store all video links with their respective subsection/section titles
        if "video_url" in metadata and metadata["video_url"]:
            video_url = f"https://dev.oma-ml.ai/{metadata['video_url']}"
            video_title = metadata.get("parent_subsection_text", metadata.get("parent_section_text", "Video"))
            if video_url not in video_links:
                video_links.add(video_url)
                video_entry = f"🎥 **{video_title}:** {video_url}"
                all_video_metadata.add(video_entry)

        # Store first available page link from the highest-scoring document
        if first_page_link is None and "page_url" in metadata and metadata["page_url"]:
            full_link = f"https://dev.oma-ml.ai/{metadata['page_url']}"
            page_title = metadata.get("title", "this page")
            first_page_link = f"📄 **{page_title} page:**({full_link})"

        # Extract and reformat tooltips for navigation paths
        if "related_tooltips" in metadata and metadata["related_tooltips"]:
            formatted_tooltips.update(extract_ui_tooltips(metadata["related_tooltips"]))

        # Collect related sections and subsections
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
            f"\n💡 **Helpful Tooltips for navigating OMA-ML:**\n" + "\n".join(formatted_tooltips) if formatted_tooltips else "",
            f"\n🎥 **Useful videos to guide through the process:**\n" + "\n".join(all_video_metadata) if all_video_metadata else "",
            f"\n📄 **Helpful Page:** {first_page_link}" if first_page_link else ""
        ]
    )

    return docs, additional_metadata



# Define the gRPC Service
class ChatbotService(ChatbotBase):
	async def chat(self, chat_request: ChatRequest) -> AsyncIterable[ChatReply]:
		"""
		Handles incoming chat requests and generates responses using a retrieval-augmented generation pipeline.

		Args:
			chat_request (ChatRequest): The incoming request containing the user's message and chat history.

		Yields:
			ChatReply: Streamed chatbot responses.
		"""
		try:
			user_query = chat_request.message
			chat_history = chat_request.history
			logger.info("Received user query")

			retrieval_start = time.time()
			docs, additional_metadata = query_vector_store_with_metadata(user_query, retriever, top_k=3)
			retrieval_time = time.time() - retrieval_start

			generation_start = time.time()
			context_text = "\n".join(docs)
			metadata_info = additional_metadata
			logger.debug(f"Context: {context_text}")
			logger.debug(f"Metadata: {additional_metadata}")

			llm_input = prompt.format(history=chat_history, context=context_text, metadata=metadata_info, question=user_query)
			logger.info(f"Query Token Count: {len(llm_input.split())}")

			response = llm.invoke(llm_input)
			generation_time = time.time() - generation_start

			logger.info(f"Total Retrieval Time: {retrieval_time:.4f} seconds")
			logger.info(f"Total Generation Time: {generation_time:.4f} seconds")
			logger.info(f"Overall Processing Time: {retrieval_time + generation_time:.4f} seconds")

			for char in response:
				yield ChatReply(chatbot_reply=char)

		except Exception as e:
			logger.error(f"Error processing chat request: {e}")

async def llm_health_check() -> None:
	"""
	Performs a health check on the LLM to ensure it's operational.
	"""
	try:
		dummy_question = "What is 2 + 2?"
		llm_input_dummy = prompt.format(history="", context="", metadata="", question=dummy_question)
		response = llm.invoke(llm_input_dummy)
		if response:
			logger.info("LLM health check passed: LLM is initialized and responsive.")
		else:
			logger.error("LLM health check failed: No response from LLM.")
			exit(1)

	except Exception as e:
		logger.error(f"LLM health check failed with an exception: {e}")
		exit(1)

async def serve() -> None:
	"""
	Initializes and runs the gRPC server for chatbot services.
	"""
	await llm_health_check()
	server = Server([ChatbotService()])
	host = "0.0.0.0"
	port = 50051
	logger.info(f"gRPC server is running on {host}:{port}")
	await server.start(host, port)
	await server.wait_closed()

if __name__ == "__main__":
	asyncio.run(serve())
