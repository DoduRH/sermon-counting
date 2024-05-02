from dataclasses import dataclass
from datetime import datetime, timedelta
from sermonCounting.passage import Passage

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

        for tag in self.tags:
            out[tag] = True
        return out

    def toCsv(self):
        return f'{self.page}|{self.title}|{self.speaker}|{self.date}|{self.book}|{self.passages.chapter_start}|{self.passages.chapter_end}|{self.passages.verse_start}|{self.passages.verse_end}|{self.tags}|{self.series}'
