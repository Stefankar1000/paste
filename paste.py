import os
from datetime import datetime

from flask import Flask, request, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import shortuuid

from utils import identify_language
from filetypes import filetypes


app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///paste.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)


class Paste(db.Model):
    __tablename__ = "pastes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    content = db.Column(db.String)
    language = db.Column(db.String)
    created_at = db.Column(db.DateTime)

    def __init__(self, name: str, content: str, language: str):
        self.name = name
        self.content = content
        self.language = language
        self.created_at = datetime.utcnow()


db.create_all()


@app.route("/create", methods=["POST"])
def create_paste():
    if not (content := request.args.get("content")):
        return {"error": "Content is required"}, 400

    if not (name := request.args.get("name")):
        name = shortuuid.random(8)
        while Paste.query.filter(Paste.name == name).first():
            # Create new names until one is not taken
            name = shortuuid.random(8)

    if not (language := request.args.get("language")):
        language = identify_language(content)
        # Append '.<language>' to the name
        name += "." + filetypes[language]

    if Paste.query.filter(Paste.name == name).first():
        return {"error": "Name is in use"}, 400

    paste = Paste(name, content, language)
    db.session.add(paste)
    db.session.commit()
    url = url_for("get_paste", name=name, _external=True)

    return {
        "name": name,
        "url": url,
        "language": language,
        "created_at": paste.created_at,
    }


@app.route("/<string:name>", methods=["GET"])
def get_paste(name: str):
    if not (paste := Paste.query.filter(Paste.name == name).first()):
        return {"error": "Paste not found"}, 404

    return {
        "name": paste.name,
        "content": paste.content,
        "language": paste.language,
        "created_at": paste.created_at,
    }


@app.route("/raw/<string:name>", methods=["GET"])
def get_raw_paste(name: str):
    if not (paste := Paste.query.filter(Paste.name == name).first()):
        return {"error": "Paste not found"}, 404

    response = make_response(paste.content)
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
