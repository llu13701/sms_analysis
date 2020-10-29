#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 23:08:29 2019

@author: louisalu
"""

from nltk.stem import PorterStemmer
from collections import Counter
import re

from nlp_script import total_stopword

ps = PorterStemmer() 

def stemma_single_word(x):
    return ps.stem(x)

def return_valid_single_nondict_word(word):
    character=list(word)
    if len(character)>0:
        max_character_num=Counter(character).most_common(1)[0][1]
    else:
        max_character_num=0
    if max_character_num > 3:
        return False
    else:
        return word

def clean_up_phrases_no_stopwords_no_short_letters_no_numeric(phrase, stemmed=True):
    filtered_words=[]
    phrase=re.sub("\n", " ", phrase)
    for word in phrase.split(" "):
        word=word.strip()
        if not word=='':
            if not len(word)>2: continue
            if word in total_stopword: continue
            word = re.sub('[^A-Za-z0-9]+', '', word)
            if word.isdigit(): continue    
            if stemmed: 
                word=stemma_single_word(word)
                if word in total_stopword: continue
            if word==False: continue                
            word=return_valid_single_nondict_word(word)
            if word==False: continue    
            filtered_words.append(word)
    return " ".join(filtered_words)


def flatten_lower_ner_list(ner_list):
    ner_list=[x for x in ner_list if not x==[]]
    ner_list=[x.lower() for sublist in ner_list for x in sublist]    
    return ner_list


#given a giant body of text, convert to tokens, take out stopwords and alsp special characters
def convert_text_to_tokens(text_list, special_list):
    text_list=" ".join([word for word in text_list.split() if word not in total_stopword])
    tokens = [token for token in text_list.split(" ") if token != ""]
    for x in special_list:
        tokens=list(filter(lambda a:a !=x, tokens))
    return tokens


def remove_substring_of_list_with_order(flat_list):
# wrapper for remove_substring in_list, return with original order
    new_flat_list=list(remove_substring_in_list(flat_list))
    new_flat_list_order=[flat_list.index(x) for x in new_flat_list]
    final_flat_list=[x for _, x in sorted(zip(new_flat_list_order, new_flat_list), reverse=False)]
    return final_flat_list


def remove_substring_in_list(string_list):
# remove substring withiin the list
    return set(i for i in string_list
           if not any(i in s for s in string_list if i != s))


def remove_single_word_in_list_of_phrases(list_gram):
# if it is a two word or more, check to see if one word is mask by a single letter

    for i in range(len(list_gram)):
        x=list_gram[i]
        if len(x.split(" ")) > 1:
            tokens=x.split(" ")
            for j in tokens:
                if len(j)<2:
                    tokens.remove(j)
            if len(tokens)>0:
                list_gram[i]=" ".join(tokens)
            else:
                list_gram[i]=""
    return list_gram




