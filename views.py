from flask import render_template, g, Blueprint,request, jsonify
import os
import pandas as pd
from matplotlib.figure import Figure
from io import BytesIO
import base64

from matplotlib.figure import Figure

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Initialize the LangChain model and prompt template
model = OllamaLLM(model="llama3.2:latest")
template = """
Answer the question below.

Here is the conversation history: {context}

Here is the next question: {question}

Answer:
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Initialize chat context
chat_context = ""

# Specify the directory containing the Excel files
EXCEL_DIR = "Dataz"

my_view = Blueprint(__name__,'my_view')

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

@my_view.route("/chat", methods=["POST"])
def chat():
    global chat_context
    user_message = request.json.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Invoke the LangChain model
    response = chain.invoke({"context": chat_context, "question": user_message})
    bot_reply = str(response)

    # Update context
    chat_context += f"\nUser: {user_message}\nAI: {bot_reply}"

    return jsonify({"reply": bot_reply})



# @my_view.route("/home")
# def hello():
#   return "hello"

# @my_view.route("/")
# def displayHomePage():

#   data["Days"] = data['End date'] - data['Start date']

#   fig = Figure()
#   ax = fig.add_subplot()

#   ax.barh(y=data['Project Name'],left=data['Start date'],width=data['Days'])

#   buf = BytesIO()
#   fig.savefig(buf, format="png")
# # Embed the result in the html output.
#   tempData = base64.b64encode(buf.getbuffer()).decode("ascii")
#   return f"<img src='data:image/png;base64,{tempData}'/>"

# @my_view.route('/dropdown', methods=['GET', 'POST'])
# def dropdown():
#     selected_option = None
#     if request.method == 'POST':
#         # Get the selected option from the form
#         selected_option = request.form.get('dropdown', 'No option selected')
#         projectManager = data.loc[data['Project Name']==selected_option,'Project manager'].item()
#         return f"You selected: {projectManager}"

#     return render_template('index.html')