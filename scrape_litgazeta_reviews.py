import csv
import re

import requests
from bs4 import BeautifulSoup
import concurrent.futures


session = requests.Session()
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
}
session.headers.update(headers)


def get_articles():
    result = set()

    for current_page in range(1, 101):
        data = {
            "action": "td_ajax_loop",
            "loopState[sidebarPosition]": "",
            "loopState[moduleId]": 10,
            "loopState[currentPage]": current_page,
            "loopState[max_num_pages]": 100,
            "loopState[atts][category_id]": 12,
            "loopState[ajax_pagination_infinite_stop]": 0,
        }
        r = session.post('https://litgazeta.com.ua/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=9.2.2',
                         data=data).json()
        if not r.get("server_reply_html_data"):
            break

        soup = BeautifulSoup(r.get("server_reply_html_data"), "html.parser")
        links = soup.select('div.item-details > h3 > a')
        for link in links:
            href = link.get('href')
            if re.match(r'https://litgazeta.com.ua/reviews/.+/', href):
                result.add(href)
                print(href)
                print(current_page)
    return result


def clean_text(text: str):
    text = re.sub(r'Передплатіть УЛГ у форматі PDF!', '', text)
    text = re.sub(r'Прокоментуєте\?', '', text)
    text = re.sub(r'^\(.+?\)\n', '', text)
    text = re.sub(r'“Українська літературна газета”, ч\..+?\n', '', text)
    text = re.sub(r'Передплатіть «Українську літературну газету» в паперовому форматі! '
                  r'Передплатний індекс: 49118\.', '', text)
    text = re.sub(r'Передплатіть «Українську літературну газету» в електронному форматі\..+?\n', '', text)
    text = re.sub(r'“Українську літературну газету” можна придбати в Києві у '
                  r'Будинку письменників за адресою м. Київ, вул. Банкова, 2.', '', text)
    return text


def parse_article(article_link: str):
    r = session.get(article_link)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        title = soup.find('h1', class_='entry-title').getText().strip()
        date = soup.select_one('div.td-post-header > header > div > span > time').getText().strip()
        text = soup.find('div', class_='td-post-content').getText().strip()
        body = clean_text(text)
    except AttributeError:
        return
    return {
        'link': article_link,
        'title': title,
        'date': date,
        'category': 'review',
        'text': body,
    }


file = open('litgazeta_reviews.csv', 'w')

writer = csv.DictWriter(file, fieldnames=['title', 'date', 'category', 'text', 'link'])
writer.writeheader()

articles = get_articles()
for link in articles:
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = []
        futures.append(executor.submit(parse_article, article_link=link))
        for future in concurrent.futures.as_completed(futures):
            parsed = future.result()
            print(parsed)
            if parsed:
                writer.writerow(parsed)

    print(f"{link} processed. Articles: {len(articles)}")

file.close()
