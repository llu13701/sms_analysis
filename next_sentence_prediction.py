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
#from transformers import AutoTokenizer, AutoModelForSequenceClassification
#tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
#model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
    
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
    
    '''
    ###############################################
    #similarity approach on ner, doesnt work very well
    if response==True:  #far more response == true
        new_prompt_string=text_cleaning_master(prompt)
        new_next_sentence=text_cleaning_master(next_sentence)    
        prompt_keyword_list,prompt_ner_list=return_rake_and_ner([new_prompt_string])
        next_keyword_list,next_ner_list=return_rake_and_ner([new_next_sentence])
        prompt_ner_list=prompt_ner_list[0]+prompt_keyword_list
        next_ner_list=next_ner_list[0]+next_keyword_list
        
        #using w2v
        max_prmopt_list=[]
        for word in prompt_ner_list:
            potential_list=[nlp(word).similarity(nlp(y)) for y in next_ner_list]
            if len(potential_list)>0:
                max_prmopt_list.append(max(potential_list))
        
        if len(max_prmopt_list)>0:
            if max(max_prmopt_list)>0.5:
                response=True
            else:
                response=False
    '''
    return response



        