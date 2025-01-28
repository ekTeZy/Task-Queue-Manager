from flask import Blueprint, render_template, redirect, url_for

index_bp = Blueprint("index", __name__)


@index_bp.route("/", methods=["GET"])
def index_page():
    return render_template("index/index.html")



@index_bp.route("/about", methods=["GET"])
def get_about():
    return render_template("about_page.html")