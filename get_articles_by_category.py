from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["scraping_db"]
collection = db["articles"]

def get_articles_by_category(category_name):
    """
    Retourne tous les articles contenant la catégorie ou sous-catégorie donnée.
    """
    query = {
        "categories": {"$in": [category_name]}
    }
    articles = list(collection.find(query))
    
    if not articles:
        print(f"Aucun article trouvé pour la catégorie/sous-catégorie : {category_name}")
        return []
    
    for article in articles:
        print(f"- {article.get('title')} ({article.get('date')}) | URL: {article.get('article_url')}")
    
    return articles

# Exemple d'utilisation
cat_input = input("Entrez la catégorie ou sous-catégorie : ")
get_articles_by_category(cat_input)
