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
import plotly.express as px

from importlib import reload

reload(esv_ranges)
import book as BookEnum
reload(BookEnum)
from book import Book

# %%
OUTPUT_FILE = "sermons.csv"

@dataclass
class Passage:
    book: Book
    chapter_start: int
    chapter_end: int
    verse_start: int
    verse_end: int
    
    def __init__(self):
        return None
    
    def __repr__(self):
        output = self.book.getName()
        output += f" {self.chapter_start}:{self.verse_start}-"
        if self.chapter_end != self.chapter_start:
            output += f"{self.chapter_end}:"
        output += str(self.verse_end)
        return output
    
    def __hash__(self):
        return hash(str(self))

    def xInY(_, x: Passage, y: Passage):
        if x.verse_start == x.verse_end == -1:
            return x.chapter_start in range(y.chapter_start, y.chapter_end+1)
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
    
    def __init__(self, data=None):
        self.passages = set()
        if data is None:
            return None
        
        self.page = data.page
        self.title = data.title
        self.speaker = data.speaker
        self.date = data.date
        self.tags = []
        self.series = data.series
        self.audio_url = data.audio_url
        self.description = None
        
        for i in range(data.passage_count):
            passage = Passage()
            passage.book = data[f'book_{i}']
            passage.chapter_start = data[f'chapter_start_{i}']
            passage.chapter_end = data[f'chapter_end_{i}']
            passage.verse_start = data[f'verse_start_{i}']
            passage.verse_end = data[f'verse_end_{i}']
            self.passages.add(passage)
        
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
    allText = output.title.title()
    if len(descriptionSelector) >= 1:
        output.description = descriptionSelector[0].text.replace("–", "-")
        allText += " " + output.description.title()
    for bibleBookGroup in Book:
        for bibleBook in bibleBookGroup.value:
            split = allText.split(bibleBook)
            if len(split) >= 2:
                for sec in split[1:]:
                    passage = Passage()
                    passage.book = bibleBookGroup
                    search = BOOK_REGEX.search(sec.removeprefix(":").replace(" ", "").split("\xa0", 1)[0])
                    if search is None and bibleBook in REMOVE_PUNCTUATION.sub('', output.title).title().split(" "):
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

BASE_URL = "https://emmanuelbristol.org.uk/talk-archive/page/"
CACHE = Path("cache")
CACHE.mkdir(exist_ok=True, parents=True)

BOOK_REGEX = re.compile(r'^(\d{1,}):?(\d{1,})?-?(\d{1,})?:?(\d{1,})?')
TITLE_REGEX = re.compile(r'(\d{1,}):?(\d{1,})?-?(\d{1,})?:?(\d{1,})?')
REMOVE_PUNCTUATION = re.compile(r'[^A-Za-z ]+')

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
a = processTalkPage('https://emmanuelbristol.org.uk/sermons/revelation-the-final-word-86-921/')
a.passages

# %%
data['passage_count'].plot.hist(bins=data['passage_count'].max()+1)

# %%
# Find specific book
mask = pd.Series(False, index=data.index)

for i in range(data['passage_count'].max()):
    mask = mask | (data[f'book_{i}'].isin(Book.EZEKIEL.value))

data[mask & westburyMask].title

# %%
# Find unvisited books
print("Unvisited books")
d = data[westburyMask]
for book in Book:
    # Skip abreviated books
    mask = pd.Series(False, index=d.index)

    for i in range(d['passage_count'].max()):
        mask = mask | (d[f'book_{i}'] == book.getName().title())
    if mask.sum() == 0:
        print(book.value[0].title())


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
    bookToIndex[bookName] = i
    indexToBook[i] = bookName
    # Remove None padding
    verseCounts = verseCounts[1:]
    for chapterNum, chapterVerseCount in enumerate(verseCounts, start=1):
        bible_data['Book'].extend([i] * chapterVerseCount)
        bible_data['Chapter'].extend([chapterNum] * chapterVerseCount)
        bible_data['Verse'].extend(range(1, chapterVerseCount + 1))

visited = pd.DataFrame(bible_data)

visited.set_index(['Book', 'Chapter', 'Verse'], inplace=True)
visited = visited.T

# %%
# Create visited Series

bible_data = {
}

bookToIndex = {}
indexToBook = {}

chapVerse = {}

for i, (bookName, chapterCount, verseCounts) in enumerate(esv_ranges.passage_data[1:]):
    bookToIndex[bookName.name] = i
    indexToBook[i] = bookName
    # Remove None padding
    verseCounts = verseCounts[1:]
    chapVerse[bookName.name] = {}
    for chapterNum, chapterVerseCount in enumerate(verseCounts, start=1):
        chapVerse[bookName.name][chapterNum] = chapterVerseCount
        for verse in range(1, chapterVerseCount + 1):
            bible_data[(i, chapterNum, verse)] = 0

visited = pd.Series(bible_data)

# %%
# Mark books we have been to
for d, church in [[data, 'all'], [data[eccMask], 'ECC'], [data[westburyMask], 'EW'], [data[bishopstonMask], 'EB']]:
    church = 'all'
    visited = pd.Series(0, index=visited.index)
    for i, sermonData in tqdm(d.iterrows(), total=d.shape[0]):
        for i in range(sermonData['passage_count']):
            sliceStart = (
                bookToIndex[sermonData[f'book_{i}'].name],
                sermonData[f'chapter_start_{i}'],
                max(sermonData[f'verse_start_{i}'], 0),
            )
            sliceEnd = (
                bookToIndex[sermonData[f'book_{i}'].name],
                sermonData[f'chapter_end_{i}'],
                max(sermonData[f'verse_end_{i}'], chapVerse[sermonData[f'book_{i}'].name][sermonData[f'chapter_end_{i}']]),
            )
            visited[sliceStart:sliceEnd] += 1

    visited.sum()

    v = visited.T.copy()
    v.index = [f'{indexToBook[x[0]]} {x[1]}:{x[2]}' for x in v.index.to_flat_index()]
    v

    pd.set_option('plotting.backend', 'plotly')
    fig = v.plot.line()
    fig.write_html(f'output/{church}.html')
    fig

# %%
# Create with slider
visited = pd.DataFrame(0, index=visited.index, columns=range(2007, datetime.now().year+1))
for year in visited.columns:
    filtered = data[data['date'] < datetime(year, 1, 1)]
    for i, sermonData in tqdm(filtered.iterrows(), total=filtered.shape[0], desc=f'{year}'):
        for i in range(sermonData['passage_count']):
            sliceStart = (
                bookToIndex[sermonData[f'book_{i}'].name], 
                sermonData[f'chapter_start_{i}'], 
                sermonData[f'verse_start_{i}'],
            )
            sliceEnd = (
                bookToIndex[sermonData[f'book_{i}'].name], 
                sermonData[f'chapter_end_{i}'], 
                sermonData[f'verse_end_{i}'],
            )
            visited.loc[sliceStart:sliceEnd,year] += 1

v = visited.copy()
v.index = [f'{indexToBook[x[0]].getName()} {x[1]}:{x[2]}' for x in v.index.to_flat_index()]

# %%
# Chat GPT
import plotly.graph_objects as go
fig = go.Figure()

for year in v.columns:
    year_data = v.loc[:,v.columns == year]
    fig.add_trace(go.Scatter(
        x=year_data.index,
        y=year_data.squeeze(),
        mode='lines',
        name=str(year),
        visible=(year==v.columns.max())
    ))

# Add slider
steps = []
for i, year in enumerate(v.columns):
    step = dict(
        method="update",
        args=[{"visible": [False] * len(v.columns)}],
        label=str(year),
    )
    step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
    steps.append(step)

sliders = [dict(
    active=len(v.columns) - 1,
    steps=steps,
    y=0
)]

fig.update_layout(sliders=sliders, title="Animated Line Plot",
                  xaxis_title="Index", yaxis_title="Value",
                  yaxis_range=[0, v.max().max()],
                  height=550,  # Adjust top and bottom margins
)

# Show the plot
fig.show()
fig.write_html('output/all_animated.html')


# %%
