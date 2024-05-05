from rhymetagger import RhymeTagger
from tqdm import tqdm
import pandas as pd
import re
import nltk
from rhymetagger import RhymeTagger
import string
from tqdm import trange
from extra_methods_authors import delete_unnecessary, preprocess, rhyme_detection, digit_detection, split_text

class FreshDataPrep:

    def __init__(self, df, column_text):
        self.df = df
        self.column_text = column_text
        

    def total_preprocessing(self):
        """Total Dataset Preparation"""
        rt = RhymeTagger()
        rt.load_model(model='ru')
        
        self.df['Poem Text'] = self.df['Poem Text'].apply(lambda x: x.replace('\n\n', ' break '))
        self.df['Poem Text'] = self.df['Poem Text'].apply(lambda x: x.replace('\n', ' br '))
        
        self.df[['Poem Title', 'Poem Texting']] = self.df['Poem Text'].apply(split_text)
        
        self.df['Rhyme'] = 0
        with pd.option_context('mode.chained_assignment', None):
            for i in range(len(self.df)):
                if self.df['Poem Text'][i] != -1:
                   self.df['Rhyme'][i] = rhyme_detection(self.df['Poem Texting'][i], rt)
        self.df['Poem Final'] = ''
        self.df['Comment'] = ''
        self.df['Status'] = ''
        for i in range(len(self.df)):
            self.df['Poem Final'][i], self.df['Comment'][i] = delete_unnecessary(self.df['Poem Texting'][i])
        #extra check for unbelivable situations
        for i in range(len(self.df)):
            self.df['Poem Final'][i], self.df['Comment'][i] = delete_unnecessary(self.df['Poem Final'][i])
        for i in range(len(self.df)):
            self.df['Poem Final'][i], self.df['Status'][i] = digit_detection(self.df['Poem Final'][i])
        return self.df
        
      

                
    
    
    

