from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import warnings
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss


# prep code run only once
# Initialize embeddings and vector store
embeddings = OllamaEmbeddings(model='nomic-embed-text', base_url="http://localhost:11434")
model = ChatOllama(model="llama3.2:latest", base_url="http://localhost:11434")

# Initialize FAISS index
single_vector = embeddings.embed_query("dummy text for initialization")
index = faiss.IndexFlatL2(len(single_vector))
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}
)

# Text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

dataFolderPath = "C:/Users/supre/HelloFlask/PDFDatabase"


from os import listdir
from os.path import isfile, join
myFiles = [f for f in listdir(dataFolderPath) if isfile(join(dataFolderPath, f))]

for file in myFiles:

  file_path = join(dataFolderPath,file)
  print(file_path)
  # Load and chunk PDF content
  loader = PyMuPDFLoader(file_path)
  docs = loader.load()
  chunks = text_splitter.split_documents(docs)
  vector_store.add_documents(documents=chunks)

db_name = "VectorStores\health_supplements"
vector_store.save_local(db_name)