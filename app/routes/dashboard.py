from flask import Blueprint, render_template, redirect, url_for


dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET", "POST"])
def primary_dashboard():
    return render_template("dashboard.html")