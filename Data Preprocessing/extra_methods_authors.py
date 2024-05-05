from tqdm import tqdm
import pandas as pd
import re
import string
import nltk
from rhymetagger import RhymeTagger



def delete_unnecessary(poem):
    def calculate_average(lines_per_stanza):
        return sum(lines_per_stanza) / len(lines_per_stanza)

    stanzas = poem.split("break")
    lines_per_stanza = [len(stanza.strip().split("br")) for stanza in stanzas]
    average_lines = calculate_average(lines_per_stanza)
    comment = ''
    
    # Remove stanzas with less lines than average
    while len(lines_per_stanza) > 0 and lines_per_stanza[0] < average_lines:
        stanzas.pop(0)
        lines_per_stanza.pop(0)
        comment = 'smth was deleted'
    
    while len(lines_per_stanza) > 0 and lines_per_stanza[-1] < average_lines:
        stanzas.pop(-1)
        lines_per_stanza.pop(-1)
        comment = 'smth was deleted'
    
    return "break".join(stanzas), comment

def preprocess(text):

    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    stopwords = set(nltk.corpus.stopwords.words('russian'))
    text = ' '.join(word for word in text.split() if word not in stopwords)
    return text

def rhyme_detection(text, rt):

    cnt_rhyme = 0
    cnt_rows = 0
    if 'break' in text:
      verse_list = text.split(' break ')
    else:
      verse_list = text
    for i in range(len(verse_list)):
        verse_i = preprocess(verse_list[i])
        verse_i = verse_i.split(' br ')
        cnt_rows += len(verse_i)
        rhymes = rt.tag(verse_i, output_format=3) 
        for i in range(len(rhymes)):
            if type(rhymes[i]) == int:
              cnt_rhyme += 1
    if cnt_rhyme >= 0.1 * cnt_rows:
      return True
    else:
      return False
    
def digit_detection(text):
    
    def is_only_symbols_and_digits(s):
        for char in s:
            if char not in string.digits and char not in string.punctuation:
                return False
        return True

    parts_text = []
    parts = text.strip().split('break')
    for part_i in parts:
        if part_i.startswith('br'):
            part_i = part_i[2:]
        if not is_only_symbols_and_digits(part_i.strip()):
            #print(part_i, is_only_symbols_and_digits(part_i))
            parts_text.append(part_i)
    new_text = "break".join(parts_text)
    if len(parts) != len(parts_text):
        status = True # it was changed
    else:
        status = False
    return new_text, status

def split_text(text):
    break_index = text.find('break')
    br_index = text.find('br')

    if break_index == -1 or (br_index != -1 and br_index < break_index):
        return pd.Series({'Poem Title': ' ', 'Poem Texting': text})
    else:
        return pd.Series({'Poem Title': text[:break_index], 'Poem Texting': text[break_index+6:]})