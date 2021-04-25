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


def get_links():
    r = session.get('https://www.wordproject.org/bibles/uk/index.htm', timeout=60)
    soup = BeautifulSoup(r.text.encode('l1').decode(), "html.parser")
    links = soup.select_one('#main > div > div > div > div.ym-grid.linearize-level-2').find_all('a')

    result = dict()
    for link in links:
        text = link.getText().strip()
        href = link.get('href')
        if re.search(r'\d+\/\d+\.htm', href):
            result[text] = f"https://www.wordproject.org/bibles/uk/{href}"
    return result


def get_sections(link: str):
    r = session.get(link, timeout=60)
    soup = BeautifulSoup(r.text.encode('l1').decode(), "html.parser")
    if soup.find('div', class_='textHeader').find_all('a'):
        max_page = soup.find('div', class_='textHeader').find_all('a')[-1].getText()
    else:
        max_page = 1
    result = list()
    for page in range(1, int(max_page)+1):
        p_link = re.sub(r'(\d+)(?:\.htm.*)', f'{page}.htm', link)
        result.append(f"{p_link}")

    return result


def clean_text(text: str):
    return text


def parse_item(section_link: str):
    r = None
    max_attempts = 3
    attempts = 0
    print('section link', section_link)
    while attempts <= max_attempts:
        try:
            r = session.get(section_link, timeout=20)
            break
        except Exception as e:
            print(f"{section_link}: {e}, {attempts}")

    if not r:
        return

    soup = BeautifulSoup(r.text.encode('l1').decode(), "html.parser")
    try:
        title = soup.find('h1').getText().strip()
        section = soup.find('span', class_='chapread').getText()
        body = soup.select_one('#textBody > p')
        for match in body.findAll('span'):
            match.replace_with('')
        body = body.getText()


    except Exception as e:
        print(f"{section_link}: {e}")
        return

    return {
        'link': section_link,
        'title': title,
        'section': section,
        'text': clean_text(body),
    }


file = open('wordproject.csv', 'w')

writer = csv.DictWriter(file, fieldnames=['title', 'section', 'text', 'link'])
writer.writeheader()

links = get_links()
for name, link in links.items():
    print(f"{link} processing.")
    sections = get_sections(link)
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = []
        for section in sections:
            futures.append(executor.submit(parse_item, section_link=section))
        for future in concurrent.futures.as_completed(futures):
            parsed = future.result()
            if parsed:
                writer.writerow(parsed)

    print(f"{link} processed. Sections: {len(sections)}")

file.close()
