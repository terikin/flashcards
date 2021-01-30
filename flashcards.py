# flashcards.py
#
# module providing a backend for kids flashcards to practice math, etc.
#

from enum import Enum
import secrets
import time
import yaml


class ResponseMetadata:
    """For a given attempt to answer a problem, store the given answer and how long it took"""
    def __init__(self, correct, answer, time):
        self.correct = correct
        self.answer = answer
        self.time = time

    def __repr__(self):
        return f'{self.answer} ({"correct" if self.correct else "incorrect"}): {self.time:.1f} seconds'

    def as_yaml_dict(self):
        return {'correct': self.correct,
                'answer': self.answer,
                'time': self.time}

    @staticmethod
    def from_yaml_dict(yaml_dict):
        return ResponseMetadata(yaml_dict['correct'], yaml_dict['answer'], yaml_dict['time'])


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

    class Result(Enum):
        INCORRECT = 0
        CORRECT = 1
        INVALID = 2

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
        result = self._check_answer(given_answer)
        if result is not Card.Result.INVALID:
            self.responses.append(ResponseMetadata(result is Card.Result.CORRECT, given_answer, time))
        return result

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

    def as_yaml_dict(self):
        return {'problem': self.problem,
                'answer': self.answer,
                'responses': [r.as_yaml_dict() for r in self.responses]}

    @staticmethod
    def from_yaml_dict(yaml_dict):
        out = Arithmetic(yaml_dict['problem'], yaml_dict['answer'])
        for r in yaml_dict['responses']:
            out.responses.append(ResponseMetadata.from_yaml_dict(r))
        return out

    def _check_answer(self, given_answer):
        try:
            if self.answer == int(given_answer):
                return Card.Result.CORRECT
            else:
                return Card.Result.INCORRECT
        except:
            return Card.Result.INVALID


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

    def as_yaml_dict(self):
        return {"time_threshold": self.time_threshold,
                "cards": [c.as_yaml_dict() for c in sorted(self.cards, reverse=True)]}

    @staticmethod
    def from_yaml_dict(yaml_dict):
        # Note that this just assumes arithmetic for the moment.  Any generalization with other Card objects will require a fix.
        cards = [Arithmetic.from_yaml_dict(cd) for cd in yaml_dict['cards']]
        return Deck(cards, yaml_dict['time_threshold'])

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


class RangeTypes(Enum):
    OuterProduct = 0
    InnerProduct = 1


def generate_pairs(a_lims, b_lims=None, range_type=RangeTypes.OuterProduct):
    assert (len(a_lims) == 2)
    if not b_lims:
        b_lims = a_lims
    else:
        assert (len(b_lims) == 2)

    a = range(a_lims[0], a_lims[1] + 1)
    b = range(b_lims[0], b_lims[1] + 1)
    if range_type is RangeTypes.OuterProduct:
        vals = [ (x, y) for x in a for y in b]
    elif range_type is range_type.InnerProduct:
        vals = [ v for v in zip(a, b)]
    return vals


def generate_addition(vals, time_threshold=5):
    cards = [Arithmetic(f'{x} + {y} = ', x+y) for (x, y) in vals]
    return Deck(cards, time_threshold)


def generate_subtraction(vals, time_threshold=5):
    cards = [Arithmetic(f'{x+y} - {x} = ', y) for (x, y) in vals]
    return Deck(cards, time_threshold)


def generate_multiplication(vals, time_threshold=5):
    cards = [Arithmetic(f'{x} × {y} = ', x*y) for (x, y) in vals]
    return Deck(cards, time_threshold)


def generate_division(vals, time_threshold=5):
    cards = []
    for (x, y) in vals:
        if not (x == 0):
            cards.append(Arithmetic(f'{x*y} ÷ {x} = ', y))
    return Deck(cards, time_threshold)


def generate_square_roots(vals, time_threshold=5):
    cards = [Arithmetic(f'√{x*x} = ', x) for (x, y) in vals]
    return Deck(cards, time_threshold)


def load_deck(file):
    with open(file) as ymlfile:
        return Deck.from_yaml_dict(yaml.load(ymlfile, Loader=yaml.SafeLoader))


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



