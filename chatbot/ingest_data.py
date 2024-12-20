import os
import json
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from langchain.schema import Document

class SentenceTransformersEmbeddings(Embeddings):
    """
    A custom embedding class using sentence-transformers for generating embeddings.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        # Convert NumPy array to Python list to avoid truth value ambiguity
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]

def parse_json_to_documents(json_file):
    """
    Parse the JSON file into LangChain Document objects.
    Extracts hierarchical data, including nested sections and subsections.
    """
    with open(json_file, "r") as f:
        data = json.load(f)
    
    documents = []

    for panel in data:
        panel_headline = panel.get("PanelHeadline", "Unknown Panel")
        panel_text = panel.get("Text", "")

        # Add the main panel content
        if panel_text.strip():
            documents.append(
                Document(
                    page_content=panel_text,
                    metadata={"title": panel_headline, "type": "Panel"}
                )
            )

        # Process sections within the panel
        for section in panel.get("Sections", []):
            section_headline = section.get("Headline", "Unknown Section")
            section_text = section.get("Text", "")

            # Add section content
            if section_text.strip():
                documents.append(
                    Document(
                        page_content=section_text,
                        metadata={"title": section_headline, "type": "Section", "parent": panel_headline}
                    )
                )

            # Process subsections within the section
            for subsection in section.get("Subsections", []):
                subsection_headline = subsection.get("SubHeadline", "Unknown Subsection")
                subsection_text = subsection.get("SubText", "")

                # Add subsection content
                if subsection_text.strip():
                    documents.append(
                        Document(
                            page_content=subsection_text,
                            metadata={
                                "title": subsection_headline,
                                "type": "Subsection",
                                "parent": section_headline,
                                "grandparent": panel_headline
                            }
                        )
                    )
    return documents

def ingest_data():
    # Load the JSON file
    json_file = "./data.json"
    if not os.path.exists(json_file):
        print("JSON file not found. Exiting.")
        return

    # Parse the JSON file into documents
    documents = parse_json_to_documents(json_file)
    if not documents:
        print("No documents found in the JSON file. Exiting.")
        return

    # Initialize SentenceTransformers embeddings
    embeddings = SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="./chroma_data", embedding_function=embeddings)

    # Add documents to the vector store
    vectorstore.add_documents(documents)
    vectorstore.persist()
    print(f"{len(documents)} documents have been successfully ingested into ChromaDB.")

if __name__ == "__main__":
    ingest_data()
