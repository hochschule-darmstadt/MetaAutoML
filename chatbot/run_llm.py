from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from langchain.llms.ollama import Ollama

class SentenceTransformersEmbeddings(Embeddings):
    """
    A custom embedding class using sentence-transformers for generating embeddings.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.model.encode(text, convert_to_numpy=True)

def query_vector_store_with_metadata(query, retriever, top_k=3):
    """
    Perform a query on the retriever and return the most relevant documents.
    - Separates video links, page links, and other metadata.
    """
    results = retriever.similarity_search_with_relevance_scores(query, k=top_k, score_threshold=0.3)

    extracted_metadata = []
    docs = []

    unique_video_links = set()  # Store unique video links
    page_links = {}  # Store unique page links
    related_tooltips = set()  # Store unique related tooltips
    related_sections = set()  # Store unique related sections and subsections

    for doc, score in results:
        doc_content = doc.page_content
        metadata = doc.metadata

        # Collect video links (ensuring uniqueness)
        if "video_url" in metadata and metadata["video_url"]:
            video_link = f"https://dev.oma-ml.ai/{metadata['video_url']}"
            unique_video_links.add(video_link)

        # Collect page links (ensuring uniqueness)
        if "page_url" in metadata and metadata["page_url"]:
            full_link = f"https://dev.oma-ml.ai/{metadata['page_url']}"
            page_title = metadata.get("title", "this page")  # Use a title if available
            page_links[page_title] = full_link  # Avoid duplicate page links

        # Collect related tooltips (ensuring uniqueness)
        if "related_tooltips" in metadata and metadata["related_tooltips"]:
            related_tooltips.update(metadata["related_tooltips"].split(", "))

        # Collect related sections/subsections
        if "parent_section_text" in metadata and metadata["parent_section_text"]:
            related_sections.add(f"**Section:** {metadata['parent_section_text']}")
        if "parent_subsection_text" in metadata and metadata["parent_subsection_text"]:
            related_sections.add(f"**Subsection:** {metadata['parent_subsection_text']}")

        # Format the document content with its title
        title = metadata.get("title", "Untitled")
        formatted_content = f"{title}: {doc_content}" if doc_content else title
        docs.append(formatted_content)

    # Format additional metadata output (excluding videos/pages)
    additional_metadata = ""

    # Add related sections/subsections
    if related_sections:
        section_list = "\n- " + "\n- ".join(related_sections)
        additional_metadata += f"\n📚 **Related Sections/Subsections:** {section_list}"

    # Add related tooltips
    if related_tooltips:
        tooltip_list = "\n- " + "\n- ".join(related_tooltips)
        additional_metadata += f"\n💡 **Helpful Tooltips:** {tooltip_list}"

    # Prepare video and page links separately
    video_links_text = ""
    page_links_text = ""

    if unique_video_links:
        video_list = ", ".join(unique_video_links)
        video_links_text = f"\n🎥 **Following videos might help during the process:** {video_list}"

    if page_links:
        for title, link in page_links.items():
            page_links_text += f"\n📄 **Please click here to go to the {title} page:** [here]({link})"

    return docs, additional_metadata, video_links_text, page_links_text

def run_rag_pipeline(user_query, retriever, llm, prompt_template, top_k=5):
    """
    A RAG pipeline that retrieves documents and uses an LLM to generate a response.
    - Separates metadata from page/video links.
    """
    # Step 1: Retrieve relevant documents, metadata, and separate links
    docs, additional_metadata, video_links, page_links = query_vector_store_with_metadata(user_query, retriever, top_k)

    # Format metadata properly
    metadata_info = additional_metadata if additional_metadata else "No additional metadata available."

    # Step 2: Combine retrieved documents into context
    context_text = "\n".join(docs) if docs else "No relevant documents found."

    # Step 3: Prepare the final input for the LLM
    llm_input = prompt_template.format(context=context_text, metadata=metadata_info, question=user_query)

    # Step 4: Get the response from the LLM
    llm_response = llm.invoke(llm_input)

    # Step 5: Append video/page links **after** the LLM response
    if video_links or page_links:
        llm_response += "\n\n📌 **Additional Resources:**"
        llm_response += video_links if video_links else ""
        llm_response += page_links if page_links else ""

    return llm_response

if __name__ == "__main__":

    # Load the vector store and embeddings
    database_directory = "./chroma_data"
    embeddings = SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2")
    retriever = Chroma(persist_directory=database_directory, embedding_function=embeddings)

    # Initialize the LLM
    llm = Ollama(model="gemma2:2b")
    #llama2:7b-chat

    # Define the user query
    user_query = "explain to me more about Model selection in OMA ML"
    print(user_query)

    # Define the structured prompt template
    prompt_template = """
    You are an intelligent assistant helping a user with their query.
    Use the following retrieved documents and metadata to generate a meaningful response.

    ### 📜 Retrieved Documents:
    {context}

    ### 📑 Additional Metadata:
    {metadata}

    ### 🚀 Instructions:
    - **Prioritize retrieved documents** to generate an answer.
    - If metadata provides useful insights, include it in your response.
    - If tooltips contain important instructions, summarize them.
    - If related sections/subsections add context, include them.
    - If none of the information answers the query, say: _"I'm not sure based on the given information."_

    ### 🔎 User's Query:
    {question}

    ### 🤖 Your Answer:
    """

    # Run the RAG pipeline
    response = run_rag_pipeline(user_query, retriever, llm, prompt_template, top_k=5)

    # Print the final LLM response
    print("\nFinal LLM Response:")
    print(response)
