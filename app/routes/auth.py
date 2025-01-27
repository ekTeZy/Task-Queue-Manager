from flask import Blueprint, render_template, redirect, url_for



auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET"])
def register():
    return render_template('register.html')



@auth_bp.route("/login", methods=["GET"])
def login():
    return render_template('login.html')