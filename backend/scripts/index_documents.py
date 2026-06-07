import os
import glob
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

# Document Loaders and Splitters
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import AzureSearch

# 1. Setup Logging & Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("national-security-indexer")

def index_docs():
    """
    Reads PDFs from backend/data, chunks them, and uploads vectors to Azure AI Search.
    """
    # 2. Define Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.normpath(os.path.join(current_dir, "..", "data")) 
    
    # 3. Debug: Check Environment Variables (Updated for new stack)
    logger.info("=" * 60)
    logger.info("National Security Environment Configuration Check:")
    logger.info(f"AZURE_SEARCH_ENDPOINT: {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("=" * 60)
    
    # 4. Validate Required Environment Variables
    
    required_vars = [
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all variables are set.")
        return
    
    # 5. Initialize Embedding Model
    
    try:
        logger.info("Initializing HuggingFace Open-Source Embeddings (all-MiniLM-L6-v2)...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        logger.info("✓ Embeddings model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize HuggingFace embeddings: {e}")
        return
    
    # 6. Initialize Azure Search (The Knowledge Base)
    try:
        logger.info("Initializing Azure AI Search vector store...")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=index_name,
            embedding_function=embeddings.embed_query
        )
        logger.info(f"✓ Vector store initialized for index: {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Search: {e}")
        logger.error("Please verify your Azure Search endpoint, API key, and index name.")
        return
    
    # 7. Find PDF Files
    logger.info(f"Searching for PDFs in: {data_folder}")
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {data_folder}. Please ensure 'National_Security.pdf' is placed here.")
        return
    
    logger.info(f"Found {len(pdf_files)} PDFs to process: {[os.path.basename(f) for f in pdf_files]}")
    
    all_splits = []
    
    # 8. Process Each PDF
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading: {os.path.basename(pdf_path)}...")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()
            
            # 9. Chunking Strategy
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(raw_docs)
            
            # Tag the source for citation later
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)
            
            all_splits.extend(splits)
            logger.info(f" -> Split into {len(splits)} chunks.")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
    
    # 10. Upload to Azure
    if all_splits:
        logger.info(f"Uploading {len(all_splits)} chunks to Azure AI Search Index '{index_name}'...")
        try:
            vector_store.add_documents(documents=all_splits)
            logger.info("=" * 60)
            logger.info("✅ Indexing Complete! The National Security Knowledge Base is ready.")
            logger.info(f"Total chunks indexed: {len(all_splits)}")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"Failed to upload documents to Azure Search: {e}")
            logger.error("Please check your Azure Search configuration and try again.")
    else:
        logger.warning("No documents were processed.")

if __name__ == "__main__":
    index_docs()