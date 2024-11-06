import requests
from bs4 import BeautifulSoup
import html

# Pobiera pierwsze 5 linków wewnętrznych z artykułu.
def extract_internal_links(content_div):
    internal_links = [
        link['title'] for link in content_div.find_all('a', href=True)
        if link['href'].startswith('/wiki/') and ':' not in link['href'][6:]
    ]
    return internal_links[:5]

# Pobiera źródła pierwszych 3 obrazków w artykule.
def extract_image_urls(content_div):
    images = content_div.find_all("img")
    return [img["src"] for img in images if '/wiki/' not in img['src']][:3]

# Pobiera pierwsze 3 zewnętrzne odnośniki z artykułu.
def extract_external_links(soup_obj):
    ref_section = soup_obj.find("div", class_="mw-references-wrap mw-references-columns")
    if not ref_section:
        ref_section = soup_obj.find("div", class_="do-not-make-smaller refsection")

    if ref_section:
        external_links = [
            link['href'] for item in ref_section.find_all("li")
            for span in item.find_all("span", class_="reference-text")
            for link in span.find_all("a", href=True) if "http" in link['href']
        ]
        return " | ".join(html.escape(url) for url in external_links[:3])
    return ""

# Pobiera pierwsze 3 kategorie przypisane do artykułu.
def extract_categories(soup_obj):
    category_div = soup_obj.find("div", class_="mw-normal-catlinks")
    if category_div:
        category_list = category_div.find('ul')
        return " | ".join(cat.text.strip() for cat in category_list.find_all("a")[:3])
    return ""

# Zwraca informacje z artykułu Wikipedii.
def retrieve_article_info(article_name):
    page_url = f'https://pl.wikipedia.org{article_name}'
    response = requests.get(page_url)

    if response.status_code != 200:
        print("Błąd podczas pobierania strony:", response.status_code)
        return []

    parsed_page = BeautifulSoup(response.text, 'html.parser')
    content_div = parsed_page.find("div", class_="mw-body-content")

    # Zbieranie danych z artykułu
    internal_links = extract_internal_links(content_div)
    image_urls = extract_image_urls(content_div)
    external_links = extract_external_links(parsed_page)
    categories = extract_categories(parsed_page)

    # Zwrócenie wyników w formie listy
    return [
        " | ".join(internal_links),
        " | ".join(image_urls),
        external_links,
        categories
    ]

# Pobiera pierwsze dwa linki artykułów z wybranej kategorii.
def retrieve_category_articles(category_name):
    url = f'https://pl.wikipedia.org/wiki/Kategoria:{category_name}'
    response = requests.get(url)

    if response.status_code != 200:
        print("Błąd podczas pobierania strony:", response.status_code)
        return []

    parsed_page = BeautifulSoup(response.text, 'html.parser')
    category_content = parsed_page.find("div", class_="mw-category mw-category-columns")
    category_links = category_content.find_all("a")

    # Zwraca pierwsze dwa linki artykułów z kategorii
    return [link["href"] for link in category_links[:2]]

# Główna funkcja programu obsługująca interakcję z użytkownikiem.
def main():
    category_name = input("Podaj nazwę kategorii: ").replace(" ", "_")

    # Pobieramy artykuły z podanej kategorii
    articles = retrieve_category_articles(category_name)

    # Dla każdego artykułu pobieramy i wyświetlamy dane
    for article in articles:
        article_info = retrieve_article_info(article)
        for info in article_info:
            print(info)


if __name__ == "__main__":
    main()
