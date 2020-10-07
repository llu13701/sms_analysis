import collections
import difflib

from sklearn.feature_extraction.text import TfidfVectorizer

from quer_transformer import return_rake_and_ner
from text_cleanup import clean_up_phrases_no_stopwords_no_short_letters_no_numeric, flatten_lower_ner_list
from words_frequency import find_top_frequent_words
from transformers import pipeline

summarizer = pipeline("summarization")

def check_document_similarity(counter_topic_summaries):
    tfidf = TfidfVectorizer().fit_transform(counter_topic_summaries)
    pairwise_similarity = tfidf * tfidf.T
    return pairwise_similarity


def remove_similar_sentence(cleaned_list_text,clean_text_matrix):
    nonrepetitive_clean_list=[]
    clean_list_original=cleaned_list_text.copy()
    while len(cleaned_list_text)>0:
        checking_text=cleaned_list_text[0]
        index_checking_text=clean_list_original.index(checking_text)
        nonrepetitive_clean_list.append(checking_text)
        matrix_similarity=[clean_text_matrix[index_checking_text, x] for x in range(0, len(clean_list_original))]
        all_similar_sentence=[clean_list_original[matrix_similarity.index(x)] for x in matrix_similarity if x > 0.6]
        for x in all_similar_sentence:
            try:
                cleaned_list_text.remove(x)
            except:
                print ("removing extra failed")
        if len(cleaned_list_text)>0:
            if checking_text==cleaned_list_text[0]:
                cleaned_list_text.remove(checking_text)
    return nonrepetitive_clean_list

def cleanning_remove_similar_sentence(list_text):
    entire_text=". ".join(list_text)
    cleaned_list_text=[clean_up_phrases_no_stopwords_no_short_letters_no_numeric(x,stemmed=False) for x in list_text]
    cleaned_list_text=[x.lower() for x in cleaned_list_text if not x=='']
    if len(cleaned_list_text)>0:
        clean_text_matrix= check_document_similarity(cleaned_list_text)
        cleaned_list_text= remove_similar_sentence(cleaned_list_text, clean_text_matrix)
        entire_text=". ".join(cleaned_list_text)
    return entire_text,cleaned_list_text


def summary_topic(list_text):
    entire_text,cleaned_list_text=cleanning_remove_similar_sentence(list_text)
    
    if len(cleaned_list_text)>0:
        frequent_ideas=find_top_frequent_words(entire_text)
        #try this one #come and fix this one later
        ner_list=return_rake_and_ner(cleaned_list_text)
        ner_list=flatten_lower_ner_list(ner_list[1])
        frequency=collections.Counter(ner_list)
        Other_key_topic=[x[0] for x in frequency.most_common(min(3, len(frequency))) if x[1]>1]
        final_topic=[]
        if len(frequent_ideas)>2:
            for idea in frequent_ideas:
                similarity_score=[difflib.SequenceMatcher(None, idea, x).ratio() for x in ner_list]
                if len(similarity_score)>0:
                    if max(similarity_score)>0.4:
                       final_topic.append(idea)
        else:
            final_topic=frequent_ideas
            
        final_topic=final_topic+Other_key_topic
        topic_summary="/".join(final_topic)
    else:
        topic_summary=''
    return topic_summary

def paragraph_summary(list_text):
    print ("summarizing text")
    entire_text,cleaned_list_text=cleanning_remove_similar_sentence(list_text)
    
    text = entire_text.split(" ")
    if len(text) > 700:
        text=text[:700]
    new_entire_text=" ".join(text)
        
    summarized_paragraph=summarizer(new_entire_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summarized_paragraph