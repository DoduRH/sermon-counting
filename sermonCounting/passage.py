from __future__ import annotations

from dataclasses import dataclass

from book import Book


@dataclass
class Passage:
    book: Book
    chapter_start: int
    chapter_end: int
    verse_start: int
    verse_end: int
    
    def __init__(self, book: Book=None, c_start: int=None, v_start: int=None, c_end: int=None, v_end: int=None):
        self.book = book
        self.chapter_start = c_start
        self.chapter_end = c_end
        self.verse_start = v_start
        self.verse_end = v_end
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

    def __eq__(self, other):
        if isinstance(other, Passage):
            return (
                (self.book == other.book) and 
                (self.chapter_start == other.chapter_start) and 
                (self.chapter_end == other.chapter_end) and 
                (self.verse_start == other.verse_start) and 
                (self.verse_end == other.verse_end))
        else:
            return False

    def xInY(_, x: Passage, y: Passage):
        if x.verse_start == x.verse_end == -1:
            return x.chapter_start in range(y.chapter_start, y.chapter_end+1)
        return x.chapter_start in range(y.chapter_start, y.chapter_end+1) and x.verse_start in range(y.verse_start, y.verse_end+1)


    def sameVerseAndChapterNumbers(self, other: Passage):
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
