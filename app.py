from config import DB_URI
from flask import Flask, request, render_template, redirect, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['DEBUG'] = True


engine = create_engine(DB_URI)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",  methods=["GET"])
def index():
    
    return jsonify("Hello World")
