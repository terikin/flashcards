# flashcards.py
#
# module providing a backend for kids flashcards to practice math, etc.
#

from enum import Enum
import secrets
import time


class ResponseMetadata:
    """For a given attempt to answer a problem, store the given answer and how long it took"""
    def __init__(self, correct, answer, time):
        self.correct = correct
        self.answer = answer
        self.time = time

    def __repr__(self):
        return f'{self.answer} ({"correct" if self.correct else "incorrect"}): {self.time:.1f} seconds'


class Card:
    """Base class for individual flashcards

    Track attributes, to include:
        - Text of the "problem"
        - Type of answer (text input box, multiple choice, etc.)
        - Answer validation function
        - For each attempt, track what answer was given and how long it took
    """
    class AnswerType(Enum):
        NULL = 0
        TEXT = 1

    def __init__(self, problem, answer_type):
        self.problem = problem
        self.answer_type = answer_type
        self.responses = []

    def __repr__(self):
        return self.problem

    def __str__(self):
        best_time = 10000
        num_correct = sum([1 if r.correct else 0 for r in self.responses])
        for r in self.responses:
            if r.correct and r.time < best_time:
                best_time = r.time
        if (len(self.responses) == 1) and r.correct:
            return f"{self.__repr__()}    (Best time = {best_time:.1f} s)"
        else:
            return f"{self.__repr__()}    ({num_correct} correct out of {len(self.responses)} attempts; best time = {best_time:.1f} s)"

    def __lt__(self, other):
        if len(self.responses) < len(other.responses):
            return True
        else:
            return sum([r.time for r in self.responses]) < sum([r.time for r in other.responses])

    def get_problem(self):
        return self.problem, self.answer_type

    def log_response(self, given_answer, time):
        correct = self._check_answer(given_answer)
        self.responses.append(ResponseMetadata(correct, given_answer, time))
        return correct

    def _check_answer(self, given_answer):
        """Return true if the provided answer is correct, otherwise return false"""
        raise

    def is_mastered(self, time_threshold):
        num_correct = [r.correct for r in self.responses].count(True)
        num_incorrect = len(self.responses) - num_correct
        if len(self.responses) > 0 and num_correct > num_incorrect:
            tr = self.responses[-1]
            if tr.correct and tr.time < time_threshold:
                return True, tr.time
        return False, 0

    def time(self):
        return sum([r.time for r in self.responses])



class Arithmetic(Card):
    """Card for basic math where the answer is a number that is typed"""
    def __init__(self, problem, answer):
        self.answer = answer
        Card.__init__(self, problem, Card.AnswerType.TEXT)

    def __repr__(self):
        return f"{self.problem}{self.answer}"

    def _check_answer(self, given_answer):
        try:
            return self.answer == int(given_answer)
        except:
            return False


class Deck:
    """Container for a group of flashcards

    Each deck tracks the 'cards' along with information about each response
    """
    def __init__(self, cards, time_threshold=5):
        self.cards = cards
        self.time_threshold = time_threshold

    def __repr__(self):
        out = "Flashcard Deck:\n"
        for c in self.cards:
            out += f"{c}\n"
        return out

    def worst_cards(self):
        total_time = sum([c.time() for c in self.cards])
        if total_time >= 60:
            minutes = total_time // 60
            seconds = int(total_time % 60)
            total_time_str = f'{minutes:.0f} minute{"s" if minutes>1 else ""} {seconds:.0f} second{"s" if seconds>1 else ""}'
        else:
            total_time_str = f'{total_time:.1f} seconds'
        out = f"Flashcard Deck (total time {total_time_str}):\n\n"
        for c in sorted(self.cards, reverse=True):
            out += f"{c}\n"
        return out

    def get_card(self):
        on_deck = []
        for i, c in enumerate(self.cards):
            if not c.is_mastered(self.time_threshold)[0]:
                on_deck.append(i)
        if len(on_deck) > 0:
            return self.cards[secrets.choice(on_deck)]
        else:
            return max(self.cards, key=lambda c: c.is_mastered(self.time_threshold)[1])

    def progress(self):
        completed = 0
        for c in self.cards:
            if c.is_mastered(self.time_threshold)[0]:
                completed += 1
        return completed, len(self.cards)


def generate_addition(start, stop, time_threshold=5):
    a = range(start, stop+1)
    b = range(start, stop+1)
    cards = [Arithmetic(f'{x} + {y} = ', x+y) for x in a for y in b]
    return Deck(cards, time_threshold)

def generate_subtraction(start, stop, time_threshold=5):
    a = range(start, stop+1)
    b = range(start, stop+1)
    cards = [Arithmetic(f'{x+y} - {x} = ', y) for x in a for y in b]
    return Deck(cards, time_threshold)

def generate_multiplication(start, stop, time_threshold=5):
    a = range(start, stop+1)
    b = range(start, stop+1)
    cards = [Arithmetic(f'{x} × {y} = ', x*y) for x in a for y in b]
    return Deck(cards, time_threshold)

def generate_division(start, stop, time_threshold=5):
    a = range(max(1, start), stop+1)
    b = range(start, stop+1)
    cards = [Arithmetic(f'{x*y} ÷ {x} = ', y) for x in a for y in b]
    return Deck(cards, time_threshold)


if __name__ == "__main__":
    print("Running flashcards!")
    addition = generate_addition(0, 1, time_threshold=5)
    while not addition.complete():
        c = addition.get_card()
        t0 = time.time()
        a = input(c.get_problem()[0])
        t = time.time() - t0
        correct = c.log_response(a, t)
        if correct:
            print("Correct!")
        else:
            print("Incorrect!")
        print("")

    print(addition)



