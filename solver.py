import re
from dataclasses import dataclass
from typing import List


@dataclass
class Solver:

    @staticmethod
    def filter_with_regex(regex: List[str], dictionnary: List[str]):
        regex_str = ''.join(regex)
        r = re.compile(regex_str)
        m = list(filter(r.match, dictionnary))
        return m

    @staticmethod
    def insert_char_at_pos(string, index, char):
        return string[:index] + char + string[index:]

    @staticmethod
    def letter_goodly_placed(regex: List[str], index: int, letter: str):  # Green letter
        regex[index] = letter
        return regex

    @staticmethod
    def letter_wrongly_placed(regex: List[str], index_input: int, letter: str):  # Yellow letter
        if regex[index_input][0] == '.':
            regex[index_input] = f'[^{letter}]'
        else:
            if letter not in regex[index_input]:
                regex[index_input] = Solver.insert_char_at_pos(regex[index_input], -2, letter)
        return regex

    @staticmethod
    def letter_not_there(regex: List[str], letter: str):  # Red letter
        tmp_regex = []
        for index, element in enumerate(regex):
            if '.' in element and 1 < index < len(regex):
                tmp_regex.append(f'[^{letter}]')
            elif element[0] == '[' and 1 < index < len(regex) - 1:
                element = Solver.insert_char_at_pos(element, -2, letter)
                tmp_regex.append(element)
            else:
                tmp_regex.append(element)
        return tmp_regex

    @staticmethod
    def build_init_regex(word_length: int, start_letter: str) -> List[str]:
        return list(f'^{start_letter}{"." * (word_length - 1)}$')
