# %%
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from urllib import request

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import esv_ranges
import plotly as px

# %%
OUTPUT_FILE = "sermons.csv"

@dataclass
class Passage:
    book: str
    chapter_start: int
    chapter_end: int
    verse_start: int
    verse_end: int
    
    def __init__(self):
        return None
    
    def __repr__(self):
        output = self.book
        output += f" {self.chapter_start}:{self.verse_start}-"
        if self.chapter_end != self.chapter_start:
            output += f"{self.chapter_end}:"
        output += str(self.verse_end)
        return output
    
    def __hash__(self):
        return hash(str(self))
    
    def __setattr__(self, name: str, value: request.Any) -> None:
        if name == 'book':
            if value == 'eph':
                value = 'ephesians'
            if value == 'phil':
                value = 'philippians'
            value: str = value.title()
        object.__setattr__(self, name, value)

    def xInY(_, x: Passage, y: Passage):
        return x.chapter_start in range(y.chapter_start, y.chapter_end+1) and x.verse_start in range(y.verse_start, y.verse_end+1)


    def sameChapter(self, other: Passage):
        return self.chapter_start == other.chapter_start and \
            self.chapter_end == other.chapter_end and \
            self.verse_start == other.verse_start and \
            self.verse_end == other.verse_end 

    def __contains__(self, other):
        # Other in self
        if type(other) != Passage:
            return False
        if self.book != other.book:
            return False
        if self.chapter_start == self.chapter_end and self.verse_start == self.verse_end:
            return False
        if other.chapter_start == other.chapter_end and other.verse_start == other.verse_end:
            return self.xInY(other, self)
        return False


@dataclass
class Sermon:
    page: str
    title: str
    speaker: str
    date: datetime
    passages: 'set[Passage]'
    tags: 'list[str]'
    series: str
    audio_url: str
    description: str
    
    def __init__(self):
        self.passages = set()
        return None

    def __hash__(self):
        return hash(f"{self.page}")

    def addPassage(self, newPassage: Passage):
        if newPassage.chapter_start == newPassage.chapter_end and newPassage.verse_start > newPassage.verse_end:
            print(f"Backwards passage {newPassage}")
            return
        for passage in self.passages:
            # other in self
            if newPassage in passage:
                return
            if passage in newPassage:
                self.passages.add(newPassage)
                self.passages.remove(passage)
                return
        self.passages.add(newPassage)

    def to_dict(self):
        out = {
            'page': self.page,
            'title': self.title,
            'speaker': self.speaker,
            'date': self.date,
            'series': self.series,
            'audio_url': self.audio_url,
            'passage_count': len(self.passages),
        }

        for i, passage in enumerate(self.passages):
            out[f'book_{i}'] = passage.book
            out[f'chapter_start_{i}'] = passage.chapter_start
            out[f'chapter_end_{i}'] = passage.chapter_end
            out[f'verse_start_{i}'] = passage.verse_start
            out[f'verse_end_{i}'] = passage.verse_end

        for tag in tags:
            out[tag] = tag in self.tags
        return out

    def toCsv(self):
        return f'{self.page}|{self.title}|{self.speaker}|{self.date}|{self.book}|{self.passages.chapter_start}|{self.passages.chapter_end}|{self.passages.verse_start}|{self.passages.verse_end}|{self.tags}|{self.series}'

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
    output.title = soup.select_one('.exodus-main-title').text.strip().replace("–", "-")
    speakerElement = soup.select_one('.exodus-sermon-speaker')
    if speakerElement is not None:
        output.speaker = speakerElement.text.strip()
    else:
        output.speaker = ""
    output.date = np.datetime64(soup.find('time').attrs['datetime'])

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

    descriptionSelector = soup.select('.exodus-entry-content')
    allText = output.title.lower()
    if len(descriptionSelector) >= 1:
        output.description = descriptionSelector[0].text.replace("–", "-")
        allText += (" " + output.description).lower()
    for bibleBook in reversed(allBooks):
        split = allText.split(bibleBook)
        if len(split) >= 2:
            for sec in split[1:]:
                passage = Passage()
                passage.book = bibleBook
                search = BOOK_REGEX.search(sec.removeprefix(":").replace(" ", "").split("\xa0", 1)[0])
                if search is None and bibleBook in output.title:
                    search = TITLE_REGEX.search(output.title.replace(" ", ""))
                if search is not None:
                    match = search.groups()
                    if match[1] is None:
                        passage.chapter_start = int(match[0])
                        passage.chapter_end = int(match[0])
                        passage.verse_start = int(-1)
                        passage.verse_end = int(-1)
                    elif match[2] is None:
                        passage.chapter_start = int(match[0])
                        passage.chapter_end = int(match[0])
                        passage.verse_start = int(match[1])
                        passage.verse_end = int(match[1])
                    elif match[3] is None:
                        passage.chapter_start = int(match[0])
                        passage.chapter_end = int(match[0])
                        passage.verse_start = int(match[1])
                        passage.verse_end = int(match[2])
                    else:
                        passage.chapter_start = int(match[0])
                        passage.verse_start = int(match[1])
                        passage.chapter_end = int(match[2])
                        passage.verse_end = int(match[3])
                    # Skip if text 1 john is already in and book is john
                    if not any([bibleBook in x.book and x.sameChapter(passage) for x in output.passages]):
                        output.addPassage(passage)

    audio = soup.select('audio')
    if len(audio) >= 2:
        raise AssertionError("Multiple audio sources detected", output.title, output.page)
    
    if len(audio) == 1:
        audio = audio[0]
        if audio.source != None:
            audio = audio.source
        if audio['src'] != None:
            output.audio_url = audio['src']
    if not hasattr(output, 'audio_url'):
        output.audio_url = ''

    return output


def processMainPageByIdx(idx: int) -> 'set[Sermon]':
    page = getPageByIndex(idx)
    output = set()

    soup = BeautifulSoup(page, 'html.parser')
    section = soup.find('section')
    for article in section.find_all('article'):
        getPage(article.find('a').attrs['href'])
        output.add(processTalkPage(article.find('a').attrs['href']))
        pbar.update(1)

    return output

with open('all-books.txt') as f:
    allBooks = f.readlines()
for i, bookName in enumerate(allBooks):
    allBooks[i] = bookName.strip().lower()

BASE_URL = "https://emmanuelbristol.org.uk/talk-archive/page/"
CACHE = Path("cache")
CACHE.mkdir(exist_ok=True, parents=True)

BOOK_REGEX = re.compile(r'^(\d{1,}):?(\d{1,})?-?(\d{1,})?:?(\d{1,})?')
TITLE_REGEX = re.compile(r'(\d{1,}):?(\d{1,})?-?(\d{1,})?:?(\d{1,})?')

# %%
last_request = datetime.now()

start = 1
end = 141
with tqdm(total=(end - start + 1) * 10) as pbar:
    sermons: 'set[Sermon]' = set()
    for num in range(start, end+1): # 141 pages to do
        sermons.update(processMainPageByIdx(num))

tags = set()
missingTagCount = 0
for sermon in sermons:
    if len(sermon.tags) == 0:
        missingTagCount += 1
    else:
        tags.update(sermon.tags)

data = pd.DataFrame.from_records([s.to_dict() for s in sermons])
data

# %%
# save data
data.to_feather("data.feather")

# %%
# Load data
data = pd.read_feather("data.feather")


# %%
# Sermon Counts
print("Sermon Counts")
westburyMask = (data['Emmanuel Westbury'] | data['EW Students'] | data['Weekend Away'] | data['audio_url'].str.contains('westbury', case=False))
westbury = data[westburyMask]
print(f"Westbury: {westbury.shape[0]}")

bishopstonMask = (data['Emmanuel Bishopston'] | data['audio_url'].str.contains('ashleydown', case=False))
bishopston = data[bishopstonMask]
print(f"Bishopston: {bishopston.shape[0]}")

eccMask = (data['Emmanuel City Centre'] | data['ECC'] | data['audio_url'].str.contains('ecc', case=False))
ecc = data[eccMask]
print(f"ECC: {ecc.shape[0]}")

unassigned = data[~(westburyMask | bishopstonMask | eccMask)]
print(f"unassigned: {unassigned.shape[0]}")


# %%
# Find sermons from multiple churches
two = data[(westburyMask.astype(int) + bishopstonMask.astype(int) + eccMask.astype(int)) == 2]
three = data[(westburyMask.astype(int) + bishopstonMask.astype(int) + eccMask.astype(int)) == 3]

# %%
# Missing books
emptyBookMask = data['passage_count'] == 0
data[emptyBookMask]

# %%
# Missing Westbury Books
data[westburyMask & emptyBookMask]

# %%
a = processTalkPage('https://emmanuelbristol.org.uk/sermons/perfect-in-christ/')
a.passages

# %%
data['passage_count'].plot.hist(bins=data['passage_count'].max()+1)

# %%
# Find specific book
mask = pd.Series(False, index=data.index)

for i in range(0, 13):
    mask = mask | (data[f'book_{i}'] == 'Jeremiah')

data[mask & westburyMask].title


# %%
# Create visited dataframe

bible_data = {
    'Book': [],
    'Chapter': [],
    'Verse': [],
    'Visited': 0,
}

bookToIndex = {}
indexToBook = {}

for i, (bookName, chapterCount, verseCounts) in enumerate(esv_ranges.passage_data[1:]):
    bookToIndex[bookName.title()] = i
    indexToBook[i] = bookName.title()
    # Remove None padding
    verseCounts = verseCounts[1:]
    for chapterNum, chapterVerseCount in enumerate(verseCounts, start=1):
        bible_data['Book'].extend([i] * chapterVerseCount)
        bible_data['Chapter'].extend([chapterNum] * chapterVerseCount)
        bible_data['Verse'].extend(range(1, chapterVerseCount + 1))

visited = pd.DataFrame(bible_data)

visited.set_index(['Book', 'Chapter', 'Verse'], inplace=True)
visited = visited.T
visited

# %%
# Create visited Series

bible_data = {
}

bookToIndex = {}
indexToBook = {}

for i, (bookName, chapterCount, verseCounts) in enumerate(esv_ranges.passage_data[1:]):
    bookToIndex[bookName.title()] = i
    indexToBook[i] = bookName.title()
    # Remove None padding
    verseCounts = verseCounts[1:]
    for chapterNum, chapterVerseCount in enumerate(verseCounts, start=1):
        for verse in range(1, chapterVerseCount + 1):
            bible_data[(i, chapterNum, verse)] = 0
        # bible_data['Book'].extend([i] * chapterVerseCount)
        # bible_data['Chapter'].extend([chapterNum] * chapterVerseCount)
        # bible_data['Verse'].extend(range(1, chapterVerseCount + 1))

visited = pd.Series(bible_data)

visited

# %%
# Mark books we have been to
for i, sermonData in tqdm(data.iterrows(), total=data.shape[0]):
    for i in range(sermonData['passage_count']):
        sliceStart = (bookToIndex[sermonData[f'book_{i}']], sermonData[f'chapter_start_{i}'], sermonData[f'verse_start_{i}'])
        sliceEnd = (bookToIndex[sermonData[f'book_{i}']], sermonData[f'chapter_end_{i}'], sermonData[f'verse_end_{i}'])
        visited[sliceStart:sliceEnd] += 1

visited.sum()

# %%
# 
v = visited.T.copy()
v.index = [f'{indexToBook[x[0]]} {x[1]}:{x[2]}' for x in v.index.to_flat_index()]
v

pd.set_option('plotting.backend', 'plotly')
fig = v.plot.line()
fig.write_html('output.html')
fig
