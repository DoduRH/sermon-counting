# %%
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from urllib import request
from bs4 import BeautifulSoup
import re
from time import sleep
from tqdm import tqdm
from dataclasses import dataclass

# %%
OUTPUT_FILE = "sermons.csv"

@dataclass
class Verses:
    chapter_start: int
    chapter_end: int
    verse_start: int
    verse_end: int
    
    def __init__(self):
        return None
    
    def __repr__(self):
        return f"{self.chapter_start}:{self.verse_start}-{self.chapter_end + ':' if self.chapter_end == self.chapter_start else ''}{self.verse_end}"
    

@dataclass
class Sermon:
    page: str
    title: str
    speaker: str
    date: datetime
    book: str
    verses: Verses
    tags: 'list[str]'
    series: str

    def __init__(self):
        self.verses = Verses()
        return None
    
    def __hash__(self):
        return hash(f"{self.page}")

    def to_dict(self):
        out = {
            'page': self.page,
            'title': self.title,
            'speaker': self.speaker,
            'date': self.date,
            'book': self.book,
            'chapter_start': self.verses.chapter_start,
            'chapter_end': self.verses.chapter_end,
            'verse_start': self.verses.verse_start,
            'verse_end': self.verses.verse_end,
            'series': self.series,
        }

        for tag in tags:
            out[tag] = tag in self.tags
        return out

    def toCsv(self):
        return f'{self.page}|{self.title}|{self.speaker}|{self.date}|{self.book}|{self.verses.chapter_start}|{self.verses.chapter_end}|{self.verses.verse_start}|{self.verses.verse_end}|{self.tags}|{self.series}'

def getPage(page: str):
    page_cache = CACHE.joinpath(request.url2pathname(page.replace('https://', ""))).with_suffix(".html")
    if page_cache.exists():
        with open(page_cache, encoding="utf-8") as f:
            return f.read()
    page_cache.parent.mkdir(exist_ok=True, parents=True)
    # Rate limiting
    while last_request + timedelta(seconds=1) > datetime.now():
        sleep(1)

    response = request.urlopen(page)
    if response.code != 200:
        print(f"Error found when loading {page}")
        raise FileNotFoundError()
    string: str = response.read().decode()
    with open(page_cache, "w+", encoding="utf-8") as f:
        f.write(string)
    return string

def getPageByIndex(idx: int):
    return getPage(f"{BASE_URL}{idx}")

def saveSermon(sermon: Sermon):
    with open(OUTPUT_FILE, "a+", encoding="utf-8") as f:
        f.write(sermon.toCsv())
        f.write("\n")

def processTalkPage(pageUrl: str) -> Sermon:
    output = Sermon()
    pageData = getPage(pageUrl)
    soup = BeautifulSoup(pageData, 'html.parser')

    output.page = pageUrl
    output.title = soup.select_one('.exodus-main-title').text.strip()
    speakerElement = soup.select_one('.exodus-sermon-speaker')
    if speakerElement is not None:
        output.speaker = speakerElement.text.strip()
    else:
        output.speaker = ""
    output.date = datetime.fromisoformat(soup.find('time').attrs['datetime'])
    bookElement = soup.select_one('.exodus-sermon-book')
    if bookElement is not None:
        output.book = bookElement.text.strip()
    else:
        output.book = ''

    # Process end tags
    for props in soup.select('.exodus-content-icon'):
        if "Series" in props.text:
            output.series = props.a.text
        elif "Tagged with" in props.text:
            output.tags = [anchor.text for anchor in props.find_all('a')]

    if not hasattr(output, 'tags'):
        output.tags = []
    if not hasattr(output, 'series'):
        output.series = ''

    search = BOOK_REGEX.search(output.title.replace(" ", ""))
    search = None
    if search is not None:
        match = search.groups()
        if match[1] is None:
            output.verses.chapter_start = match[0]
            output.verses.chapter_end = match[0]
            output.verses.verse_start = -1
            output.verses.verse_end = -1
        if match[2] is None:
            output.verses.chapter_start = match[0]
            output.verses.chapter_end = match[0]
            output.verses.verse_start = match[1]
            output.verses.verse_end = match[1]
        elif match[3] is None:
            output.verses.chapter_start = match[0]
            output.verses.chapter_end = match[0]
            output.verses.verse_start = match[1]
            output.verses.verse_end = match[2]
        else:
            output.verses.chapter_start = match[0]
            output.verses.verse_start = match[1]
            output.verses.chapter_end = match[2]
            output.verses.verse_end = match[3]
    else:
        output.verses.chapter_start = -1
        output.verses.chapter_end = -1
        output.verses.verse_start = -1
        output.verses.verse_end = -1

    return output


def processMainPageByIdx(idx: int) -> 'set[Sermon]':
    page = getPageByIndex(idx)
    output = set()

    soup = BeautifulSoup(page, 'html.parser')
    section = soup.find('section')
    for article in section.find_all('article'):
        getPage(article.find('a').attrs['href'])
        try:
            output.add(processTalkPage(article.find('a').attrs['href']))
        except Exception as e:
            print(f"Error on {article.find('a').attrs['href']} {e}")
        pbar.update(1)

    return output

with open('all-books.txt') as f:
    allBooks = f.readlines()

BASE_URL = "https://emmanuelbristol.org.uk/talk-archive/page/"
CACHE = Path("cache")
CACHE.mkdir(exist_ok=True, parents=True)

BOOK_REGEX = re.compile(r'(\d{1,}):?(\d{1,})?-?(\d{1,})?:?(\d{1,})?')

last_request = datetime.now()

start = 1
end = 141
with tqdm(total=(end - start + 1) * 10) as pbar:
    sermons: 'set[Sermon]' = set()
    for num in range(start, end+1): # 141 pages to do
        sermons.update(processMainPageByIdx(num))

# %%
tags = set()
missingTagCount = 0
for sermon in sermons:
    if len(sermon.tags) == 0:
        missingTagCount += 1
    else:
        tags.update(sermon.tags)
print(missingTagCount)
print(tags)

# %%
data = pd.DataFrame.from_records([s.to_dict() for s in sermons])
data
# %%
westbury = data[(data['Emmanuel Westbury'] | data['EW Students'] | data['Weekend Away'])]
bishopston = data[(data['Emmanuel Bishopston'])]
center = data[(data['Emmanuel City Centre'] | data['ECC'])]

print("Sermon Counts")
print(f"Westbury: {westbury.shape[0]}")
print(f"Bishopston: {bishopston.shape[0]}")
print(f"ECC: {center.shape[0]}")
