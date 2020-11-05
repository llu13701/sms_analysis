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

from incoming_outgoing_msg import count_total_incoming_outgoing_words, create_adjusted_sent_info, \
    message_ratio_ordered_adjusted, count_number_of_incoming_outcoming
from initiation_related import summary_initiation_count, find_initiator_ender, identify_initiation_with_new_topic
from sentiment_analysis import bert_sentiment
from topic_analysis import summary_topic, paragraph_summary

from datetime import datetime
import emoji
import matplotlib.backends.backend_pdf
from holy_grail import add_block_conv, holy_grail_analysis, scoring_holy_grail_normal
from preprocessing_script import whatapp_export_processing

#

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

    pd_day_text.reset_index(drop=True, inplace=True)
    attachment_number=len(all_incoming_msg)-len(all_incoming_msg_no_attachment)
    all_incoming_msg_no_link=all_incoming_msg_no_attachment[~all_incoming_msg_no_attachment.Text.str.contains('www.')]
    web_link=len(all_incoming_msg_no_attachment)-len(all_incoming_msg_no_link)
    attachment_number=attachment_number+web_link
    list_text=pd_day_text['Text'].values.tolist()
    list_text=[x for x in list_text if x==x]
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
     'Emoji_partner':emoji_count_him, 'Emoji_me':emoji_count_her, 'Response':sentiment}, ignore_index=True)
    
    return pd_master


def generate_master_summary(pd_text):
    #this is where you get the function
    pd_text=date_processing(pd_text)
    
    pd_text=add_block_conv(pd_text)
    pd_text['index_holder'] = range(0, len(pd_text))
    first_conversation=pd_text.groupby(['block_conv']).first()
    all_potential_initiation=first_conversation['index_holder'].values.tolist()
    nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index=\
    summary_initiation_count(pd_text, all_potential_initiation)
    pd_master=pd.DataFrame(columns=['Date', 'Start Time', 'End Time', 'Text sent by Me', 'Text Sent by partner', 'raw ratio', 'adjusted text ratio','word count by me', 'word count by partner', 'word ratio', 'Total Text', 'Initiator', 'Ender',
                                    'initiate with new topic', 'Emoji_partner','Emoji_me', 'Attachment_partner','Attachment_me', 'Topic', 'Response'])
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
        
    return pd_master, nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index



def summary_analytical(pd_text, pd_master,file_name,nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index):
    all_figure=[]
    file_name=file_name+".pdf"
    pdf = matplotlib.backends.backend_pdf.PdfPages(file_name)

    # sent message ratip
    incoming_msg_count,outgoing_msg_count,fig=count_number_of_incoming_outcoming(date_processing(pd_text), to_graph=True)
    all_figure.append(fig)
    #total words
    pd_master['total_word_by_me']=pd_master['word count by me'].rolling(7).mean()
    pd_master['total_word_by_him']=pd_master['word count by partner'].rolling(7).mean()
    pd_master['word_rolling_ratio']=pd_master['total_word_by_him']/pd_master['total_word_by_me']
    fig2, axs = plt.subplots(2,sharex=True, squeeze=True)
    axs[0].plot(pd_master['Date'], pd_master['total_word_by_me'], '-r', label='me')
    axs[0].plot(pd_master['Date'], pd_master['total_word_by_him'],'-b', label='partner')
    leg = axs[0].legend();
    axs[0].set_title('Avg words by partner vs Avg words by me')
    axs[1].plot(pd_master['Date'], pd_master['word_rolling_ratio'])
    axs[1].set_title('Rolling Word Ratio - by Partner / by Me ')
    fig2.autofmt_xdate()
    all_figure.append(fig2)

    #initiator
    him_initiation=nr_incoming_again_Index+guy_initiation_index
    her_initiation=girl_initiation_index+nr_outgoing_again_Index
    first_conversation=pd_text.groupby(['block_conv']).first()
    first_conversation=categorization_him_me(first_conversation,him_initiation,her_initiation)
    first_conversation_summary=first_conversation.groupby(['Message_Day']).mean()
    fig3 = plt.figure()
    plt.plot(first_conversation_summary.index, first_conversation_summary['initiation_score'].rolling(7).mean())
    plt.title('Partner Initiation of Conversation (Score)')
    fig3.autofmt_xdate()
    all_figure.append(fig3)
    
    #count emoji
    pd_master['total_attachment_him']=pd_master['Emoji_partner']+pd_master['Attachment_partner']
    pd_master['total_attachment_her']=pd_master['Emoji_me']+pd_master['Attachment_me']

    pd_master['total_attachment_him_average']=pd_master['total_attachment_him'].rolling(7).sum()
    pd_master['total_attachment_her_average']=pd_master['total_attachment_her'].rolling(7).sum()

    fig4 = plt.figure()
    plt.plot(pd_master['Date'], pd_master['total_attachment_him_average'],'-b', label='partner' )
    plt.plot(pd_master['Date'], pd_master['total_attachment_her_average'],'-r', label='me')
    fig4.autofmt_xdate()
    plt.title('No. of Multimedia Sent')
    leg = plt.legend()
    all_figure.append(fig4)

    #count sentiment
    #pd_master['raw_sentiment']=pd_master['Response'].apply(clean_sentiment)
    fig5 = plt.figure()
    plt.plot(pd_master['Date'], pd_master['Response'].apply(float).rolling(7).mean())
    plt.title('Conversation Sentiment Index - higher is better (beta version)')
    fig5.autofmt_xdate()
    all_figure.append(fig5)
    
    #holy grail
    pd_raw=add_block_conv(pd_text)
    fig6=holy_grail_analysis(pd_raw, method='normal', conversation_cutoff=5, rolling_avg=10)
    all_figure.append(fig6)
    
    #find topics for the holy grail:
    '''
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
    '''
    #finally all of them
    for fig in all_figure: ## will open an empty extra figure :(
        pdf.savefig( fig )
    pdf.close()

def stats_collections(direct_process=True ):
    #a simple dashboard of the past text analysis##
    #file_name='Messages.csv'

    file_name = input("Enter your whatapp chat filename (ending in txt): ")
    outgoing_name = input("Please enter your whatsapp name: ")

    if direct_process==True:
        raw_data=whatapp_export_processing(file_name, outgoing_name)
    else:   
        raw_data=pd.read_csv(file_name)
        
    original_file_name=file_name
    
    pd_text=raw_data[['Message Date', 'Type','Text']]
    pd_master, nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index=\
    generate_master_summary(pd_text)
    
    #initiation needs to be worked on
    #presentation and analytical needs to be worked on as well
    file_name=file_name.replace('.csv', '_analytical.csv')
    pd_master.to_csv(file_name)
    file_name=file_name.replace('.csv', '')
    summary_analytical(pd_text, pd_master,file_name, nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index)


    
    
    
if __name__ == "__main__":
    stats_collections()