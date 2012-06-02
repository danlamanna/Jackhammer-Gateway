from flask import Flask, jsonify, request
from mongokit import Connection, Document

import bson
from bson import BSON, json_util

import json

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27018

app = Flask(__name__)
app.config.from_object(__name__)

conn = Connection(app.config["MONGODB_HOST"],
                  app.config["MONGODB_PORT"])

db = conn.jackhammer

projects = db.projects

def actual_slug():
    import re
    def validate(value):
        if not re.match('^\w+$', value):
            raise Exception('%s is not a valid slug, only alphanumeric characters and underscores allowed.' % value)
        else:
            return True
    return validate

class Project(Document):
    structure = {
        'slug': basestring
    }

    validators = {
        'slug': actual_slug()
    }

    required_fields = ['slug']

    use_dot_notation = True
    use_schemaless   = True

    def __repr__(self):
        return '<Project %s>' % self.slug

conn.register([Project])

"""
Create a new project  - POST /project/create
View all projects     - GET  /projects/read
View single project   - GET  /project/read/project_slug
Delete single project - GET  /project/delete/project_slug
"""

# create
@app.route("/project/create", methods=["POST"])
def create_project():
    try:
        project = projects.Project()
        
        for k,v in json.loads(request.form["project_data"]).iteritems():
            project[k] = v

            

        project.save()

        return success_json("", "Project created.")
    except:
        return error_json("", "Project failed to be created.")
    
# read
@app.route("/projects/read")
def read_projects():
    project_cursor  = projects.find()

    project_records = {}

    for record in project_cursor:
        del(record["_id"]) # sloppy fix, learn json/bson_util
        project_records[record["slug"]] = record

    return success_json(project_records)

@app.route("/project/read/<project_slug>")
def read_project(project_slug):
    try:
        project = projects.find_one({ "slug": project_slug })

        del(project["_id"])

        return success_json(project)
    except:
        return error_json("", "Project not in manifest.")

@app.route("/project/update/<project_slug>")
def update_project(project_slug, methods=["POST"]):
    try:
        project = projects.find_one({ "slug": project_slug })

        update_data = json.loads(request.form["project_data"])

        # edge case, if they go to /project/update/a and pass a slug of something other than a
        if "slug" in update_data:
            del(update_data["slug"])

        final_project_data = dict(project.items() + update_data.items())

        projects.update({ _id: project._id }, final_project_data)
    except:
        return error_json("", "Something went wrong!")        

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
