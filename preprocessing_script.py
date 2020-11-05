#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 20:33:02 2020


https://towardsdatascience.com/heres-how-you-can-access-your-entire-imessage-history-on-your-mac-f8878276c6e9

@author: louisalu
"""

import pandas as pd
from datetime import datetime
import difflib
import re




def convert_type(x, criterion=0):
    if x in criterion:
        return 'Incoming'
    else:
        return 'Outgoing'

'''
#couple popular date_format
#https://docs.python.org/3/library/datetime.html
%m/%d/%y, %I:%M:%S %p #this is 12 hours with am/pm. y=two digits year
%d/%m/%Y, %H:%M #%H is 24 hour
'''

def whatapp_export_processing(file_name, my_name, date_format='%d/%m/%Y, %H:%M'):
    """this is the whatspp direct download, file name by default is _chat.txt"""
    a_file = open(file_name, "r")
    list_of_lists = []
    for line in a_file:
      stripped_line = line.strip()
      list_of_lists.append(stripped_line)
    a_file.close()
    
    list_of_lists=list_of_lists[1:]
    pd_conv=pd.DataFrame()
    
    #checking split symbol
    if '[' in list_of_lists[0][0:9]:
        split_symbol='['
    else:
        split_symbol='-'
    
    first_split=[x.split(split_symbol) for x in list_of_lists]
    #check for validation for the first_split
    final_first_split=[]
    average_length=sum([len(x[0]) for x in first_split])/len(first_split)
    for i in range(0, len(first_split)):
        check_item=first_split[i][0]
        if abs(len(check_item)-average_length)<4:
            check_item=re.sub('[^A-Za-z0-9]+', '', check_item)
            numbers = sum(c.isdigit() for c in check_item)
            if numbers/(len(check_item)+0.0001)>0.45:
                final_first_split.append(first_split[i])
    
    first_split=final_first_split
    
    date_time_list=[x[0].replace("[", "").strip() for x in first_split]
    date_time_list=[x.replace("\u200e", "") for x  in date_time_list]    
    
    new_date_time_list=[]
    for i in range(len(date_time_list)):
        new_date_time_list.append(datetime.strptime(date_time_list[i], date_format).strftime('%Y-%m-%d %H:%M:%S'))
    
    pd_conv['Message Date']=new_date_time_list
    
    #checking types:
    second_split=[x[1:] for x in first_split]
    second_split=[x[0].split(":")for x in second_split]
    #final_Split
    final_split=[x[1:] for x in second_split]
    name_split=[x[0].strip() for x in second_split]
    potential_name=list(set(name_split))
    
    scoring_similarlity=[difflib.SequenceMatcher(None,my_name,x).ratio() for x in potential_name]
    outgoing_name=potential_name[scoring_similarlity.index(max(scoring_similarlity))]
    incoming_name=[x for x in potential_name if not x==outgoing_name]
    pd_conv['Type']=[convert_type(x, criterion=incoming_name) for x in name_split]
    
    final_split=[" ".join(x).strip() for x in final_split ]
    pd_conv['Text']=final_split
    
    file_name=file_name.replace(".txt", ".csv")
    pd_conv.to_csv(file_name)
    return pd_conv



