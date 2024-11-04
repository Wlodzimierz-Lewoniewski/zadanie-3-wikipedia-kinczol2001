import requests
from bs4 import BeautifulSoup

def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def generate_category_url(category_name):
    formatted_name = category_name.replace(" ", "_")
    category_url = f"https://pl.wikipedia.org/wiki/Kategoria:{formatted_name}"
    return category_url

def get_articles_from_category(category_url):
    html = get_html(category_url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.select('div#mw-pages li a')[:2]
    articles = []
    for link in links:
        article_url = f"https://pl.wikipedia.org{link['href']}"
        article_name = link.get_text()
        articles.append((article_name, article_url))
    return articles

def extract_article_data(article_url):
    html = get_html(article_url)
    if not html:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    links = [a for a in soup.select('a[href^="/wiki/"]') if ':' not in a['href'] and '/wiki/Kategoria:' not in a['href']][:5]
    article_links = [(link.get_text(), f"https://pl.wikipedia.org{link['href']}") for link in links]
    images = [img for img in soup.select('img') if img.get('src') and ('//upload.wikimedia.org' in img['src'] or 'upload.wikimedia.org' in img['src'])][:3]
    image_urls = [f"https:{img['src']}" if img['src'].startswith("//") else f"https://pl.wikipedia.org{img['src']}" for img in images]
    external_links = soup.select('ol.references li cite a.external')[:3]
    external_urls = [link['href'] for link in external_links]
    categories = soup.select('div#mw-normal-catlinks ul li a')[:3]
    category_names = [cat.get_text() for cat in categories]
    return {
        'article_links': article_links,
        'image_urls': image_urls,
        'external_urls': external_urls,
        'category_names': category_names
    }

def main():
    category_name = input("Podaj nazwę kategorii w polskojęzycznej Wikipedii: ")
    category_url = generate_category_url(category_name)
    print(f"Generowany URL kategorii: {category_url}")
    articles = get_articles_from_category(category_url)
    if not articles:
        print("Nie znaleziono artykułów w tej kategorii.")
        return
    for article_name, article_url in articles:
        print(f"\nArtykuł: {article_name}\nURL: {article_url}")
        data = extract_article_data(article_url)
        if data:
            print("\nOdnośniki do innych artykułów Wikipedii:")
            for text, url in data['article_links']:
                print(f"{text} -> {url}")
            print("\nAdresy URL obrazków:")
            for img in data['image_urls']:
                print(img)
            print("\nAdresy URL źródeł:")
            for src in data['external_urls']:
                print(src)
            print("\nKategorie artykułu:")
            for cat in data['category_names']:
                print(cat)
        else:
            print("Błąd w pobieraniu danych z artykułu.")

if __name__ == "__main__":
    main()
