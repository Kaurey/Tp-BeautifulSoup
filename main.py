import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["scraping_db"]
collection = db["articles"]
collection.create_index("article_url", unique=True)


def fetch_articles(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        main_tag = soup.find('main')
        if not main_tag:
            print("Pas de <main> trouvé")
            return []

        articles = main_tag.find_all('article')
        for article in articles:
            # lien vers l'article complet
            link_tag = article.find('a')
            if not link_tag or not link_tag['href']:
                continue

            article_url = link_tag['href']
            article_content = scrape_article(article_url)

            if not article_content:
                continue
            
            # === Miniature ===
            thumbnail_url = None
            thumbnail_div = article.find('div', class_='post-thumbnail')
            if thumbnail_div:
                thumbnail_img = thumbnail_div.find('img')
                if thumbnail_img:
                    thumbnail_url = extract_img_url(thumbnail_img)

            if not thumbnail_url:
                thumbnail_url = "Aucune miniature"


            # === HEADER ===
            header = article_content.find('header')
            title = header.find('h1').get_text(strip=True) if header else None

            time_tag = header.find('time', class_='entry-date') if header else None
            if time_tag and time_tag.has_attr('datetime'):
                date_formatted = time_tag['datetime'].split('T')[0]
            else:
                date_formatted = None

            author_tag = header.find('span', class_='byline') if header else None
            author = author_tag.get_text(strip=True) if author_tag else None

            # === CONTENU PRINCIPAL ===
            content = article_content.find('div', class_='entry-content')
            if content:
                # Supprimer les balises inutiles
                for tag in content.find_all(['script', 'style', 'aside', 'noscript']):
                    tag.decompose()
                content_text = content.get_text("\n", strip=True)
                content_text = " ".join(content_text.split())  # supprime espaces multiples
            else:
                content_text = None


            # Sommaire
            summary_list = get_summary(article_content)

            # Catégories
            categories_div = article_content.find('ul', class_='tags-list')
            categories = [li.get_text(strip=True) for li in categories_div.find_all('li')] if categories_div else []

            # Résumé
            resume_div = article_content.find('div', class_='article-hat')
            resume_text = resume_div.get_text(strip=True) if resume_div else None

            # Images
            images = get_article_images(article_content)

            # Préparer document MongoDB
            article_doc = {
                "article_url": article_url,
                "title": title,
                "thumbnail": thumbnail_url,
                "date": date_formatted,
                "author": author,
                "summary": summary_list,
                "categories": categories,
                "resume": resume_text,
                "content": content_text,
                "images": images
            }

            result = collection.update_one(
                {"article_url": article_url},
                {"$set": article_doc},
                upsert=True
            )
            if result.upserted_id:
                print(f"✅ Nouvel article inséré : {title}")
            else:
                print(f"🔄 Article mis à jour : {title}")


    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête : {e}")


def extract_img_url(img_tag):
    if not img_tag:
        return None
    url_attrs = ['src', 'srcset', 'data-src', 'data-lazy-src', 'data-lazy-srcset']
    for attr in url_attrs:
        if img_tag.has_attr(attr):
            url = img_tag[attr]
            if url and url.startswith('http'):
                return url.split()[0]
    return None


def scrape_article(article_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article_tag = soup.find('main').find('article')
        return article_tag
    except Exception as e:
        print(f"Erreur scrape_article : {e}")
        return None


def get_summary(soup):
    if not soup:
        return None
    ol_tag = soup.find('ol', class_='summary-inner')
    if ol_tag:
        return [li.get_text(strip=True) for li in ol_tag.find_all('li')]
    ul_tag = soup.find('ul', class_='summary-inner')
    if ul_tag:
        return [li.get_text(strip=True) for li in ul_tag.find_all('li')]
    return None


def get_article_images(soup):
    images = []
    if not soup:
        return images
    for img_tag in soup.find_all('img'):
        img_url = extract_img_url(img_tag)
        if img_url:
            caption = img_tag.get('alt') or img_tag.get('title') or ""
            images.append({'url': img_url, 'caption': caption})
    return images


# URL principale
url = "https://www.blogdumoderateur.com/web/"
fetch_articles(url)
