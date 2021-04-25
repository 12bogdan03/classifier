import csv
import re
import uuid

import requests
from bs4 import BeautifulSoup
import concurrent.futures

from pdfminer.high_level import extract_text

session = requests.Session()
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
}
session.headers.update(headers)


def get_issues():
    r = session.get('https://il-journal.com/index.php/journal')
    soup = BeautifulSoup(r.text, "html.parser")
    divs = soup.select('#customblock-ARCHIVE > div')
    result = list()
    for div in divs:
        links = div.find_all('a')
        for link in links:
            href = link.get('href')
            if re.match(r'https://il-journal\.com/index\.php/journal/issue/view/\d+', href):
                result.append(href)
    return result


def get_issue_articles(issue_link: str):
    r = session.get(issue_link)
    soup = BeautifulSoup(r.text, "html.parser")
    divs = soup.select('#pkp_content_main > div > div > div.sections')
    result = list()
    for div in divs:
        links = div.find_all('a')
        for link in links:
            href = link.get('href')
            if re.match(r'https://il-journal\.com/index\.php/journal/article/view/\d+', href):
                result.append(href)
    return result


def get_pdf(view_pdf_link: str):
    r = session.get(view_pdf_link)
    soup = BeautifulSoup(r.text, "html.parser")
    download_btn_link = soup.find('a', class_='download').get('href')
    r = session.get(download_btn_link)
    path = f"il_journal_articles/{uuid.uuid4()}.pdf"
    file = open(path, "wb")
    file.write(r.content)
    file.close()
    return path


def parse_pdf(file_path: str):
    text = extract_text(file_path)
    text = re.sub(r'DOI:.+?\n', '', text)
    text = re.sub(r'УДК:.+?\n', '', text)
    text = re.sub(r'e-mail:.+?\n', '', text)
    text = re.sub(r'Ключові слова:.+?\.', '', text)
    text = re.sub(r'ISSN .+?\n', '', text)
    text = re.sub(r'ORCID:.+?\n', '', text)
    text = re.sub(r'O RCID:.+?\n', '', text)
    text = re.sub(r'Слово і Час.+?\n', '', text)
    text = re.sub(r'\nЛІТЕРАТУРА\n[\w\W]+', '', text)
    return text


def parse_article(article_link: str):
    r = session.get(article_link)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        title = soup.find('h1', class_='page_title').getText().strip()
        authors = soup.select_one(
            '#pkp_content_main > div > article > div > div.main_entry > ul > li > span.name').getText().strip()
        school = soup.select_one(
            '#pkp_content_main > div > article > div > div.main_entry > ul > li > span.affiliation').getText().strip()
        keywords = soup.select_one(
            '#pkp_content_main > div > article > div > div.main_entry > div.item.keywords > span.value').getText().strip()
        annotation = soup.select_one(
            '#pkp_content_main > div > article > div > div.main_entry > div.item.abstract > p').getText().strip()
        categories = soup.select_one(
            '#pkp_content_main > div > article > div > div.entry_details > '
            'div.item.issue > div:nth-child(2) > div.value').getText().strip()
        view_pdf_link = soup.select_one('#pkp_content_main > div > article > div > '
                                        'div.entry_details > div.item.galleys > ul > li > a').get('href')
        pdf_file = get_pdf(view_pdf_link)
        body = parse_pdf(pdf_file)
    except AttributeError:
        return
    return {
        'link': article_link,
        'title': title,
        'school': school,
        'authors': authors,
        'annotation': annotation,
        'keywords': keywords,
        'categories': categories,
        'text': body,
    }


file = open('il-journal.csv', 'w')

writer = csv.DictWriter(file, fieldnames=['title', 'authors', 'school', 'annotation', 'keywords',
                                          'categories', 'text', 'link'])
writer.writeheader()

issues = get_issues()
for link in issues:
    articles = get_issue_articles(link)
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = []
        for article in articles:
            futures.append(executor.submit(parse_article, article_link=article))
        for future in concurrent.futures.as_completed(futures):
            parsed = future.result()
            if parsed:
                writer.writerow(parsed)

    print(f"{link} processed. Articles: {len(articles)}")

file.close()
