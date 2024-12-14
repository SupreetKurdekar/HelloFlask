#Below is a Python code snippet to create a simple project management application using the Flask web framework and an SQLite database. This application includes functionalities to manage projects, tasks, and team members.

# Code for Project Management Application

# Step 1: Install dependencies

# Make sure to install the required dependencies before running the code:

# pip install flask flask-sqlalchemy flask-wtf

# Step 2: Application Code

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(_name_)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tasks = db.relationship('Task', backref='project', cascade="all, delete", lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Pending")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

# Forms
class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Project Description')
    submit = SubmitField('Add Project')

class TaskForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    description = TextAreaField('Task Description')
    submit = SubmitField('Add Task')

# Routes
@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data, description=form.description.data)
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('new_project.html', form=form)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project.id).all()
    return render_template('project_detail.html', project=project, tasks=tasks)

@app.route('/project/<int:project_id>/task/new', methods=['GET', 'POST'])
def new_task(project_id):
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(name=form.name.data, description=form.description.data, project_id=project_id)
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    return render_template('new_task.html', form=form, project_id=project_id)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('project_detail', project_id=task.project_id))

if _name_ == '_main_':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)

Step 3: Templates

Create the following HTML templates in a templates folder:
	1.	index.html:

<!doctype html>
<html>
<head>
    <title>Project Management</title>
</head>
<body>
    <h1>Project Management</h1>
    <a href="/project/new">Add New Project</a>
    <ul>
        {% for project in projects %}
        <li>
            <a href="{{ url_for('project_detail', project_id=project.id) }}">{{ project.name }}</a>
        </li>
        {% endfor %}
    </ul>
</body>
</html>

	2.	new_project.html:

<!doctype html>
<html>
<head>
    <title>Add Project</title>
</head>
<body>
    <h1>Add New Project</h1>
    <form method="POST">
        {{ form.hidden_tag() }}
        {{ form.name.label }} {{ form.name() }}<br>
        {{ form.description.label }} {{ form.description() }}<br>
        {{ form.submit() }}
    </form>
</body>
</html>

	3.	project_detail.html:

<!doctype html>
<html>
<head>
    <title>{{ project.name }}</title>
</head>
<body>
    <h1>{{ project.name }}</h1>
    <p>{{ project.description }}</p>
    <h2>Tasks</h2>
    <a href="{{ url_for('new_task', project_id=project.id) }}">Add New Task</a>
    <ul>
        {% for task in tasks %}
        <li>{{ task.name }} - {{ task.status }}
            <form method="POST" action="{{ url_for('delete_task', task_id=task.id) }}">
                <button type="submit">Delete</button>
            </form>
        </li>
        {% endfor %}
    </ul>
</body>
</html>

	4.	new_task.html:

<!doctype html>
<html>
<head>
    <title>Add Task</title>
</head>
<body>
    <h1>Add New Task to {{ project_id }}</h1>
    <form method="POST">
        {{ form.hidden_tag() }}
        {{ form.name.label }} {{ form.name() }}<br>
        {{ form.description.label }} {{ form.description() }}<br>
        {{ form.submit() }}
    </form>
</body>
</html>

Features
	•	Add projects
	•	View project details
	•	Add tasks to projects
	•	Delete tasks

You can expand this application further to include user authentication, task statuses, or progress tracking.