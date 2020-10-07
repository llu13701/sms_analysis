#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 19:25:18 2019

@author: louisalu
used in answer_to_keyword_function
given a statement or a sentense, scrape initial search result and 
then find a better search term to refine search
output is the list of wiki_keywords and key phrases used to find these keywords

"""

from mediawiki import MediaWiki

wikipedia_m = MediaWiki()
from rake_nltk import Rake

r = Rake()
import os
from nlp_script import nlp

os.environ["SPACY_WARNING_IGNORE"] = "W008"
from ner_testing import extract_preliminary_ner_from_sentence

import re


#use rake to extract questions from keywords
def extract_keywords_with_rake(question):
    r.extract_keywords_from_text(question)
    phrases=r.get_ranked_phrases_with_scores()
    degree=select_degree_for_rake(question)
    phrases=[x[1] for x in phrases if x[0] >degree]
    phrases= filter_repetitive_phrases(phrases, thresh_hold=0.6)
    return phrases

def select_degree_for_rake(question):
    if len(question)>15:
        degree=2
    else:
        degree=1
    return degree


#find similar and disimilar words
#given the list of words, output the ones that are not close to each others
def filter_repetitive_phrases(word_list, thresh_hold=0.6):
    final_word_list=list(word_list)  #this is output
    word_count=len(word_list)
    for i in range(len(word_list)):
        center=nlp(word_list[i])
        if i<len(word_list):
            for j in range((i+1), word_count):
                if center.similarity(nlp(word_list[j])) > thresh_hold:
                    if word_list[j] in final_word_list:
                        final_word_list.remove(word_list[j])
    return final_word_list


def return_rake_and_ner(clean_tweet_list):
    rake_keywords=[extract_keywords_with_rake(x) for x in clean_tweet_list]    
    rake_keywords=[re.sub(r"[^a-zA-Z0-9]+", ' ', x).strip() for sublist in rake_keywords for x in sublist]    
    refined_rake_keyword_list=list(rake_keywords )
    ner_list_group=[extract_preliminary_ner_from_sentence(x) for x in clean_tweet_list]
    return refined_rake_keyword_list,ner_list_group

