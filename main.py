import requests
from bs4 import BeautifulSoup
 
def fetch_articles(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
 
    try :
        response = requests.get(url, headers=headers)
        response.raise_for_status()
 
        soup = BeautifulSoup(response.text, 'html.parser')
 
        main_tag = soup.find('main')
        if not main_tag:
            print("no <main> tag found")
   
        articles = main_tag.find_all('article')
        for article in articles :

            # # titre de l'article
            # title_tag = article.find('h3', class_='entry-title')
            # if title_tag:
            #     title_text = title_tag.get_text(strip=True)
            #     print(title_text)


            # # image de l'article
            # img_div = article.find(
            #     'div',
            #     class_='post-thumbnail'
            # )
            # img_tag = img_div.find('img') if img_div else None
            # img_url = extract_img_url(img_tag)
            # print(img_url)
            
            # lien vers l'article complet
            link_tag = article.find('a')
            if link_tag and link_tag['href']:
                article_url = link_tag['href']
                
                article_content = scrape_article(article_url)
                
                # sommaire de l'article
                # summary_list = get_summary(article_content)
                # if summary_list:
                #     print(summary_list)

                # catégories de l'article
                categories_div = article_content.find('ul', class_='tags-list')
                if categories_div:
                    categories = [li.get_text(strip=True) for li in categories_div.find_all('li')]
                    print(categories)
                    
                # résumé de l'article
                resume_div = article_content.find('div', class_='article-hat')
                if resume_div:
                    resume_text = resume_div.get_text(strip=True)
                    print(resume_text)
            
            
        return []
    except requests.exceptions.RequestException as e :
        print(f"Error: {e}")
        return []
    
 
def extract_img_url(img_tag):
    if not img_tag:
        return None
    url_attrs = [
        'src',
        'data-lazy-srcset',
        'data-lazy-src'
    ]
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
 
    try :
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
 
        soup = BeautifulSoup(response.text, 'html.parser')
 
        main_tag_article = soup.find('main')
        if not main_tag_article:
            print("no <main> tag found")
            
        return main_tag_article
    except requests.exceptions.RequestException as e :
        print(f"Error: {e}")
        return []
    
 
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
 

url = "https://www.blogdumoderateur.com/web/"
articles = fetch_articles(url)