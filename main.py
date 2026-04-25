import requests
from bs4 import BeautifulSoup
import csv
import re
import time


BASE_URL = "https://www.bbc.com"
START_URL = "https://www.bbc.com/news"


def clean_text(text):
    """Очищення тексту від зайвих пробілів і переносів."""
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_html(url):
    """Завантаження HTML-сторінки."""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Помилка завантаження сторінки {url}: {response.status_code}")
            return None

        return response.text

    except requests.RequestException as error:
        print(f"Помилка HTTP-запиту: {error}")
        return None


def extract_article_text(article_url):
    """Витягування повного тексту новини."""
    html = fetch_html(article_url)

    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    paragraphs = soup.find_all("p")

    text_parts = []

    for paragraph in paragraphs:
        text = clean_text(paragraph.get_text())

        if len(text) > 30:
            text_parts.append(text)

    article_text = " ".join(text_parts)
    return clean_text(article_text)


def parse_bbc_news(html, limit=20):
    """Парсинг новин BBC: заголовок, посилання, текст."""
    soup = BeautifulSoup(html, "html.parser")

    links = soup.find_all("a", href=True)

    articles = []
    seen_urls = set()

    for link in links:
        title = clean_text(link.get_text())
        href = link.get("href")

        if not title or len(title) < 20:
            continue

        if not href.startswith("/news/articles/"):
            continue

        full_url = BASE_URL + href

        if full_url in seen_urls:
            continue

        seen_urls.add(full_url)

        print(f"Обробка новини: {title}")

        article_text = extract_article_text(full_url)

        if len(article_text) < 100:
            continue

        articles.append({
            "title": title,
            "url": full_url,
            "text": article_text
        })

        time.sleep(0.5)

        if len(articles) >= limit:
            break

    return articles


def save_to_csv(data, filename):
    """Збереження результатів у CSV-файл."""
    with open(filename, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow(["Title", "URL", "Text"])

        for item in data:
            writer.writerow([
                item["title"],
                item["url"],
                item["text"]
            ])


def main():
    print("Завантаження BBC News...")

    html = fetch_html(START_URL)

    if not html:
        print("Не вдалося завантажити головну сторінку.")
        return

    with open("bbc_html.html", "w", encoding="utf-8") as file:
        file.write(html)

    news = parse_bbc_news(html, limit=20)

    print(f"Знайдено і оброблено новин: {len(news)}")

    if not news:
        print("Новини не знайдені.")
        return

    save_to_csv(news, "bbc_news.csv")

    print("Дані збережено у файл bbc_news.csv")


if __name__ == "__main__":
    main()