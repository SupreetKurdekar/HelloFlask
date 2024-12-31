from flask import render_template, Blueprint, request, jsonify
import os
import pandas as pd
from matplotlib.figure import Figure
from io import BytesIO
import base64

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

# Load environment variables
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
warnings.filterwarnings("ignore")
load_dotenv()

# Initialize models
model = ChatOllama(model="llama3.2:latest", base_url="http://localhost:11434")
embeddings = OllamaEmbeddings(model='nomic-embed-text', base_url="http://localhost:11434")

def format_docs(docs):
    """Helper function to format documents into a string."""
    return "\n\n".join([doc.page_content for doc in docs])

# Load vector store from file
vector_store = FAISS.load_local("VectorStores\health_supplements", embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 3, 'fetch_k': 100, 'lambda_mult': 1})

# Load prompt for regular chatbot
regular_prompt = """
Answer the question below.

Here is the conversation history: {context}

Here is the next question: {question}

Answer:
"""
regular_prompt_template = ChatPromptTemplate.from_template(regular_prompt)

# Initialize LangChain chains for regular chat
regular_rag_chain = regular_prompt_template | model | StrOutputParser()

# Load prompt for PDF chatbot (similar to the regular one)
pdf_prompt = """
    You are an assistant for question-answering tasks based on a PDF document. Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.
    Make sure your answer is relevant to the question and it is answered from the context only.
    Question: {question} 
    Context: {context} 
    Answer:
"""

pdf_prompt_template = ChatPromptTemplate.from_template(pdf_prompt)

# Initialize the PDF-specific RAG chain
pdf_rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | pdf_prompt_template
    | model
    | StrOutputParser()
)

# Initialize chat context for regular chatbot and PDF chatbot
regular_chat_context = ""
pdf_chat_context = ""


# Specify the directory containing the Excel files
EXCEL_DIR = "Dataz"

my_view = Blueprint(__name__, 'my_view')

@my_view.route("/")
def index():
    # List all Excel files and strip their extensions
    excel_files = [os.path.splitext(f)[0] for f in os.listdir(EXCEL_DIR) if f.endswith(('.xls', '.xlsx'))]
    return render_template("index.html", excel_files=excel_files)

@my_view.route("/process", methods=["POST"])
def process():
    # Get the selected file (name without extension)
    selected_file_name = request.form.get("excel_file")

    if selected_file_name:
        file_path = os.path.join(EXCEL_DIR, f"{selected_file_name}.xlsx")

        try:
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(file_path)

            # Prepare data for Gantt chart
            df["Days"] = (df["End date"] - df["Start date"]).dt.days

            # Create a very compact Gantt chart
            fig = Figure(figsize=(6, 3))  # Compact overall size
            ax = fig.add_subplot(1, 1, 1)

            # Reduce bar height further
            bar_height = 0.3
            y_positions = range(len(df) - 1, -1, -1)  # Reverse task order

            # Plot horizontal bars
            ax.barh(y=y_positions, left=df["Start date"], width=df["Days"], color="skyblue", height=bar_height)

            # Set Y-axis labels
            ax.set_yticks(y_positions)
            ax.set_yticklabels(df["Project Task"], fontsize=8)  # Smaller font size for compactness

            # Invert Y-axis and adjust the X-axis label
            ax.invert_yaxis()
            ax.set_xlabel("Timeline", fontsize=8)
            ax.tick_params(axis="x", labelsize=8)  # Smaller ticks for X-axis

            # Compact spacing around the figure
            fig.subplots_adjust(top=0.95, bottom=0.2, left=0.3, right=0.95)  # Tight spacing

            # Save the chart to a BytesIO buffer
            buf = BytesIO()
            fig.tight_layout()  # Prevent overlap
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            # Encode the PNG image to base64
            chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
            buf.close()

            # Generate table HTML
            table_html = df.to_html(classes="table table-striped table-bordered", index=False)

            return render_template(
                "view_excel.html",
                file_name=selected_file_name,
                table_html=table_html,
                chart_base64=chart_base64
            )

        except Exception as e:
            return f"An error occurred while processing the file: {e}"
    else:
        return "No file was selected. Please try again."

@my_view.route('/upload', methods=['POST'])
def upload_pdf():
    """Handles PDF upload and document processing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    file_path = os.path.join(my_view.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    return jsonify({"message": "PDF uploaded and processed successfully", "chunks_count": 1})

@my_view.route('/pdfChat', methods=['POST'])
def pdf_chat():
    """Handles question answering using RAG for PDF-based chat."""
    global pdf_chat_context  # Use global pdf_chat_context to preserve PDF conversation context

    user_message = request.json.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Use the pdf_rag_chain for PDF-based conversation
    try:
        output = pdf_rag_chain.invoke(user_message)
        bot_reply = str(output)
    except Exception as e:
        return jsonify({"error": "Error while processing request.", "details": str(e)}), 500

    # Update PDF chat context
    pdf_chat_context += f"\nUser: {user_message}\nAI: {bot_reply}"

    # Return response for PDF chatbot
    return jsonify({"reply": bot_reply})

@my_view.route("/chat", methods=["POST"])
def regular_chat():
    """Handles question answering using RAG for regular chatbot."""
    global regular_chat_context  # Use global regular_chat_context to preserve regular conversation context

    user_message = request.json.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Use the regular_rag_chain for regular conversation
        response = regular_rag_chain.invoke({"context": regular_chat_context, "question": user_message})
        
        # Extract only the 'content' from the response
        bot_reply = response.get("content", "") if isinstance(response, dict) else str(response)

    except Exception as e:
        return jsonify({"error": "Error while processing request.", "details": str(e)}), 500

    # Update context for regular chatbot
    regular_chat_context += f"\nUser: {user_message}\nAI: {bot_reply}"

    return jsonify({"reply": bot_reply})

