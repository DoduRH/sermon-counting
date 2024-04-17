from datetime import datetime
from pathlib import Path
from urllib import request
from bs4 import BeautifulSoup
import re


class Sermon:
    page: str
    title: str
    speaker: str
    date: datetime
    book: str
    chapter_start: int
    chapter_end: int
    verse_start: int
    verse_end: int
    tags: 'list[str]'
    series: str

BASE_URL = "https://emmanuelbristol.org.uk/talk-archive/page/"
CACHE = Path("cache")
CACHE.mkdir(exist_ok=True, parents=True)

BOOK_REGEX = re.compile(r'(\d{1,}):(\d{1,})-?(\d{1,})?:?(\d{1,})?')

def getPage(page: str):
    page_cache = CACHE.joinpath(request.url2pathname(page.replace('https://', ""))).with_suffix(".html")
    if page_cache.exists():
        with open(page_cache, encoding="utf-8") as f:
            return f.read()
    page_cache.parent.mkdir(exist_ok=True, parents=True)
    response = request.urlopen(page)
    if response.code == 404:
        raise FileNotFoundError()
    string: str = response.read().decode()
    with open(page_cache, "w+", encoding="utf-8") as f:
        f.write(string)
    return string

def getPageByIndex(idx: int):
    return getPage(f"{BASE_URL}{idx}")


def processTalkPage(pageUrl: str) -> Sermon:
    output = Sermon()
    pageData = getPage(pageUrl)
    soup = BeautifulSoup(pageData, 'html.parser')

    output.page = pageUrl
    output.title = soup.select_one('.exodus-main-title').text.strip()
    output.speaker = soup.select_one('.exodus-sermon-speaker').text.strip()
    output.date = datetime.fromisoformat(soup.find('time').attrs['datetime'])
    output.book = soup.select_one('.exodus-sermon-book').text.strip()

    # Process end tags
    for props in soup.select('.exodus-content-icon'):
        if "Series" in props.text:
            output.series = props.a.text
        elif "Tagged with" in props.text:
            output.tags = [anchor.text for anchor in props.find_all('a')]

    if output.book in output.title:
        match = BOOK_REGEX.findall(output.title)

        if len(match) == 2:
            output.chapter_start = match[0]
            output.verse_start = match[1]
        elif len(match) == 3:
            output.chapter_start = match[0]
            output.verse_start = match[1]
            output.verse_end = match[2]
        elif len(match) == 4:
            output.chapter_start = match[0]
            output.verse_start = match[1]
            output.chapter_end = match[2]
            output.verse_end = match[3]

    else:
        print(f"{output.title} does not contain {output.book}")

    return output


def processMainPage(page: str) -> 'set[Sermon]':
    output = set()

    soup = BeautifulSoup(page, 'html.parser')
    section = soup.find('section')
    for article in section.find_all('article'):
        output.add(processTalkPage(article.find('a').attrs['href']))

    return output

def main():
    for num in range(1, 2): # 141 pages to do
        getPageByIndex(num)

if __name__ == "__main__":
    # main()
    # processMainPage(getPageByIndex(1))
    print(processTalkPage("https://emmanuelbristol.org.uk/sermons/isaiah-5213-536-punished-in-our-place/"))