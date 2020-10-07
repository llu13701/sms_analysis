#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 19:47:13 2019

@author: louisalu

testing whether a phrases is name entity or belong to a album category of name entities

"""
import os
os.environ["SPACY_WARNING_IGNORE"] = "W008"
from nlp_script import nlp_name

TIMER=False


def extract_preliminary_ner_from_sentence(tweet):
    NEA_TYPE=['CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY', 'PERCENT','TIME', 'DATE']
    tweet=tweet.translate ({ord(c): "" for c in "!@#$%^&*`~-=_+"})
    tweet=tweet.translate ({ord(c): " " for c in "/\|"})  
    tweet=tweet.replace("\n", " ")                                                
    doc=nlp_name(tweet)
    nea_list=[Y.text for Y in doc.ents if not Y.label_ in NEA_TYPE]    
    nea_list=eliminate_all_digit_ner(nea_list)
    return nea_list

def eliminate_all_digit_ner(nea_list):
    new_nea_list=list(nea_list)
    for x in nea_list:
        if x.isdigit()==True:
            new_nea_list.remove(x)
    return new_nea_list
