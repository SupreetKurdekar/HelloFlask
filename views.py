from flask import render_template, g, Blueprint,request, jsonify
import os
import pandas as pd
from matplotlib.figure import Figure
from io import BytesIO
import base64
from openai import OpenAI

from matplotlib.figure import Figure

# Initialize OpenAI client
#client = OpenAI(api_key="my key")
# response = client.chat.completions.create(
#      model="gpt-3.5-turbo",
#      messages=[{"role": "user", "content": "Hello, who are you?"}]
#  )
# print(response.choices[0].message.content)

#data = pd.read_excel("Dataz\ProjectData1.xlsx")

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
    try:
        # Get the user's input message
        user_message = request.json.get("message")

        # Send user input to OpenAI's GPT-3.5 Turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        # Extract AI's response
        ai_reply = response.choices[0].message.content
        return jsonify({"reply": ai_reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})
    # print("success")
    # return client.api_key


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