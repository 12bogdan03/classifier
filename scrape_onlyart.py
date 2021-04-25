import csv

import requests
from bs4 import BeautifulSoup
import concurrent.futures


session = requests.Session()
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
}
session.headers.update(headers)


def get_authors():
    r = session.get('https://onlyart.org.ua/ukrainian-poets/', timeout=60)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find('div', class_='one_fourth').find_all('a')
    result = dict()
    for link in links:
        text = link.getText().strip()
        href = link.get('href')
        result[text] = href
    return result


def get_author_links(author_link: str):
    r = session.get(author_link, timeout=60)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find('div', class_='entry').find_all('a')
    result = set()
    for link in links:
        text = link.getText().strip()
        if 'Біографія' in text or 'Афоризми' in text:
            continue
        href = link.get('href')
        if 'http://' in href:
            result.add(href)

    return result


def clean_text(text: str):
    return text


def parse_item(item_link: str, author: str):
    r = None
    max_attempts = 3
    attempts = 0
    while attempts <= max_attempts:
        try:
            r = session.get(item_link, timeout=20)
            break
        except Exception as e:
            print(f"{item_link}: {e}", {attempts})

    if not r:
        return

    soup = BeautifulSoup(r.text, "html.parser")
    author_names = author.split()
    try:
        title = soup.find('title').getText().strip().split(' | ')[0]
        if ' – ' in title:
            splitted = title.split(' – ')
            part1, part2 = splitted[0], ' – '.join(splitted[1:])
        elif ' - ' in title:
            splitted = title.split(' - ')
            part1, part2 = splitted[0], ' - '.join(splitted[1:])
        else:
            part1, part2 = title, title

        if any(i in part1 for i in author_names):
            title = part2
        else:
            title = part1

        try:
            p_list = soup.find('div', class_='entry').find_all('p')
        except AttributeError:
            p_list = soup.find('div', class_='post-excerpt').find_all('p')

    except Exception as e:
        print(f"{item_link}: {e}")
        return
    body = ''
    for p in p_list:
        body += f'\n{p.getText()}'

    return {
        'link': item_link,
        'title': title,
        'author': author,
        'text': clean_text(body),
    }


file = open('onlyart.csv', 'w')

writer = csv.DictWriter(file, fieldnames=['title', 'author', 'text', 'link'])
writer.writeheader()

authors = get_authors()
for author, link in authors.items():
    print(f"{link} processing.")
    items = get_author_links(link)
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = []
        for item in items:
            futures.append(executor.submit(parse_item, item_link=item, author=author))
        for future in concurrent.futures.as_completed(futures):
            parsed = future.result()
            if parsed:
                writer.writerow(parsed)

    print(f"{link} processed. Items: {len(items)}")

file.close()
