import pymorphy2
import pandas as pd
import random
import string
import numpy as np
from collections import defaultdict
import re
from huggingface_hub import hf_hub_download
from tqdm import tqdm
from collections import Counter

morph = pymorphy2.MorphAnalyzer()

class DataCorruption_Words:

    def __init__(self, list_for_corrupt, words_frequency_dict, model_fasstext):

        self.list_for_corrupt = list_for_corrupt
        self.words_frequency_dict = words_frequency_dict
        self.model = model_fasstext
        self.final_texts = []

        self.manipulation = [1, 2, 3, 4]
        self.freq_values = [freq for pos, (freq) in words_frequency_dict.values()]
        self.total_freq = sum(self.freq_values)
        self.translator = str.maketrans('', '', string.punctuation)

    def do_corruption(self):

      for text in tqdm(self.list_for_corrupt):
          self.text_i = text
          self.words = text.split()
          num_replacements = int(len(self.words) * 0.15)
          replaceable_indices = [idx for idx, word in enumerate(self.words) if word != '<BR>']
          replace_indices = random.sample(replaceable_indices, min(num_replacements, len(replaceable_indices)))

          for idx in replace_indices:
              self.word_to_replace = self.words[idx]
              selected_manipulation = random.choice(self.manipulation)
              if selected_manipulation == 1:
                 new_word_i = self.corruption_type_1()
              elif selected_manipulation == 2:
                 new_word_i = self.corruption_type_2()
              elif selected_manipulation == 3:
                 new_word_i =  self.corruption_type_3()
              else:
                 new_word_i = self.corruption_type_4()
              self.words[idx] = new_word_i
          self.final_texts.append(' '.join(self.words))

      return self.final_texts



    def corruption_type_1(self):

      new_word = np.random.choice(list(self.words_frequency_dict.keys()), p=np.array(self.freq_values) / self.total_freq)
      new_word = new_word.lower() if self.word_to_replace.islower() else new_word.capitalize()

      punctuation = ''
      if self.word_to_replace[-1] in string.punctuation:
          punctuation = self.word_to_replace[-1]
          #word_to_replace_i = self.word_to_replace[:-1]
      new_word = new_word.capitalize() if self.word_to_replace[0].isupper() else new_word
      new_word = new_word + punctuation

      return new_word

    def corruption_type_2(self):

      try:
        punctuation = ''.join([char for char in self.word_to_replace if char in string.punctuation])
        word_i = re.sub(r'[^\w\s-]', '', self.word_to_replace)
        pos_to_replace = morph.parse(word_i)[0].tag.POS
        filtered_dict = {word: (pos, freq) for word, (pos, freq) in self.words_frequency_dict.items() if pos == pos_to_replace}
        filtered_freq_values = [freq for pos, (freq) in filtered_dict.values()]
        filtered_total_freq = sum(filtered_freq_values)

        new_word = np.random.choice(list(filtered_dict.keys()), p=np.array(filtered_freq_values) / filtered_total_freq)
        new_word = new_word.lower() if self.word_to_replace.islower() else new_word.capitalize()
        new_word = new_word.capitalize() if self.word_to_replace[0].isupper() else new_word
        new_word = new_word + punctuation
      except ValueError:
        self.corruption_type_3()

      return new_word

    def corruption_type_3(self):

      k_word = int(random.randint(30, 1000))
      word_i = re.sub(r'[^\w\s-]', '', self.word_to_replace)
      neighbors = self.model.get_nearest_neighbors(word_i, k=1000)

      if not neighbors or k_word >= len(neighbors):
        return self.corruption_type_1()  # Return original word if no neighbors or k_word out of range

      new_word = random.choice(neighbors[k_word:])
      new_word = new_word[1]
      punctuation = ''.join([char for char in self.word_to_replace if char in string.punctuation])
      new_word = new_word.capitalize() if self.word_to_replace[0].isupper() else new_word
      new_word = new_word + punctuation
      return new_word


    def corruption_type_4(self):

      k_word = int(random.randint(30, 1000))
      word_i = re.sub(r'[^\w\s-]', '', self.word_to_replace)
      neighbors = self.model.get_nearest_neighbors(word_i, k=1000)
      if not neighbors or k_word >= len(neighbors):
          return self.corruption_type_1()

      parsed_word = morph.parse(word_i)[0]
      word_pos = parsed_word.tag.POS


      same_pos_neighbors = [
          neighbor for neighbor in neighbors[k_word:]
          if morph.parse(neighbor[1])[0].tag.POS == word_pos
      ]


      if same_pos_neighbors:
          random_neighbor = random.choice(same_pos_neighbors)
          return random_neighbor[1]
      else:
          return self.corruption_type_3()
