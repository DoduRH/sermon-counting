import unittest
from book import Book
from sermonCounting.getSermons import processTalkPage
from sermonCounting.passage import Passage

class TestPassageCollection(unittest.TestCase):

    def test_intimacy_with_another(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/intimacy-with-another/')
        expected = {Passage(Book.SONG_OF_SONGS, 7, 1, 8, 7)}
        self.assertSequenceEqual(res.passages, expected)

    def test_revelation_the_final_word(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/revelation-the-final-word-86-921/')
        expected = {Passage(Book.REVELATION, 8, 6, 9, 21)}
        self.assertSequenceEqual(res.passages, expected)

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)