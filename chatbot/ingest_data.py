import os
import json
import shutil
import logging
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("SERVER_LOGGING_LEVEL", "INFO").upper())

class SentenceTransformersEmbeddings(Embeddings):
	"""
	A custom embedding class using sentence-transformers for generating embeddings.
	"""
	def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
		self.model = SentenceTransformer(model_name)

	def embed_documents(self, texts):
		return self.model.encode(texts, convert_to_numpy=True).tolist()

	def embed_query(self, text):
		return self.embed_documents([text])[0]

def clean_metadata(metadata: dict) -> dict:
	"""
	Removes metadata keys where values are None or empty.
	Ensures only valid metadata is stored.
	"""
	return {k: v for k, v in metadata.items() if v not in [None, "", []]}

def format_content(title: str, text: str, section: str = None) -> str:
	"""
	Formats document content appropriately based on provided title, text, and section.
	"""
	if section:
		return f"{section}.{title} {text}" if text else f"{section}.{title}"
	return f"{title} {text}" if text else title

def parse_json_to_documents(json_data):
    """
    Parses the JSON data into LangChain Document objects.
    - Stores tooltips inside section/subsection metadata.
    - Stores section/subsection text inside tooltip metadata.
    - Subsections inherit video and page links from their parent section.
    """
    documents = []

    for panel in json_data:
        help_category = panel.get("PanelHeadline", "Unknown Category")
        category_description = panel.get("Text", "").strip()

        # Store the main category as a document
        if category_description:
            documents.append(
                Document(
                    page_content=format_content("Introduction", category_description),
                    metadata=clean_metadata({
                        "title": "Introduction",
                        "type": "Help Category",
                        "help_category": help_category
                    })
                )
            )

        # Process sections in the help category
        for section in panel.get("Sections", []):
            section_title = section.get("Headline", "Unknown Section")
            section_text = section.get("Text", "").strip()
            section_video = section.get("Video", "")
            section_link = section.get("pageLink", "")

            section_tooltips = []  # Store section tooltips
            all_subsection_tooltips = []  # Store all tooltips under subsections

            # Process tooltips for this section
            for tooltip in section.get("Tooltips", []):
                ui_component = tooltip.get("Button", "Unknown UI Element")
                tooltip_text = tooltip.get("Tooltip-text", "").strip()
                tooltip_title = f"Tooltip location and text: {ui_component}"  # Standardized title

                if tooltip_text:
                    tooltip_doc = Document(
                        page_content=format_content(tooltip_title, tooltip_text),
                        metadata=clean_metadata({
                            "title": tooltip_title,
                            "type": "UI Tooltip",
                            "help_category": help_category,
                            "help_section": section_title,
                            "video_url": section_video,  # Inherit video from section
                            "page_url": section_link,  # Inherit page link from section
                            "parent_section_text": format_content(section_title, section_text)  # Store section text inside tooltip
                        })
                    )
                    documents.append(tooltip_doc)
                    section_tooltips.append(f"{tooltip_title} - {tooltip_text}")  # Store formatted tooltip

            # Process subsections
            for subsection in section.get("Subsections", []):
                subsection_title = subsection.get("SubHeadline", "Unknown Subsection")
                subsection_text = subsection.get("SubText", "").strip()

                subsection_tooltips = []  # Store subsection tooltips

                # Process tooltips for this subsection
                for tooltip in subsection.get("Tooltips", []):
                    ui_component = tooltip.get("Button", "Unknown UI Element")
                    tooltip_text = tooltip.get("Tooltip-text", "").strip()
                    tooltip_title = f"Tooltip navigation_path : {ui_component}"  # Standardized title

                    if tooltip_text:
                        tooltip_doc = Document(
                            page_content=format_content(tooltip_title, tooltip_text),
                            metadata=clean_metadata({
                                "title": tooltip_title,
                                "type": "UI Tooltip",
                                "help_category": help_category,
                                "help_section": section_title,
                                "help_subsection": subsection_title,
                                "video_url": section_video,  # Inherit video from section
                                "page_url": section_link,  # Inherit page link from section
                                "parent_section_text": format_content(section_title, section_text),  # Store section text inside tooltip
                                "parent_subsection_text": format_content(subsection_title, subsection_text)  # Store subsection text inside tooltip
                            })
                        )
                        documents.append(tooltip_doc)
                        subsection_tooltips.append(f"{tooltip_title} - {tooltip_text}")  # Store formatted tooltip
                        all_subsection_tooltips.append(f"{tooltip_title} - {tooltip_text}")  # Track all subsection tooltips

                # Add subsection content if exists
                if subsection_text:
                    documents.append(
                        Document(
                            page_content=format_content(subsection_title, subsection_text,section_title),
                            metadata=clean_metadata({
                                "title": subsection_title,
                                "type": "Help Subsection",
                                "help_category": help_category,
                                "parent_section": section_title,
                                "video_url": section_video,  # Inherit video from section
                                "page_url": section_link,  # Inherit page link from section
                                "related_tooltips": ", ".join(subsection_tooltips) if subsection_tooltips else None,  # Store tooltip texts inside subsection metadata
                                "parent_section_text": format_content(section_title, section_text)  # Store formatted parent section
                            })
                        )
                    )

            # Add section content if exists
            if section_text:
                documents.append(
                    Document(
                        page_content=format_content(section_title, section_text),
                        metadata=clean_metadata({
                            "title": section_title,
                            "type": "Help Section",
                            "help_category": help_category,
                            "video_url": section_video,
                            "page_url": section_link,
                            "related_tooltips": ", ".join(section_tooltips + all_subsection_tooltips) if section_tooltips or all_subsection_tooltips else None,  # Store all tooltips
                        })
                    )
                )

    return documents

def delete_existing_database(directory: str) -> None:
	"""
	Deletes the existing database directory if it exists.
	"""
	if os.path.exists(directory):
		shutil.rmtree(directory)
		logger.info(f"Existing database at '{directory}' has been deleted.")

def ingest_data() -> None:
    """Loads JSON data, parses it into LangChain Documents, and stores it in ChromaDB."""
    database_directory = "./chroma_data"
    json_file = "./data/rag_processed_data.json"

    if not os.path.exists(json_file):
        logger.error("JSON file not found. Exiting.")
        return

    delete_existing_database(database_directory)

    with open(json_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    documents = parse_json_to_documents(json_data)
    if not documents:
        logger.error("No documents found in the JSON file. Exiting.")
        return

    embeddings = SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=database_directory,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "l2"}
    )
    vectorstore.add_documents(documents)
    vectorstore.persist()
    logger.info(f"{len(documents)} documents have been successfully ingested into ChromaDB.")

    # ✅ Corrected Print Statements (Proper Indentation)
    # print("\n--- Processed Documents ---")
    # for i, doc in enumerate(documents):
    #     print(f"\nDocument {i + 1}:")
    #     print("Content:", doc.page_content)
    #     print("Metadata:", json.dumps(doc.metadata, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    ingest_data()
