import unittest
from book import Book
from sermonCounting.getSermons import processTalkPage
from sermonCounting.passage import Passage

class TestTrickyPassageCollection(unittest.TestCase):
    def test_intimacy_with_another(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/intimacy-with-another/')
        expected = {Passage(Book.SONG_OF_SONGS, 7, 1, 8, 7)}
        self.assertSetEqual(res.passages, expected)

    def test_revelation_the_final_word(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/revelation-the-final-word-86-921/')
        expected = {Passage(Book.REVELATION, 8, 6, 9, 21)}
        self.assertSetEqual(res.passages, expected)

    def test_the_answer_to_death_psalm_139(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/the-answer-to-death-psalm-139/')
        expected = {Passage(Book.PSALM, 139, 1, 139, 24)}
        self.assertSetEqual(res.passages, expected)

    def test_finding_joy_in_christmas(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/finding-joy-in-christmas-1-john-11-4/')
        expected = {Passage(Book.JOHN1, 1, 1, 1, 4)}
        self.assertSetEqual(res.passages, expected)
        
    def test_worth_equal_and_different(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/worthy-equal-and-different-various/')
        expected = {
            Passage(Book.GENESIS, 1, 28, 1, 28),
            Passage(Book.GENESIS, 2, 15, 2, 15),
            Passage(Book.NUMBERS, 3, 5, 3, 8),
            Passage(Book.MATTHEW, 28, 16, 28, 20),
            Passage(Book.PETER1, 5, 1, 5, 2),
            Passage(Book.TIMOTHY1, 3, 1, 3, 2),
            Passage(Book.LUKE, 1, 26, 1, 31),
            Passage(Book.LUKE, 8, 1, 8, 3),
            Passage(Book.LUKE, 10, 38, 10, 42),
            Passage(Book.LUKE, 24, 9, 24, 11),
            Passage(Book.ACTS, 16, 12, 16, 15),
            Passage(Book.ACTS, 18, 24, 18, 28),
            Passage(Book.ROMANS, 16, 1, 16, 16),
        }
        self.assertSetEqual(res.passages, expected)

    def test_hebrews8_1_13(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/interview-mike-cain/')
        expected = set()
        self.assertSetEqual(res.passages, expected)
        
    
    def test_worthy_equal_and_difference_footnotes(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/worthy-equal-and-different-matthew-15-1-9/')
        expected = {Passage(Book.MATTHEW, 15, 1, 15, 9)}
        self.assertSetEqual(res.passages, expected)

class TestStandardPassageCollection(unittest.TestCase):
    def template(self):
        res = processTalkPage('')
        expected = {Passage(Book.GENESIS, 11, 11, 11, 11)}
        self.assertSetEqual(res.passages, expected)    
    
    def test_god_is_mighty_to_save(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/god-is-mighty-to-save-praise-him/')
        expected = {Passage(Book.JONAH, 1, 17, 2, 10)}
        self.assertSetEqual(res.passages, expected)

    def test_we_are_in_christ(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/we-are-in-christ/')
        expected = {Passage(Book.EPHESIANS, 1, 3, 1, 14)}
        self.assertSetEqual(res.passages, expected)
        
    def test_the_word_made_flesh(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/the-word-made-flesh-john-1/')
        expected = {Passage(Book.JOHN, 1, 1, 1, 18)}
        self.assertSetEqual(res.passages, expected)

    def test_the_king_will_judge(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/the-king-will-judge/')
        expected = {Passage(Book.THESSALONIANS2, 1, 1, 1, 13)}
        self.assertSetEqual(res.passages, expected)
        
    def test_we_believe_and_therefore_speak(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/we-believe-and-therefore-speak/')
        expected = {Passage(Book.CORINTHIANS2, 4, 13, 4, 15)}
        self.assertSetEqual(res.passages, expected)

    def test_real_faith_works(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/real-faith-works-suffering-sunshine-sickness-and-sin-james-513-20/')
        expected = {Passage(Book.JAMES, 5, 13, 5, 20)}
        self.assertSetEqual(res.passages, expected)
        
    def test_moaning_about_the_mediator(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/moaning-about-the-mediator/')
        expected = {Passage(Book.NUMBERS, 16, 1, 18, 7)}
        self.assertSetEqual(res.passages, expected)
        
    def test_life_in_christ(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/life-in-christ/')
        expected = {Passage(Book.GALATIANS, 3, 1, 3, 14)}
        self.assertSetEqual(res.passages, expected)
        
    def test_transgressions_removed_sins_forever(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/isaiah-4222-445-transgressions-removed-sins-forgotten/')
        expected = {Passage(Book.ISAIAH, 42, 22, 44, 5)}
        self.assertSetEqual(res.passages, expected)
        
    def test_god_loves_the_unlovely(self):
        res = processTalkPage('https://emmanuelbristol.org.uk/sermons/god-loves-the-unlovely-1-john-410/')
        expected = {Passage(Book.JOHN1, 4, 10, 4, 10)}
        self.assertSetEqual(res.passages, expected)