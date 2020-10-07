#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 20:33:02 2020


https://towardsdatascience.com/heres-how-you-can-access-your-entire-imessage-history-on-your-mac-f8878276c6e9

@author: louisalu
"""

import ast
import sqlite3
import pandas as pd
from datetime import datetime
import difflib


#this is to convert from imessage to timestam
apple_beginninng=datetime(2001,1,1).timestamp()
unix_beginninng=datetime(1970,1,1).timestamp()
difference=apple_beginninng-unix_beginninng

def convert_apple_time(x):
    return datetime.fromtimestamp(x+difference).strftime('%Y-%m-%d %H:%M:%S')


# substitute username with your username
#file_name='imessage.db'
def extracting_db(file_name, ex_phone_number='15555555555'):
    """used for imessage downloaded directly from the backup file"""
    conn = sqlite3.connect(file_name)
    cur = conn.cursor()
    cur.execute(" select name from sqlite_master where type = 'table' ")     
    messages = pd.read_sql_query("select * from message", conn)
    handles = pd.read_sql_query("select * from handle", conn)
    messages.rename(columns={'ROWID' : 'message_id'}, inplace = True)
    handles.rename(columns={'id' : 'phone_number', 'ROWID': 'handle_id'}, inplace = True)
    merge_level_1 = pd.merge(messages[['text', 'handle_id', 'date','is_sent', 'message_id']],  handles[['handle_id', 'phone_number']], on ='handle_id', how='left')
    this_convo = merge_level_1.loc[merge_level_1.phone_number == ex_phone_number , ]
    file_name=file_name.replace(".db", ".csv")
    this_convo.to_csv(file_name)


def convert_type(x, criterion=0):
    if x==criterion:
        return 'Incoming'
    else:
        return 'Outgoing'

#reading the script
def preprocessing_script(file_name):
    """convert it into readable format for the official real text analyzer"""
    pd_raw=pd.read_csv(file_name+".csv")
    pd_raw['Type']=pd_raw['is_sent'].apply(convert_type)
    pd_raw['Message Date']=pd_raw['date'].apply(convert_apple_time)
    pd_raw=pd_raw.drop(['Unnamed: 0', 'handle_id', 'is_sent', 'message_id', 'date'], axis=1)
    pd_raw.columns=['Text', 'phone_number', 'Type', 'Message Date']
    pd_raw.to_csv(file_name+"_cleaned.csv")
    
    
#file_name='_chat.txt'

def whatapp_export_processing():
    """this is the whatspp direct download, file name by default is _chat.txt"""
    
    file_name = input("Enter the text file that you want to analysis, ending with .txt: ")
    outgoing_name = input("Please enter your whatsapp name: ")
    
    a_file = open(file_name, "r")
    list_of_lists = []
    for line in a_file:
      stripped_line = line.strip()
      list_of_lists.append(stripped_line)
    a_file.close()
    
    #doing the three tyoes
    list_of_lists=list_of_lists[1:]
    pd_conv=pd.DataFrame()
    first_split=[x.split("]") for x in list_of_lists]
    date_time_list=[x[0].replace("[", "").strip() for x in first_split]
    date_time_list=[x.replace("\u200e", "") for x  in date_time_list]    
    date_time_list=[datetime.strptime(x, '%m/%d/%y, %I:%M:%S %p').strftime('%Y-%m-%d %H:%M:%S') for x in date_time_list]
    pd_conv['Message Date']=date_time_list
    
    #checking types:
    second_split=[x[1:] for x in first_split]
    second_split=[x[0].split(":")for x in second_split]
    #final_Split
    final_split=[x[1:] for x in second_split]
    name_split=[x[0].strip() for x in second_split]
    potential_name=list(set(name_split))
    
    scoring_similarlity=[difflib.SequenceMatcher(None,outgoing_name,x).ratio() for x in potential_name]
    outgoing_name=potential_name[scoring_similarlity.index(max(scoring_similarlity))]
    incoming_name=[x for x in potential_name if not x==outgoing_name][0]
    pd_conv['Type']=[convert_type(x, criterion=incoming_name) for x in name_split]
    
    final_split=[" ".join(x).strip() for x in final_split ]
    pd_conv['Text']=final_split
    
    file_name=file_name.replace(".txt", "")
    file_name=incoming_name.replace(" ", "_")+file_name+".csv"
    pd_conv.to_csv(file_name)
    return pd_conv


if __name__ == "__main__":
    whatapp_export_processing()
