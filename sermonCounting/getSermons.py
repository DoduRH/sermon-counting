from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from urllib import request

import numpy as np
from bs4 import BeautifulSoup

from book import Book
from sermonCounting.sermon import Sermon
from sermonCounting.passage import Passage

BASE_URL = "https://emmanuelbristol.org.uk/talk-archive/page/"

BOOK_REGEX = re.compile(r'^(\d{1,}):?(\d{1,})?-?(\d{1,})?:?(\d{1,})?')
TITLE_REGEX = re.compile(r'(\d{1,}):?(\d{1,})?-?(\d{1,})?:?(\d{1,})?')
REMOVE_PUNCTUATION = re.compile(r'[^A-Za-z ]+')

CACHE = Path("cache")
CACHE.mkdir(exist_ok=True, parents=True)

last_request = datetime.now()

def getPage(page: str):
    page_cache = CACHE.joinpath(request.url2pathname(page.replace('https://', "").replace("?", "QUESTION_MARK"))).with_suffix(".html")
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

def processTalkPage(pageUrl: str) -> Sermon:
    output = Sermon()
    pageData = getPage(pageUrl.removesuffix("/") + "?player=audio")
    soup = BeautifulSoup(pageData, 'html.parser')

    output.page = pageUrl
    output.title = soup.select_one('.exodus-main-title').text.strip().replace("–", "-")
    speakerElement = soup.select_one('.exodus-sermon-speaker')
    if speakerElement is not None:
        # TODO: There might be 2 speakers
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
        allText += " " + output.description.title().split("Footnotes")[0]
    for bibleBookGroup in reversed(Book):
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
                        if not any([x.book.isSubName(bibleBookGroup) and x.sameVerseAndChapterNumbers(passage) for x in output.passages]):
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

    return output