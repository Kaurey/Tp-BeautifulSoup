# app.py (Flask minimal)
from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["scraping_db"]
collection = db["articles"]

@app.route("/", methods=["GET"])
def index():
    # Récupération des filtres depuis le formulaire
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    author = request.args.get("author")
    category = request.args.get("category")
    subcategory = request.args.get("subcategory")
    title_contains = request.args.get("title_contains")

    query = {}

    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date
        if not query["date"]:
            query.pop("date")

    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if category:
        query["categories"] = category
    if subcategory:
        query["categories"] = subcategory
    if title_contains:
        query["title"] = {"$regex": title_contains, "$options": "i"}

    articles = list(collection.find(query).sort("date", -1))
    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True)
