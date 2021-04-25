import csv
import re

import requests
from bs4 import BeautifulSoup
import concurrent.futures


cookies = {"qtrans_front_language": "ua"}
session = requests.Session()
session.cookies.update(cookies)


def get_categories():
    r = session.get('https://nauka-online.com/ua/rubriki/')
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select_one('section.tegz > div > div:nth-child(3)').find_all('a')
    result = dict()
    for link in links:
        href = link.get('href')
        text = link.getText()
        result[text] = href
    return result


def get_category_articles(category_link: str):
    r = session.get(category_link)
    soup = BeautifulSoup(r.text, "html.parser")
    # process page 1
    articles = soup.find_all('article')
    result = list()
    for article in articles:
        link = article.find('a', class_='sss')
        result.append(link.get('href'))
    next_page = soup.find('a', class_='next')

    while next_page:
        r = session.get(next_page.get('href'))
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.find_all('article')
        for article in articles:
            link = article.find('a', class_='sss')
            result.append(link.get('href'))
        next_page = soup.find('a', class_='next')

    return result


def clean_text(text: str):
    text = re.sub(r'DOI:.+?\n', '', text)
    text = re.sub(r'УДК:.+?\n', '', text)
    text = re.sub(r'e-mail:.+?\n', '', text)
    text = re.sub(r'Ключові слова:.+?\.', '', text)
    text = re.sub(r'Ключевые слова:.+?\.', '', text)
    text = re.sub(r'Key words:.+?\.', '', text)
    text = re.sub(r'ISSN .+?\n', '', text)
    text = re.sub(r'ORCID:.+?\n', '', text)
    text = re.sub(r'O RCID:.+?\n', '', text)
    text = re.sub(r'\nЛітература\n[\w\W]+', '', text)
    text = re.sub(r'Анотація\.[\w\W]+(?:Ключові слова)', '', text)
    text = re.sub(r'Аннотация\.[\w\W]+(?:Ключевые слова)', '', text)
    text = re.sub(r'Summary\.[\w\W]+(?:Key words)', '', text)
    text = re.sub(r'Рис\. \d{1,5}\.', '', text)
    text = re.sub(r'Таблиця\.? \d{1,5}\.?', '', text)
    return text



def parse_article(article_link: str):
    r = session.get(article_link)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find('h3').getText().strip()
    authors = soup.find('div', class_='article_aftor art_list').getText().replace("Автор:", "").strip()
    annotation = soup.find('div', class_='article_anotacia').getText().replace("Анотація:", "").strip()
    keyword_links = soup.find_all('div', class_='article_keywords art_list')[0].find_all('a')
    keywords = []
    for link in keyword_links:
        keywords.append(link.getText().strip())

    category_links = soup.find_all('div', class_='article_keywords art_list')[1].find_all('a')
    category_list = []
    for link in category_links:
        category_list.append(link.getText().strip())

    body = soup.find('div', class_='statia-body').getText().strip()
    if body == 'Вибачте цей текст доступний тільки в “Російська”.':
        return

    return {
        'link': article_link,
        'title': title,
        'authors': authors,
        'annotation': annotation,
        'keywords': keywords,
        'categories': category_list,
        'text': clean_text(body),
    }


file = open('nauka-online.csv', 'w')

writer = csv.DictWriter(file, fieldnames=['title', 'authors', 'annotation', 'keywords',
                                          'main_category', 'categories', 'text', 'link'])
writer.writeheader()

categories = get_categories()
for category, link in categories.items():
    articles = get_category_articles(link)
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = []
        for article in articles:
            futures.append(executor.submit(parse_article, article_link=article))
        for future in concurrent.futures.as_completed(futures):
            parsed = future.result()
            if parsed:
                parsed['main_category'] = category
                writer.writerow(parsed)

    # for article in articles:
    #     parsed = parse_article(article)
    #     parsed['main_category'] = category
    #     writer.writerow(parsed)
    print(f"{category} processed. Articles: {len(articles)}")

file.close()
