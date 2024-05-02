import unittest
from book import Book
from sermonCounting.getSermons import processTalkPage
from sermonCounting.passage import Passage

class TestTrickyPassageCollection(unittest.TestCase):

    def test_intimacy_with_another(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/intimacy-with-another/')
        expected = {Passage(Book.SONG_OF_SONGS, 7, 1, 8, 7)}
        self.assertSequenceEqual(res.passages, expected)

    def test_revelation_the_final_word(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/revelation-the-final-word-86-921/')
        expected = {Passage(Book.REVELATION, 8, 6, 9, 21)}
        self.assertSequenceEqual(res.passages, expected)

    def test_the_answer_to_death_psalm_139(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/the-answer-to-death-psalm-139/')
        expected = {Passage(Book.PSALM, 139, 1, 139, 24)}
        self.assertSequenceEqual(res.passages, expected)
