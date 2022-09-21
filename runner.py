from dataclasses import dataclass, field, InitVar
from time import sleep
from typing import List

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from solver import Solver
from dictionnary import DICTIONNARY


@dataclass
class Runner:
    speed: float = field(default=1.0)
    regex: List[str] = field(init=False)
    # s_url: str = field(init=False, default='https://zutom.z-lan.fr/hard')
    s_url: str = field(init=False, default='https://zutom.z-lan.fr/infinit')


    def run(self):
        driver = self._init_window()

        while True:
            if driver.find_element(By.CSS_SELECTOR, 'p[data-popup-text]').text.startswith('Perdu'):
                print('Lost !')
                driver.get(self.s_url)
            elif driver.find_element(By.CSS_SELECTOR, 'span[data-counter]').text=='0':
                print('Won !')
                driver.get(self.s_url)
            else:
                self._process_answers(driver)

    def _process_answers(self, driver: webdriver.Chrome):
        contained_letters = []
        words = DICTIONNARY
        start_letter = self._get_first_letter(driver)
        word_length = self._get_word_length(driver)
        self.regex = Solver.build_init_regex(word_length, start_letter)
        for index in range(1, 7):
            if contained_letters:
                words = self._filter_by_known_values(words, contained_letters)
            words = Solver.filter_with_regex(self.regex, words)
            words = sorted(words, key=lambda x: len(set(x)), reverse=True)
            word = words[0]
            self._send_keys(word, driver)

            contained_letters = self._get_tested_response(driver, index)
            if word_length == self._check_is_all_good(driver, index):
                break

            # filter by word containing value
        sleep(3/self.speed)

    @staticmethod
    def _filter_by_known_values(words: List[str], contained_letters: List[str]):
        v = []
        for word in words:
            count = 0
            for letter in contained_letters:
                if letter in word:
                    count += 1
            if count == len(contained_letters):
                v.append(word)
        return v
    @staticmethod
    def _check_is_all_good(driver: webdriver.Chrome, index: int):
        count = 0
        table = driver.find_element(By.CSS_SELECTOR, f'body > main > table > tr:nth-child({index})')
        word_elements = table.find_elements(By.TAG_NAME, 'td')
        for index, word_element in enumerate(word_elements):
            if 'wellplaced' in word_element.get_attribute('class').split():
                count +=1
        return count
    @staticmethod
    def _get_first_letter(driver: webdriver.Chrome) -> str:
        return driver.find_element(By.CSS_SELECTOR, 'body > main > table > tr:nth-child(1) > td:nth-child(1)').text

    @staticmethod
    def _get_word_length(driver: webdriver.Chrome) -> int:
        table =  driver.find_element(By.CSS_SELECTOR, 'body > main > table > tr:nth-child(1)')
        return len(table.find_elements(By.TAG_NAME, 'td'))

    def _get_tested_response(self, driver: webdriver.Chrome, index: int):
        contained_letters = []
        table = driver.find_element(By.CSS_SELECTOR, f'body > main > table > tr:nth-child({index})')
        letters_to_skip = []
        word_elements = table.find_elements(By.TAG_NAME, 'td')
        for index, word_element in enumerate(word_elements):
            if 'wellplaced' in word_element.get_attribute('class').split():
                self.regex = Solver.letter_goodly_placed(self.regex, index + 1, word_element.text)
                contained_letters.append(word_element.text)
            elif 'existant' in word_element.get_attribute('class').split():
                self.regex = Solver.letter_wrongly_placed(self.regex, index + 1, word_element.text)
                letters_to_skip.append(word_element.text)
                contained_letters.append(word_element.text)
            else:
                if word_element.text not in letters_to_skip:
                    self.regex = Solver.letter_not_there(self.regex, word_element.text)
        return contained_letters

    def _init_window(self) -> webdriver.Chrome:
        options = Options()
        options.add_argument('window-size=1920x1080')

        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

        driver.get(self.s_url)

        driver.maximize_window()
        return driver

    @staticmethod
    def _send_keys(word: str, driver: webdriver.Chrome) -> None:
        input = driver.find_element(By.TAG_NAME, 'body')
        input.send_keys(word)
        input.send_keys(Keys.ENTER)
