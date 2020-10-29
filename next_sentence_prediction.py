#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 23:29:15 2020

@author: louisalu
"""

from transformers import BertTokenizer, BertForNextSentencePrediction
from nlp_script import nlp_name,total_stopword
import re
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForNextSentencePrediction.from_pretrained('bert-base-uncased', return_dict=True)

#https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment?text=I+like+you.+I+love+you

def text_cleaning_master(prompt):
    doc_prompt=nlp_name(prompt)
    prompt_sentence_list=[sent for sent in doc_prompt.sents]
    new_prompt=[]
    for sent in prompt_sentence_list:
        potential_list=" ".join([x for x in sent.text.split(" ") if (not re.sub('[^A-Za-z0-9]+', '', x.lower()) in total_stopword) and (len(re.sub('[^A-Za-z0-9]+', '', x.lower()))>3)])
        if not potential_list=='':
            if potential_list[len(potential_list)-1].isalnum():
                potential_list=potential_list+"."
            new_prompt.append(potential_list)
    new_prompt_string=" ".join(new_prompt)
    return new_prompt_string



def next_sentence_prediction(prompt,next_sentence):
    #################################################
    #this is bert approach
    encoding = tokenizer(prompt, next_sentence, return_tensors='pt')
    outputs = model(**encoding, next_sentence_label=torch.LongTensor([1]))
    logits = outputs.logits
    #'assert logits[0, 0] < logits[0, 1] # next sentence was random
    if logits[0, 0] < logits[0, 1]:
        response=False
    else:
        response=True
    
    return response



        