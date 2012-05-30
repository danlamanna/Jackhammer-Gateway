from flask import Flask, jsonify, request
app = Flask(__name__)

import json
import os

"""
Create a new project  - POST /project/create
View all projects     - GET  /projects/read
View single project   - GET  /project/read/project_slug
Delete single project - GET  /project/delete/project_slug
"""

# create
@app.route("/project/create", methods=["POST"])
def create_project():
    post_data = request.form

    if "project_slug" not in post_data or "project_data" not in post_data:
        return error_json("", "project_slug and project_data fields required.")
    else:
        project_manifest = json.load(open("project_manifest.json"))

        project_slug, project_data = post_data["project_slug"], post_data["project_data"]

        if post_data["project_slug"] in project_manifest["projects"]:
            return error_json("", "Project already exists in manifest.")
        else:
            project_manifest["projects"][project_slug] = project_data
            
            json.dump(project_manifest, open(get_base_dir("project_manifest.json"), "w+"), indent=4)

            ret_data = { project_slug: project_manifest["projects"][project_slug] }

            return success_json(ret_data, "Project created.")

    return error_json("", "Something went wrong!")

# read
@app.route("/projects/read")
def read_projects():
    try:
        project_manifest = json.load(open(get_base_dir("project_manifest.json")))
        
        return success_json(project_manifest)
    except IOError:
        return error_json("", "Project manifest unable to be read.")        

@app.route("/project/read/<project_slug>")
def read_project(project_slug):
    try:
        project_manifest = json.load(open(get_base_dir("project_manifest.json")))

        return success_json(project_manifest["projects"][project_slug])            
    except IOError:
        return error_json("", "Project manifest unable to be read.")
    except KeyError:
        return error_json("", "Project doesn't exist in manifest.")    

# delete
@app.route("/project/delete/<project_slug>")
def delete_project(project_slug):
    project_manifest = json.load(open(get_base_dir("project_manifest.json")))

    if project_slug not in project_manifest["projects"]:
        return error_json("", "Project doesn't exist in manifest.")
    else:
        del(project_manifest["projects"][project_slug])
        
        json.dump(project_manifest, open(get_base_dir("project_manifest.json"), "w+"), indent=4)

        return success_json("", "Project deleted.")

    return error_json("", "Something went wrong!")


def get_base_dir(file_name):
    return os.path.abspath(os.path.dirname(__file__)) + "/" + file_name


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
