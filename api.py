from flask import Flask, jsonify, request
app = Flask(__name__)

import json
import os

import pymongo
from pymongo import Connection

conn = Connection()

db = conn.jackhammer_manifest

projects = db.projects

"""
Create a new project  - POST /project/create
View all projects     - GET  /projects/read
View single project   - GET  /project/read/project_slug
Delete single project - GET  /project/delete/project_slug
"""

# create
@app.route("/project/create", methods=["POST"])
def create_project():
    project_def = json.loads(request.form["project_data"])
    projects.insert(project_def)
    
    return success_json("", "Project created.")
    
# read
@app.route("/projects/read")
def read_projects():
    projects_list = []
    
    for proj in projects.find():
        del(proj["_id"])
        projects_list.append(proj)
    
    return success_json(projects_list)

@app.route("/project/read/<project_slug>")
def read_project(project_slug):
    project = projects.find({ "slug": project_slug }).limit(1)

    if project.count() > 0:
        project = project[0]
        del(project["_id"])

        return success_json(project)
    else:
        return error_json("", "Project not in manifest.")

# delete
@app.route("/project/delete/<project_slug>")
def delete_project(project_slug):
    projects.remove({ "slug": project_slug })

    return success_json("", "Project deleted.")

def error_json(data, message=""):
    return jsonify(success=0,
                   message=message,
                   data=data)

def success_json(data, message=""):
    return jsonify(success=1,
                   message=message,
                   data=data)

if __name__ == "__main__":
    app.run()
