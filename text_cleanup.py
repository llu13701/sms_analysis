#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 23:08:29 2019

@author: louisalu
"""
from urllib.parse import unquote

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 
from collections import Counter
import re

from nlp_script import total_stopword, wiki_string, clean_string_master, nlp

ps = PorterStemmer() 
#sym_spell=loading_symspell()


def stemming_list_of_phrases(final_phrases):
    new_final_phrases=list()
    temp=[word_tokenize(phrase) for phrase in final_phrases]        
    for x in temp:            
      new_final_phrases.append(" ".join([ps.stem(w) for w in x]))
  
    return new_final_phrases

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


def clean_list_of_ner(ner_list_group):
    ner_list=flatten_lower_ner_list(ner_list_group)
    ner_list=[clean_up_phrases_no_stopwords_no_short_letters_no_numeric(x, stemmed=False) for x in ner_list]
    ner_list=list(set([x for x in ner_list if not x==''])) 
    return ner_list


def stem_a_phrase(phrase):
# stemming a phrases
    x_token=word_tokenize(phrase.lower())
    new_phrase=" ".join([ps.stem(w) for w in x_token])
    return new_phrase


def extract_keyword_from_wikiurl(re_search_id ):
# given wiki url, extract the wiki title, eliminate all special characters
    wiki_keyword=re_search_id.replace(wiki_string, "")
    wiki_keyword=unquote(wiki_keyword)
    wiki_keyword=wiki_keyword.replace("_", " ")
    wiki_keyword=wiki_keyword.strip()
    return wiki_keyword

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


def lemmatization(texts):
    output = []
    for i in texts:
        s = [token.lemma_ for token in nlp(i)]
        output.append(' '.join(s))
    return output





def merge_cat_and_content_pair(wiki_page_cat_list,full_content_pair,group_wiki_list):
    """#in a tuple structure, merge everything in the same list into one giant string"""
    new_merged_cat=[]
    new_merged_content=[]
    for keyword_list in group_wiki_list:
        new_merged_cat.append((keyword_list[0], [item for sublist in [x[1] for x in wiki_page_cat_list if x[0] in keyword_list] for item in sublist]))
        grouped_content=[x[1] for x in full_content_pair if x[0] in keyword_list]
        mega_content=''
        for x in grouped_content:
            mega_content=mega_content+x
        new_merged_content.append((keyword_list[0], mega_content))
    return new_merged_cat,new_merged_content


def stem_unqiue_list(flat_list):
    """#clean up a list of items using stems and case insensitives. still preserve the order """
    stem_lower_flat_list=list(flat_list)
    non_repeated_flat_list=list()
    stem_lower_flat_list=[stem_a_phrase(x) for x in stem_lower_flat_list]
    marker=set()
    for i in range(len(flat_list)):
        if stem_lower_flat_list[i] not in marker:
            non_repeated_flat_list.append(flat_list[i])
            marker.add(stem_lower_flat_list[i])
    return non_repeated_flat_list


def concat_two_list_to_flat (category_dict_final, nea_keywords):
    """helper functions,just add another list and flatten the list with unique elements only """
    flat_list = [item for category_dict_final in category_dict_final for item in category_dict_final]
    flat_list=list(set(flat_list))
    nea_keywords=list(set(nea_keywords))
    flat_list=list(set(flat_list+nea_keywords))
    return flat_list


def remove_special_reddit_reference(mystring):
    """for all quotes within '>xxxx\n' format """
    start = mystring.find( '>' )
    end = mystring.find( '\n' )
    if start != -1 and end != -1:
        result=mystring[0:start]+mystring[end: len(mystring)].strip()
    else:
        result=mystring

    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    if regex.search(result[0]) == None:
        result=result
    else:
        result=result[1:]
    return result


def remove_urls (vTEXT):
    vTEXT = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', vTEXT, flags=re.MULTILINE)
    return(vTEXT)


def remove_parathesis(para):
    para = re.sub(re.escape("("), '', para)
    para = re.sub(re.escape(")"), '', para)
    para = re.sub(re.escape("["), '', para)
    para = re.sub(re.escape("]"), '', para)
    return para


def clean_reddit_post_format(para):
    para = para.replace("\n", "")
    para = re.sub(r'\[[0-9]*\]', ' ', para)
    para = re.sub(r'\s+', ' ', para)
    return para

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def remove_special_char(x):
    return ''.join(e for e in x if e.isalnum())
