import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["scraping_tp"]
collection = db["articles"]


def fetch_articles(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        main_tag = soup.find('main')
        if not main_tag:
            print("no <main> tag found")
            return []

        articles = main_tag.find_all('article')
        for article in articles:

            link_tag = article.find('a')
            if link_tag and link_tag['href']:
                article_url = link_tag['href']
                article_content = scrape_article(article_url)

                if not article_content:
                    continue

                # Dictionnaire de l'article
                article_data = {}

                # Titre
                title_tag = article.find('h3', class_='entry-title')
                article_data['title'] = title_tag.get_text(strip=True) if title_tag else None

                # Sommaire
                article_data['summary'] = get_summary(article_content)

                # Images
                article_data['images'] = get_article_images(article_content)

                # Auteur
                author_tag = article_content.find('span', class_='byline')
                article_data['author'] = author_tag.get_text(strip=True) if author_tag else None

                # Date
                time_tag = article_content.find('time', class_='entry-date')
                if time_tag and time_tag.has_attr('datetime'):
                    article_data['date'] = time_tag['datetime'].split('T')[0]
                else:
                    article_data['date'] = None

                # Catégories
                categories_div = article_content.find('ul', class_='tags-list')
                if categories_div:
                    article_data['categories'] = [li.get_text(strip=True) for li in categories_div.find_all('li')]
                else:
                    article_data['categories'] = []

                # Résumé (article-hat)
                resume_div = article_content.find('div', class_='article-hat')
                article_data['resume'] = resume_div.get_text(strip=True) if resume_div else None

                # Sauvegarde MongoDB
                collection.insert_one(article_data)
                print("✅ Article inséré :", article_data['title'])

        return []

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


def extract_img_url(img_tag):
    if not img_tag:
        return None
    url_attrs = ['src', 'data-lazy-srcset', 'data-lazy-src']
    for attr in url_attrs:
        if img_tag.has_attr(attr):
            url = img_tag[attr]
            if url and url.startswith('https://'):
                return url
    return None


def scrape_article(article_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        main_tag_article = soup.find('main')
        if not main_tag_article:
            print("no <main> tag found")
            return None

        return main_tag_article

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def get_summary(soup):
    # 1. Listes ordonnées
    ol_tag = soup.find('ol', class_='summary-inner')
    if ol_tag:
        return [li.get_text(strip=True) for li in ol_tag.find_all('li')]

    # 2. Listes non ordonnées
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


# URL à scraper
url = "https://www.blogdumoderateur.com/web/"
articles = fetch_articles(url)
