from flask import render_template, g, Blueprint,request
import os
import pandas as pd
from matplotlib.figure import Figure
from io import BytesIO
import base64

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
        # Append '.xlsx' to locate the file in the directory
        file_path = os.path.join(EXCEL_DIR, f"{selected_file_name}.xlsx")

        try:
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(file_path)
            table_html = df.to_html(classes="table table-striped table-bordered", index=False)
            return render_template("view_excel.html", file_name=selected_file_name, table_html=table_html)
        except Exception as e:
            return f"An error occurred while reading the file: {e}"
    else:
        return "No file was selected. Please try again."


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