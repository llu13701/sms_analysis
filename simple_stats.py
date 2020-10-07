#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 23:27:36 2020

@author: louisalu
"""

import os
#os.chdir("/Users/louisalu/Documents/text/text_analyzer")
import pandas as pd
from matplotlib import pyplot as plt

from incoming_outgoing_msg import count_total_incoming_outgoing_words, create_adjusted_sent_info, \
    message_ratio_ordered_adjusted, count_number_of_incoming_outcoming
from initiation_related import summary_initiation_count, find_initiator_ender, identify_initiation_with_new_topic, \
identify_potential_initiation_point
from sentiment_analysis import bert_sentiment
from topic_analysis import summary_topic, paragraph_summary

from datetime import datetime
import emoji
import matplotlib.backends.backend_pdf
from holy_grail import add_block_conv, holy_grail_analysis, scoring_holy_grail_normal
from preprocessing_script import whatapp_export_processing


def time_conversion(x):
    temp_date=datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timestamp()
    return temp_date

def date_conversation(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()

def date_processing(pd_text):
    pd_text['Message_Day']=pd_text['Message Date'].apply(date_conversation)
    pd_text['Message_seconds']=pd_text['Message Date'].apply(time_conversion)
    pd_text['message_diff'] = pd_text['Message_seconds'].diff()
    pd_text['message_diff']=pd_text['message_diff']/3600 #in hours format
    pd_text['message_diff_z_score']=zscore(pd_text['message_diff'])
    return pd_text

def zscore(x):
    #r = x.rolling(window=window)
    r = x.expanding()
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z

def generate_daily_text_group(pd_text):
    all_dates=pd_text['Message_Day'].drop_duplicates()
    list_of_entire_text=[]
    for i in range(0, len(all_dates)):
        date=all_dates.iloc[i]
        text_list=pd_text.loc[pd_text.Message_Day==date,'Text' ]
        text_list=[x for x in text_list if x==x]
        entire_text=". ".join(text_list)
        list_of_entire_text.append(entire_text)
    return list_of_entire_text


def count_attachment(pd_day_text):
    all_incoming_msg=pd_day_text.loc[pd_day_text.Type=='Incoming', :]
    all_incoming_msg_no_attachment = all_incoming_msg[all_incoming_msg['Text'].notna()]
    pd_day_text.reset_index(drop=True, inplace=True)
    attachment_number=len(all_incoming_msg)-len(all_incoming_msg_no_attachment)
    list_text=pd_day_text['Text'].values.tolist()
    list_text=[x for x in list_text if x==x]
    with_link_length=len(list_text)
    list_text=[x for x in list_text if 'www.' not in x]
    attachment_number=attachment_number+(with_link_length-len(list_text))
    return attachment_number, list_text

def generating_analytical(pd_day_text, pd_master, date,initial_time, initial_time_index,end_time, nr_incoming_again_Index,guy_initiation_index, nr_outgoing_again_Index, girl_initiation_index, text_sentiment_pair):
    send_by_him,send_by_me,fig= count_number_of_incoming_outcoming(pd_day_text, to_graph=False)
    raw_ratio=send_by_him/send_by_me
    pd_adjusted_text= create_adjusted_sent_info(pd_day_text)
    adjusted_ratio= message_ratio_ordered_adjusted(pd_adjusted_text)
    word_count_me,word_count_him,average_outgoing_length, average_incoming_length= \
    count_total_incoming_outgoing_words(pd_day_text)
    initiator, ender= find_initiator_ender(pd_day_text)
    new_topic= identify_initiation_with_new_topic(initiator, initial_time_index, nr_incoming_again_Index, guy_initiation_index, nr_outgoing_again_Index, girl_initiation_index)
    
    attachment_number, list_text=count_attachment(pd_day_text)
    topic_summary= summary_topic(list_text)
    all_incoming_msg=pd_day_text.loc[pd_day_text.Type=='Incoming', :]
    all_incoming_msg_text=[x for x in all_incoming_msg['Text'] if x==x]
    emoji_count=len([c for c in " ".join(all_incoming_msg_text) if c in emoji.UNICODE_EMOJI])

    sentiment=[x[1] for x in text_sentiment_pair if x[0]==date][0]
    #sentiment_name=[x[1] for x in sentiment_map if x[0] == round(sentiment)][0]
    sentiment=str(sentiment)
    
    pd_master=pd_master.append({'Date':date, 'Start Time': initial_time, 'End Time':end_time, 'Text sent by Me':send_by_me,
     'Text Sent by Him':send_by_him, 'raw ratio': raw_ratio, 'adjusted text ratio': adjusted_ratio,
     'word count by me': average_outgoing_length, 'word count by him':average_incoming_length,
     'word ratio': average_incoming_length/(average_outgoing_length+0.00001),'Total Text': send_by_him+send_by_me, 
     'Initiator':initiator , 'Ender':ender , 'initiate with new topic':new_topic, 'Attachment':attachment_number, 'Topic': topic_summary, 
     'Emoji':emoji_count, 'Response':sentiment}, ignore_index=True)
    return pd_master


def generate_master_summary(pd_text):
    #this is where you get the function
    pd_text=date_processing(pd_text)
    all_potential_initiation=identify_potential_initiation_point(pd_text)
    nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index=\
    summary_initiation_count(pd_text, all_potential_initiation)
    pd_master=pd.DataFrame(columns=['Date', 'Start Time', 'End Time', 'Text sent by Me', 'Text Sent by Him', 'raw ratio', 'adjusted text ratio','word count by me', 'word count by him', 'word ratio', 'Total Text', 'Initiator', 'Ender',
                                    'initiate with new topic', 'Emoji', 'Attachment', 'Topic', 'Response'])
    list_of_entire_text=generate_daily_text_group(pd_text)
    all_dates=pd_text['Message_Day'].drop_duplicates()
    
    #checking this sentiment changes
    #text_info= sentiment_analysis_list(list_of_entire_text)
    text_info=bert_sentiment(list_of_entire_text)
    text_info_sentiment=[x[1] for x in text_info]
    text_sentiment_pair=list(zip(all_dates,text_info_sentiment ))
    
    for index_date in range(0, len(all_dates)):
        print ("analysing day ", index_date)
        date=all_dates.iloc[index_date]
        all_date_time=pd_text.loc[pd_text['Message_Day']==date, 'Message Date']
        initial_time_index=all_dates.index[index_date]

        all_date_time.reset_index(drop=True, inplace=True)
        initial_time=all_date_time[0]

        end_time=all_date_time[len(all_date_time)-1]
        pd_day_text=pd_text.loc[pd_text.Message_Day==date, ]
        pd_day_text.reset_index(drop=True, inplace=True)
        
        #this will be used for block study
        pd_master=generating_analytical(pd_day_text, pd_master,date,initial_time, initial_time_index,end_time,\
                                        nr_incoming_again_Index,guy_initiation_index, nr_outgoing_again_Index, girl_initiation_index,\
                                        text_sentiment_pair)
        
    return pd_master


def encode_me_him(x):
    if x=='me':
        return 0
    else:
        return 1

def clean_sentiment(x):
    return float(x.split('/')[0])


    
def summary_analytical(pd_text, pd_master,file_name):
    all_figure=[]
    file_name=file_name+".pdf"
    pdf = matplotlib.backends.backend_pdf.PdfPages(file_name)

    # sent message ratip
    try:
        incoming_msg_count,outgoing_msg_count,fig=count_number_of_incoming_outcoming(date_processing(pd_text), to_graph=True)
        all_figure.append(fig)
    except:
        print ("failed to analyze incoming/outgoing ratio. Maybe less than 7 days data")

    
    try:
    #total words
        pd_master['total_word_by_me']=pd_master['word count by me'].rolling(7).mean()
        pd_master['total_word_by_him']=pd_master['word count by him'].rolling(7).mean()
        pd_master['word_rolling_ratio']=pd_master['total_word_by_him']/pd_master['total_word_by_me']
        fig2, axs = plt.subplots(2,sharex=True, squeeze=True)
        axs[0].plot(pd_master['Date'], pd_master['total_word_by_me'], '-b', label='send by me')
        axs[0].plot(pd_master['Date'], pd_master['total_word_by_him'],'-r', label='send by him')
        leg = axs[0].legend();
        axs[0].set_title('Avg Incoming words vs Avg Outgoing words')
        axs[1].plot(pd_master['Date'], pd_master['word_rolling_ratio'])
        axs[1].set_title('Rolling Incoming/Outgoing Word Ratio')
        all_figure.append(fig2)
    except:
        print ("failed to analyze average word ratio. Maybe less than 7 days data")

    #initiator
    try:
        pd_master['initiator_encoder']=pd_master['Initiator'].apply(encode_me_him)
        pd_master['initiator_encoder_average']=pd_master['initiator_encoder'].rolling(7).mean()
        fig3 = plt.figure()
        plt.plot(pd_master['Date'], pd_master['initiator_encoder_average'])
        plt.title('initiating history - 1: him initiating (beta version)')
        all_figure.append(fig3)
    except:
        print ("failed to initialization. Maybe less than 7 days data")

    try:
    #count emoji
        pd_master['total_attachment']=pd_master['Emoji']+pd_master['Attachment']
        pd_master['total_attachment_average']=pd_master['total_attachment'].rolling(7).sum()
        fig4 = plt.figure()
        plt.plot(pd_master['Date'], pd_master['total_attachment_average'])
        plt.title('rolling 3d multimedia text by him')
        all_figure.append(fig4)
    except:
        print ("failed to count emojis. Maybe less than 7 days data")


    #count sentiment
    #pd_master['raw_sentiment']=pd_master['Response'].apply(clean_sentiment)
    try:
        fig5 = plt.figure()
        plt.plot(pd_master['Date'], pd_master['Response'].apply(float))
        plt.title('sentiment history - higher the better (beta version)')
        all_figure.append(fig5)
    except:
        print ("failed to analyze sentiment. Maybe less than 7 days data")

    try:
    #holy grail
        pd_raw=add_block_conv(pd_text)
        fig6=holy_grail_analysis(pd_raw, method='normal', conversation_cutoff=5, rolling_avg=10)
        all_figure.append(fig6)
    except:
        print ("failed to analyze holy grail conversation. Maybe less than 7 days data")

        
    
    #find topics for the holy grail:
    file_name=file_name.replace(".pdf", "_topic_analysis.csv")
    final_score=scoring_holy_grail_normal(pd_raw)
    range_len=int(len(final_score)*0.3)
    topic_analysis_list=[]
    for i in range(0,range_len):
        print (i)
        top_block_number=final_score.index[i]
        score=final_score.iloc[i]
        all_content=pd_raw.loc[pd_raw.block_conv==top_block_number, 'Text'].values.tolist()
        all_content=[x for x in all_content if x==x]
        all_content=[x for x in all_content if not 'www.' in x]
        date_of_conversation=pd_text.loc[pd_text.block_conv==top_block_number, 'Message Date'].iloc[0]
        keywords=summary_topic(all_content)
        summary=paragraph_summary(all_content)
        topic_analysis_list.append((date_of_conversation, score,keywords,summary ))
    pd.DataFrame(topic_analysis_list).to_csv(file_name)
            
    #finally all of them
    for fig in all_figure: ## will open an empty extra figure :(
        pdf.savefig( fig )
    pdf.close()

def stats_collections(direct_process=True):
    #a simple dashboard of the past text analysis##
    file_name='Messages.csv'
    
    if direct_process==True:
        #file_name='_chat'
        raw_data=whatapp_export_processing()
    else:   
        raw_data=pd.read_csv(file_name)
        
        
    pd_text=raw_data[['Message Date', 'Type','Text']]
    pd_master=generate_master_summary(pd_text)
    
    #initiation needs to be worked on
    #presentation and analytical needs to be worked on as well
    file_name=file_name.replace('.csv', '_analytical.csv')
    pd_master.to_csv(file_name)
    file_name=file_name.replace('.csv', '')
    summary_analytical(pd_text, pd_master,file_name)

if __name__ == "__main__":
    stats_collections()
