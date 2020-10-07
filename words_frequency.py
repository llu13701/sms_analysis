#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 16:06:49 2020

@author: louisalu
"""
from text_cleanup import convert_text_to_tokens,remove_single_word_in_list_of_phrases,\
 remove_substring_of_list_with_order
from collections import Counter
from nlp_script import flat_list_of_list,find_kneeling_point

def generate_n_gram_words(tokens, n=4):
    master_list_gram=list()
    for n in range(1,n):
        ngrams = zip(*[tokens[i:] for i in range(n)])
        list_gram=[" ".join(ngram) for ngram in ngrams]
        list_gram= remove_single_word_in_list_of_phrases(list_gram)
        master_list_gram=master_list_gram+list_gram
    return master_list_gram

def filter_top_percentile_ngrams(tokens, n=4, percentile=0.05):
    meta_word_list=list()
    list_gram=generate_n_gram_words(tokens, n=n)
    counts=Counter(list_gram)
    counts_list=list(counts.items())
    count_name=[x[0] for x in counts_list]
    count_frequency=return_adjusted_frequency_count(counts_list)
    new_counts_list=list(zip(count_name, count_frequency))
    new_counts_list.sort(key=lambda x:x[1], reverse=True)
    meta_word_list=new_counts_list[0:round(len(counts)*percentile)]    
    return meta_word_list

def return_adjusted_frequency_count(flat_list):
    new_count_list=list()
    for x in flat_list:
        if x[1]==1:
            new_count_list.append(1)
        else:
            new_count_list.append(x[1]*(len(x[0].split(" "))))
    return new_count_list


def return_pair_list_adjusted_frequency(flat_list):
    new_count_list=return_adjusted_frequency_count(flat_list)
    wiki_names=[x[0] for x in flat_list]
    new_flat_list=list(zip(wiki_names, new_count_list))
    new_flat_list=sorted(new_flat_list, key = lambda x: x[1], reverse=True)
    return new_flat_list


def find_top_frequent_words(text_list):
    special_list=['wikipedia', 'wiki' ]
    tokens= convert_text_to_tokens(text_list, special_list)
    tokens=[word for word in tokens if len(word)>2]
    meta_word_list=filter_top_percentile_ngrams(tokens, n=6)    
    
    #flat_list = [item for sublist in meta_word_list for item in sublist]
    flat_list=flat_list_of_list(meta_word_list)
    
    flat_list.sort(key=lambda x: x[1], reverse=True)           
    flat_list=[x for x in flat_list if x[1]>1] 
    flat_list=return_pair_list_adjusted_frequency(flat_list)
    name_list=[x[0] for x in flat_list ]
    final_flat_list= remove_substring_of_list_with_order(name_list)
    count_list=[x[1] for x in flat_list]
    
    index_point=find_index_with_knee_points(count_list)
    final_flat_list=final_flat_list[0:(min(min(5,index_point),len(final_flat_list)))]
    return (final_flat_list)

def find_index_with_knee_points(count_list):
    mid_point=find_kneeling_point(count_list, curve='concave', direction='decreasing')
    if not mid_point==0:
        try:
            index_point=count_list.index(mid_point)
        except:
            index_point=1
    else:
        index_point=5
    return index_point