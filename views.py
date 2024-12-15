from flask import render_template, g, Blueprint,request
import pandas as pd
from matplotlib.figure import Figure
from io import BytesIO
import base64

data = pd.read_excel("ProjectData.xlsx")

my_view = Blueprint(__name__,'my_view')


@my_view.route("/home")
def hello():
  return "hello"

@my_view.route("/")
def displayHomePage():

  data["Days"] = data['End date'] - data['Start date']

  fig = Figure()
  ax = fig.add_subplot()

  ax.barh(y=data['Project Name'],left=data['Start date'],width=data['Days'])

  buf = BytesIO()
  fig.savefig(buf, format="png")
# Embed the result in the html output.
  tempData = base64.b64encode(buf.getbuffer()).decode("ascii")
  return f"<img src='data:image/png;base64,{tempData}'/>"

@my_view.route('/dropdown', methods=['GET', 'POST'])
def dropdown():
    selected_option = None
    if request.method == 'POST':
        # Get the selected option from the form
        selected_option = request.form.get('dropdown', 'No option selected')
        projectManager = data.loc[data['Project Name']==selected_option,'Project manager'].item()
        return f"You selected: {projectManager}"

    return render_template('index.html')