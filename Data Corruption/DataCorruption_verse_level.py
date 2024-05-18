import pandas as pd
import random
import string
import numpy as np
from collections import defaultdict
import re
from huggingface_hub import hf_hub_download
from tqdm import tqdm
from collections import Counter

class VerseCorruption_Verses:

    def __init__(self, list_for_corrupt, random_rows):

        self.list_for_corrupt = list_for_corrupt
        self.random_rows = random_rows
        self.final_text = []

        self.manipulation = [1, 2, 3, 4]


    def do_corruption(self):

      for verse in self.list_for_corrupt:
          self.text = verse
          selected_manipulation = random.choice(self.manipulation)
          if selected_manipulation == 1:
              corrupt_i = self.corruption_type_1()
          elif selected_manipulation == 2:
              corrupt_i = self.corruption_type_2()
          elif selected_manipulation == 3:
              corrupt_i = self.corruption_type_3()
          else:
              corrupt_i = self.corruption_type_4()
          self.final_text.append(corrupt_i)

      return self.final_text


    def corruption_type_1(self):

      words_and_punct = re.findall(r'\b\w+\b|<BR>|[^\w\s<BR>]', self.text)
      capital_flags = [word[0].isupper() for word in words_and_punct if re.match(r'\b\w+\b', word)]
      words = [word for word in words_and_punct if re.match(r'\b\w+\b', word)]

      shuffled_words = words[:]
      random.shuffle(shuffled_words)
      word_index = 0
      result = []
      for i, token in enumerate(words_and_punct):
          if re.match(r'\b\w+\b', token):
              shuffled_word = shuffled_words[word_index]
              if capital_flags[word_index]:
                  shuffled_word = shuffled_word.capitalize()
              else:
                  shuffled_word = shuffled_word.lower()
              result.append(shuffled_word)
              word_index += 1
          else:
              result.append(token)

          if i < len(words_and_punct) - 1:
              next_token = words_and_punct[i + 1]
              if next_token == '<BR>':
                  result.append(' ')
              elif not re.match(r'[^\w\s]', next_token):
                  result.append(' ')

      if result[-1] == ' ':
          result = result[:-1]

      return ''.join(result)

    def corruption_type_2(self):

      lines = self.text.split('<BR>')
      if len(lines) > 4:
          random.shuffle(lines)
      else:
          return self.corruption_type_1()

      shuffled_text = '<BR>'.join(lines)
      return shuffled_text

    def corruption_type_3(self):

      lines = self.text.split('<BR>')
      random_line = random.choice(lines)
      random_other_line = random.choice(self.random_rows)
      index_of_l = lines.index(random_line)
      lines[index_of_l] = random_other_line
      shuffled_text = '<BR>'.join(lines)
      return shuffled_text

    def corruption_type_4(self):

      lines = self.text.split('<BR>')
      random_line = int(random.randint(0, len(lines)-1))
      lines = lines.pop(random_line)
      new_text = '<BR>'.join(lines)
      return new_text