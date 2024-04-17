from datetime import date
from pathlib import Path
from urllib import request
from bs4 import BeautifulSoup


class Sermon:
    page: str
    speaker: str
    date: date
    book: str
    chapter: int
    verse_start: int
    verse_end: int
    tags: 'list[str]'
    series: str

BASE_URL = "https://emmanuelbristol.org.uk/talk-archive/page/"
CACHE = Path("cache")
CACHE.mkdir(exist_ok=True, parents=True)

def getPage(page: str):
    page_cache = CACHE.joinpath(request.url2pathname(page.replace(BASE_URL, ""))).with_suffix(".html")
    if page_cache.exists():
        with open(page_cache, encoding="utf-8") as f:
            return f.read()
    
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
    return None


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
    processTalkPage("https://emmanuelbristol.org.uk/sermons/john-1016-one-world-alliance/")