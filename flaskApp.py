import base64
from io import BytesIO

from flask import Flask

from matplotlib.figure import Figure
from io import BytesIO

import pandas as pd

# data loading

data = pd.read_excel("ProjectData.xlsx")
data["Days"] = data['End date'] - data['Start date']

fig = Figure()
ax = fig.add_subplot()

ax.barh(y=data['Project Name'],left=data['Start date'],width=data['Days'])

buf = BytesIO()
fig.savefig(buf, format="png")

# app creation
app = Flask(__name__)

# page display

@app.route("/")
def hello():
    # Generate the figure **without using pyplot**.
    # fig = Figure()
    # ax = fig.subplots()
    # ax.plot([1, 2])
    # # Save it to a temporary buffer.
    # buf = BytesIO()
    # fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

if __name__ == "__main__":
    app.run()