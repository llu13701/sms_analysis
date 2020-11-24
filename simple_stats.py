#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 23:27:36 2020

@author: louisalu
"""

import os
#os.chdir("/Users/louisalu/Documents/text/text_analyzer")
os.chdir(os.getcwd())

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import collections

from incoming_outgoing_msg import count_total_incoming_outgoing_words, create_adjusted_sent_info, \
    message_ratio_ordered_adjusted, count_number_of_incoming_outcoming,identify_custom_stopwords
from initiation_related import summary_initiation_count, find_initiator_ender, identify_initiation_with_new_topic
from sentiment_analysis import bert_sentiment
from topic_analysis import summary_topic, paragraph_summary

from datetime import datetime
import emoji
import matplotlib.backends.backend_pdf
from holy_grail import add_block_conv, holy_grail_analysis
from preprocessing_script import master_preprocessing_script

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

def encode_me_him(x):
    if x=='me':
        return 0
    else:
        return 1

def clean_sentiment(x):
    return float(x.split('/')[0])

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

def categorization_him_me(first_conversation,him_initiation,her_initiation):
    '''1-completely him new initiaiton, 0- completely me new initiation, 
    me replying back - 0.5, him replying back -0.25 '''
    initiation_list=[]
    for i in range(0, len(first_conversation)):
        x=first_conversation['index_holder'].iloc[i]
        if x in him_initiation:
            initiation_list.append(1)
        elif x in her_initiation:
            initiation_list.append(0)
        else:
            msg_type=first_conversation['Type'].iloc[i]
            if msg_type=='Incoming': #him replying
                initiation_list.append(0.25)
            else:
                initiation_list.append(0.5) #me replying
                
    first_conversation['initiation_score']=initiation_list
    return first_conversation
                

def count_attachment(pd_day_text, msg_type='Incoming'):
    all_incoming_msg=pd_day_text.loc[pd_day_text.Type==msg_type, :]
    all_incoming_msg_no_attachment = all_incoming_msg[all_incoming_msg['Text'].notna()]

    #adding the other attachment
    all_incoming_msg_no_attachment=all_incoming_msg_no_attachment[~all_incoming_msg_no_attachment.Text.str.contains('<Multimedia')]
    all_incoming_msg_no_attachment=all_incoming_msg_no_attachment[~all_incoming_msg_no_attachment.Text.str.contains('<Media')]
    all_incoming_msg_no_attachment=all_incoming_msg_no_attachment[~all_incoming_msg_no_attachment.Text.str.contains('<Pominięto multimedia>')]
    all_incoming_msg_no_attachment=all_incoming_msg_no_attachment[~all_incoming_msg_no_attachment.Text.str.contains('<attached')]

    pd_day_text.reset_index(drop=True, inplace=True)
    attachment_number=len(all_incoming_msg)-len(all_incoming_msg_no_attachment)
    all_incoming_msg_no_link=all_incoming_msg_no_attachment[~all_incoming_msg_no_attachment.Text.str.contains('www.')]
    web_link=len(all_incoming_msg_no_attachment)-len(all_incoming_msg_no_link)
    attachment_number=attachment_number+web_link
    list_text=pd_day_text['Text'].values.tolist()
    list_text=[x for x in list_text if x==x]
    return attachment_number, list_text

def calculate_length_of_total_conv(pd_day_text):
    #calculating how long did we spend texting each other
    total_block_conversation=list(set(pd_day_text['block_conv'].values.tolist()))
    common_total_seconds=0
    me_total_seconds=0
    him_total_seconds=0
    for block in total_block_conversation:
        min_time=min(pd_day_text.loc[pd_day_text.block_conv==block, 'Message_seconds'])
        max_time=max(pd_day_text.loc[pd_day_text.block_conv==block, 'Message_seconds'])
        time_count=max_time-min_time
        participants=list(set(pd_day_text.loc[pd_day_text.block_conv==block, 'Type'].tolist()))
        if time_count<1 or len(participants)==1:
            list_of_text=pd_day_text.loc[pd_day_text.block_conv==block, 'Text']
            list_of_text=" ".join([x for x in list_of_text if x==x])
            try:
                msg_length=len(list_of_text.split(" "))
            except:
                msg_length=0
                print ("msg is none: ",list_of_text )
            time_count=(msg_length/40)*60 +2*60#average texting speed is 40 wpm, 5mins prep time
            if participants==['Incoming']:
                him_total_seconds=him_total_seconds+time_count
            else:
                me_total_seconds=me_total_seconds+time_count
        else:
            common_total_seconds=common_total_seconds+time_count
    return me_total_seconds+common_total_seconds, him_total_seconds+common_total_seconds

def calculate_hours_in_talk(pd_day_text, msg_type='Incoming'):
    #how many hours are you guys keep in touch
    #check incoming vs outcoming
    all_dates=pd_day_text.loc[pd_day_text.Type==msg_type, 'Message Date']
    all_hours=[datetime.strptime(x, '%Y-%m-%d %H:%M:%S').hour for x in all_dates]
    all_hours_list=list(collections.Counter(all_hours).items())
    #all_hours_list=[x[0] for x in all_hours_list if x[1]>1]
    hours_in_touch=len(all_hours_list)
    return hours_in_touch

def calculate_gnat_tendency(pd_day_text,nr_outgoing_again_Index):
    #figuring out the gnat tendancy
    '''if there is no response, i shall text again'''
    all_index=pd_day_text['index_holder'].values.tolist()
    gnat_abs=[x for x in all_index if x in nr_outgoing_again_Index]
    all_block_convo=set(pd_day_text['block_conv'].values.tolist())
    gnat_percentage=len(gnat_abs)/len(all_block_convo)
    return len(gnat_abs),gnat_percentage

#the reponse text doesnt seem to work very well at all
def calculate_reponse_time(pd_day_text,nr_outgoing_again_Index,girl_initiation_index,nr_incoming_again_Index,guy_initiation_index):
    #response_time
    pd_potential_response=pd_day_text.groupby('block_conv').first()
    #response for outgoing
    outgoing_index=pd_potential_response.loc[pd_potential_response.Type=='Outgoing', : ]
    outgoing_reponse_item=[]
    for x in outgoing_index['index_holder']:
        if x not in nr_outgoing_again_Index and x not in girl_initiation_index:
            outgoing_reponse_item.append(x)
            
    incoming_index=pd_potential_response.loc[pd_potential_response.Type=='Incoming', : ]
    incoming_reponse_item=[]
    for x in incoming_index['index_holder']:
        if x not in nr_incoming_again_Index and x not in guy_initiation_index:
            incoming_reponse_item.append(x)

    if len(incoming_reponse_item)==0:
        incoming_response_time=0
    else:
        incoming_response_time=pd_day_text.loc[pd_day_text['index_holder'].isin(incoming_reponse_item), 'message_diff'].mean()
    
    if len(outgoing_reponse_item)==0:
        outgoing_response_time=0
    else:
        outgoing_response_time=pd_day_text.loc[pd_day_text['index_holder'].isin(outgoing_reponse_item), 'message_diff'].mean()
    
    return incoming_response_time,outgoing_response_time


def generating_analytical(pd_day_text, pd_master, date,initial_time, initial_time_index,end_time, nr_incoming_again_Index,guy_initiation_index, nr_outgoing_again_Index, girl_initiation_index, text_sentiment_pair, custom_stopwords):
    send_by_him,send_by_me,fig= count_number_of_incoming_outcoming(pd_day_text,pd_master, to_graph=False)
    raw_ratio=send_by_him/send_by_me
    
    word_count_me,word_count_him,average_outgoing_length, average_incoming_length= \
    count_total_incoming_outgoing_words(pd_day_text, no_stopwords=False, custom_stopwords=custom_stopwords)
    
    valid_word_count_me,valid_word_count_him,average_valid_outgoing_length, average_valid_incoming_length= \
    count_total_incoming_outgoing_words(pd_day_text, no_stopwords=True, custom_stopwords=custom_stopwords)

    pd_adjusted_text= create_adjusted_sent_info(pd_day_text)
    adjusted_ratio= message_ratio_ordered_adjusted(pd_adjusted_text)
    adjusted_words_ratio=message_ratio_ordered_adjusted(pd_adjusted_text, adjustment_type='total_words')
    #find the total times we spend on texting and overall frequencies
    me_total_seconds, him_total_seconds=calculate_length_of_total_conv(pd_day_text)
    him_hours_in_touch=calculate_hours_in_talk(pd_day_text, msg_type='Incoming')
    me_hours_in_touch=calculate_hours_in_talk(pd_day_text, msg_type='Outgoing')
    him_hours_in_touch=max(him_hours_in_touch, 1)
    me_hours_in_touch=max(me_hours_in_touch, 1)

    gnat_abs,gnat_percentage=calculate_gnat_tendency(pd_day_text,nr_outgoing_again_Index)
    #beta version
    him_response_time,me_response_time=calculate_reponse_time(pd_day_text,nr_outgoing_again_Index,girl_initiation_index,nr_incoming_again_Index,guy_initiation_index)
    initiator,ender= find_initiator_ender(pd_day_text)
    new_topic= identify_initiation_with_new_topic(initiator, initial_time_index, nr_incoming_again_Index, guy_initiation_index, nr_outgoing_again_Index, girl_initiation_index)
    attachment_number_him, list_text_him=count_attachment(pd_day_text, msg_type='Incoming')
    attachment_number_her, list_text_her=count_attachment(pd_day_text, msg_type='Outgoing')
    topic_summary= summary_topic(list_text_him)
    
    all_incoming_msg=pd_day_text.loc[pd_day_text.Type=='Incoming', :]
    all_incoming_msg_text=[x for x in all_incoming_msg['Text'] if x==x]
    emoji_count_him=len([c for c in " ".join(all_incoming_msg_text) if c in emoji.UNICODE_EMOJI])
    
    all_outgoing_msg=pd_day_text.loc[pd_day_text.Type=='Outgoing', :]
    all_outgoing_msg=[x for x in all_outgoing_msg['Text'] if x==x]
    emoji_count_her=len([c for c in " ".join(all_outgoing_msg) if c in emoji.UNICODE_EMOJI])

    sentiment=[x[1] for x in text_sentiment_pair if x[0]==date][0]
    #sentiment_name=[x[1] for x in sentiment_map if x[0] == round(sentiment)][0]
    sentiment=str(sentiment)
    
    pd_master=pd_master.append({'Date':date, 'Start Time': initial_time, 'End Time':end_time, 'Text sent by Me':send_by_me,
     'Text Sent by partner':send_by_him, 'raw ratio': raw_ratio, 'adjusted text ratio': adjusted_ratio,
     'word count by me': average_outgoing_length, 'word count by partner':average_incoming_length,
     'word ratio': average_incoming_length/(average_outgoing_length+0.00001),'Total Text': send_by_him+send_by_me, 
     'Initiator':initiator , 'Ender':ender , 'initiate with new topic':new_topic, 'Attachment_partner':attachment_number_him,'Attachment_me':attachment_number_her, 'Topic': topic_summary, 
     'Emoji_partner':emoji_count_him, 'Emoji_me':emoji_count_her, 'Response':sentiment, \
     'adjust_word_ratio': adjusted_words_ratio,'total_minutes_partner':him_total_seconds/60, 'total_minutes_me': me_total_seconds/60, \
     'hours_in_touch_partner':him_hours_in_touch, 'hours_in_tough_me': me_hours_in_touch, 'gnat_abs':gnat_abs, 'gnat_perctg': gnat_percentage, \
     'response_time_partner':him_response_time, 'reponse_time_me': me_response_time, 'valid word count by me':average_valid_outgoing_length, \
     'valid word count by partner':average_valid_incoming_length, 'valid word ratio': average_valid_incoming_length/(average_valid_outgoing_length+0.00001)}, ignore_index=True)
    
    return pd_master

def label_conversation_initiation(x,nr_incoming_again_Index, guy_initiation_index, girl_initiation_index, nr_outgoing_again_Index):
    if x in nr_incoming_again_Index:
        return "NR_INCOM"
    elif x in guy_initiation_index:
        return "INCOM"
    elif x in nr_outgoing_again_Index:
        return "NR_OUTGO"
    elif x in girl_initiation_index:
        return "OUTGO"
    else:
        return "REPLY"


def generate_master_summary(pd_text):
    #this is where you get the function
    pd_text=date_processing(pd_text)
    
    pd_text=add_block_conv(pd_text)
    pd_text['index_holder'] = range(0, len(pd_text))
    first_conversation=pd_text.groupby(['block_conv']).first()
    all_potential_initiation=first_conversation['index_holder'].values.tolist()
    nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index=\
    summary_initiation_count(pd_text, all_potential_initiation)
    list_of_entire_text=generate_daily_text_group(pd_text)
    all_dates=pd_text['Message_Day'].drop_duplicates()
    
    #checking this sentiment changes
    #maybe we dont need this anymore
    
    text_info=bert_sentiment(list_of_entire_text)
    text_info_sentiment=[x[1] for x in text_info]
    
    #text_info_sentiment=len(all_dates)*[1]
    text_sentiment_pair=list(zip(all_dates,text_info_sentiment ))
    
    #special keywords
    custom_stopwords=identify_custom_stopwords(list_of_entire_text)
    pd_master=pd.DataFrame(columns=['Date', 'Start Time', 'End Time', 'Text sent by Me', 'Text Sent by partner', 'raw ratio', 'adjusted text ratio','word count by me', 'word count by partner', 'word ratio', 'Total Text', 'Initiator', 'Ender',
                                    'initiate with new topic', 'Emoji_partner','Emoji_me', 'Attachment_partner','Attachment_me', 'Topic', 'Response',\
                                    'adjust_word_ratio', 'total_minutes_partner', 'total_minutes_me', 'hours_in_touch_partner', 'hours_in_tough_me', 'gnat_abs', \
                                    'gnat_perctg', 'response_time_partner', 'reponse_time_me', 'valid word count by me', 'valid word count by partner', 'valid word ratio',])

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
                                        text_sentiment_pair, custom_stopwords)
        
    return pd_master, nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index



def summary_analytical(pd_text, pd_master,file_name,nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index):
    all_figure=[]
    file_name=file_name+".pdf"
    pdf = matplotlib.backends.backend_pdf.PdfPages(file_name)

    # sent message ratip
    incoming_msg_count,outgoing_msg_count,fig=count_number_of_incoming_outcoming(date_processing(pd_text),pd_master, to_graph=True)
    all_figure.append(fig)
    
    #total words
    pd_master.loc[pd_master['valid word count by me']==0,'valid word count by me']=1 
    pd_master.loc[pd_master['word count by me']==0,'word count by me']=1 

    pd_master['valid_word_rolling_ratio']=pd_master['valid word count by partner']/pd_master['valid word count by me']
    pd_master['valid_word_rolling_ratio']=pd_master['valid_word_rolling_ratio'].rolling(7).median()    
    pd_master['word_rolling_ratio']=pd_master['word count by partner']/pd_master['word count by me']
    pd_master['word_rolling_ratio']=pd_master['word_rolling_ratio'].rolling(7).median()    

    fig2, axs = plt.subplots(2,sharex=True, squeeze=True)
    axs[0].plot(pd_master['Date'], pd_master['word count by me'].rolling(7).mean(), '-r', label='me')
    axs[0].plot(pd_master['Date'], pd_master['word count by partner'].rolling(7).mean(),'-b', label='partner')
    leg = axs[0].legend();
    axs[0].set_title('Avg words by partner vs Avg words by me')
    axs[1].plot(pd_master['Date'], pd_master['word_rolling_ratio'],'-r', label='normal ratio')
    axs[1].plot(pd_master['Date'], pd_master['valid_word_rolling_ratio'],'-b', label='valid words only ratio')
    leg = axs[1].legend();
    axs[1].set_title('Rolling Word Ratio - by Partner / by Me ')
    fig2.autofmt_xdate()
    all_figure.append(fig2)
    
    #2b hours
    pd_master.loc[pd_master['total_minutes_me']==0,'total_minutes_me']=1 
    pd_master['minutes_ratio']=pd_master['total_minutes_partner']/pd_master['total_minutes_me']
    pd_master['minutes_ratio']=pd_master['minutes_ratio'].rolling(7).median()
    pd_master.loc[pd_master['minutes_ratio']==0, 'minutes_ratio']=1
    

    #2c hours in talk
    pd_master['hours_in_touch_ratio']=pd_master['hours_in_touch_partner']/(pd_master['hours_in_tough_me'])
    pd_master['hours_in_touch_ratio']=pd_master['hours_in_touch_ratio'].rolling(7).mean()
    fig2c, axs = plt.subplots(2,sharex=True, squeeze=True)
    axs[0].plot(pd_master['Date'], pd_master['hours_in_tough_me'].rolling(7).mean(), '-r', label='me')
    axs[0].plot(pd_master['Date'], pd_master['hours_in_touch_partner'].rolling(7).mean(),'-b', label='partner')
    leg = axs[0].legend();
    axs[0].set_title('Hour points partner sends message vs hour points me send message')
    axs[1].plot(pd_master['Date'], pd_master['hours_in_touch_ratio'])
    axs[1].set_title('Rolling Hour Points Ratio - by Partner / by Me ')
    fig2c.autofmt_xdate()
    all_figure.append(fig2c)

    #new initiator chart
    first_conversation=pd_text.groupby(['block_conv']).first()
    initial_type=[]
    for x in first_conversation['index_holder']:
        initial_type.append(label_conversation_initiation(x,nr_incoming_again_Index, guy_initiation_index, girl_initiation_index, nr_outgoing_again_Index))
    first_conversation['initial_type']=initial_type
    initition_summary=first_conversation.groupby(['Message_Day', 'initial_type'])['Type'].count().unstack()
    initition_summary=initition_summary.fillna(0)
    
    initition_summary_columns=list(initition_summary.columns)
    if 'INCOM' not in initition_summary_columns:
        initition_summary['INCOM']=[0]*len(initition_summary)
    if 'NR_INCOM' not in initition_summary_columns:
        initition_summary['NR_INCOM']=[0]*len(initition_summary)
    if 'OUTGO' not in initition_summary_columns:
        initition_summary['OUTGO']=[0]*len(initition_summary)
    if 'NR_OUTGO' not in initition_summary_columns:
        initition_summary['NR_OUTGO']=[0]*len(initition_summary)

    fig3, axs = plt.subplots(2, 2)
    #axs.set_title('Breakdown of initiation type (rolling 7d)')
    axs[0, 0].plot(initition_summary.index, initition_summary.INCOM.rolling(7).sum())
    axs[0, 0].set_title('New Initiation from Partner')
    axs[0, 0].xaxis.set_visible(False)
    axs[0, 1].plot(initition_summary.index, initition_summary.NR_INCOM.rolling(7).sum(), 'tab:orange')
    axs[0, 1].set_title('Second Initiation from Partner')
    axs[0, 1].xaxis.set_visible(False)
    axs[1, 0].plot(initition_summary.index, initition_summary.OUTGO.rolling(7).sum(), 'tab:green')
    axs[1, 0].set_title('New Initiation from Me')
    axs[1, 1].plot(initition_summary.index, initition_summary.NR_OUTGO.rolling(7).sum(), 'tab:red')
    axs[1, 1].set_title('Second Initiation from Me')
    fig3.suptitle('Breakdown of initiation type (rolling 7d)',fontsize=18)
    fig3.autofmt_xdate()
    all_figure.append(fig3)
    
    #gnat tendency
    pd_master['rolling_gnat_perctg']=pd_master['gnat_perctg'].rolling(7).mean()
    fig3a = plt.figure()
    plt.plot(pd_master['Date'], pd_master['rolling_gnat_perctg'])
    plt.title('Text Gnat Tendency -- Percentage of conversations initiated repeatedly')
    fig3a.autofmt_xdate()
    all_figure.append(fig3a)

    #initiator
    him_initiation=nr_incoming_again_Index+guy_initiation_index
    her_initiation=girl_initiation_index+nr_outgoing_again_Index
    first_conversation=pd_text.groupby(['block_conv']).first()
    first_conversation=categorization_him_me(first_conversation,him_initiation,her_initiation)
    first_conversation_summary=first_conversation.groupby(['Message_Day']).mean()
    fig8 = plt.figure()
    plt.plot(first_conversation_summary.index, first_conversation_summary['initiation_score'].rolling(7).mean())
    plt.title('Partner Initiation of Conversation (Score)')
    fig8.autofmt_xdate()
    all_figure.append(fig8)

    #count emoji
    pd_master['total_attachment_him']=pd_master['Emoji_partner']+pd_master['Attachment_partner']
    pd_master['total_attachment_her']=pd_master['Emoji_me']+pd_master['Attachment_me']
    pd_master['total_attachment_him_average']=pd_master['total_attachment_him'].rolling(7).sum()
    pd_master['total_attachment_her_average']=pd_master['total_attachment_her'].rolling(7).sum()
    
    pd_master.loc[pd_master.total_attachment_her == 0, 'total_attachment_her'] = 1
    pd_master['mms_ratio']=pd_master['total_attachment_him_average']/pd_master['total_attachment_her_average']
    pd_master['mms_ratio']=pd_master['mms_ratio'].rolling(7).median()

    fig4c, axs = plt.subplots(2,sharex=True, squeeze=True)
    axs[0].plot(pd_master['Date'], pd_master['total_attachment_her_average'], '-r', label='me')
    axs[0].plot(pd_master['Date'], pd_master['total_attachment_him_average'],'-b', label='partner')
    leg = axs[0].legend();
    axs[0].set_title('No. of Multimedia Sent by Partner vs by Me')
    axs[1].plot(pd_master['Date'], pd_master['mms_ratio'])
    axs[1].set_title('Multimedia Send Ratio: by Partner / by Me')
    fig4c.autofmt_xdate()
    all_figure.append(fig4c)
    
    
    #count sentiment: maybe in the future
    #pd_master['raw_sentiment']=pd_master['Response'].apply(clean_sentiment)
    pd_master['rolling_response_sentiment']=pd_master['Response'].apply(float).rolling(7).mean()
    fig5 = plt.figure()
    plt.plot(pd_master['Date'], pd_master['rolling_response_sentiment'])
    plt.title('Conversation Sentiment Index - higher is better (beta version)')
    fig5.autofmt_xdate()
    all_figure.append(fig5)
    
    
    #holy grail
    pd_raw=add_block_conv(pd_text)
    fig6=holy_grail_analysis(pd_raw, method='normal', conversation_cutoff=5, rolling_avg=10)
    all_figure.append(fig6)
    
    
    pd_master['raw ratio'].replace(np.inf, 1, inplace=True)
    mms_ratio_mean=pd_master['mms_ratio'].mean()
    pd_master['mms_ratio'].replace(np.nan, mms_ratio_mean, inplace=True)
    
    pd_master['final_score']=pd_master['valid_word_rolling_ratio']+\
    pd_master['raw ratio']+pd_master['minutes_ratio']+pd_master['hours_in_touch_ratio']+\
    pd_master['mms_ratio']-pd_master['rolling_gnat_perctg']
    
    fig5d = plt.figure()
    plt.plot(pd_master['Date'], pd_master['final_score'], '-b',label='current' )
    plt.plot(pd_master['Date'], pd_master['final_score'].rolling(7).mean(), '-r', label='7d-average')
    plt.title('Final Quality Score (7d Avg)')

    leg = plt.legend();
    fig5d.autofmt_xdate()
    all_figure=[fig5d]+all_figure

    #finally all of them
    for fig in all_figure: ## will open an empty extra figure :(
        pdf.savefig( fig )
    pdf.close()

def stats_collections(direct_process=True):
    #a simple dashboard of the past text analysis##

    file_name = input("Enter your whatapp chat filename (ending in txt): ")
    outgoing_name = input("Please enter your whatsapp name: ")
    raw_data= master_preprocessing_script(file_name, outgoing_name)
        
    print ("finish processing")
    original_file_name=file_name
    
    pd_text=raw_data[['Message Date', 'Type','Text']]
    pd_master, nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index=\
    generate_master_summary(pd_text)
    #adjusting the adjusted text ratio for pd_master
    median_adjusted_ratio=pd_master['adjusted text ratio'].median()
    pd_master['adjusted text ratio']=pd_master['adjusted text ratio'].fillna(median_adjusted_ratio)
    pd_master.loc[pd_master['adjusted text ratio']>7, 'adjusted text ratio']=median_adjusted_ratio
    
    
    #initiation needs to be worked on
    #presentation and analytical needs to be worked on as well
    if '.txt' in file_name:
        file_name=file_name.replace('.txt', '_analytical.csv')
    else:
        file_name=file_name.replace('.csv', '_analytical.csv')
    
    pd_master.to_csv(file_name)
    
    file_name=file_name.replace('.csv', '')
    file_name="new_"+file_name
    summary_analytical(pd_text, pd_master,file_name, nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index)
    
if __name__ == "__main__":
    stats_collections()