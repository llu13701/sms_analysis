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
import statistics
import collections



'''
choices include:
#refer here: https://docs.python.org/3/library/datetime.html
%m/%d/%y, %I:%M:%S %p
%d/%m/%Y, %H:%M #%H is 24 hour
'''


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
16 Oct 2017, 11:36: %d %b %Y, %H:%M
'''

def input_into_list(file_name):
    a_file = open(file_name, "r")
    list_of_lists = []
    for line in a_file:
      stripped_line = line.strip()
      list_of_lists.append(stripped_line)
    a_file.close()
    return list_of_lists

list_of_date_format=input_into_list("date_format.csv")

def determine_right_dateformat(list_of_lists):
    right_date_format=[]
    for x in range(0, len(list_of_date_format)):
        date_format_to_try=list_of_date_format[x]
        for i in range(0, min(900, len(list_of_lists))):
            try:
                date_object=datetime.strptime(list_of_lists[i], date_format_to_try)
                right_date_format.append(date_format_to_try)
            except:
                i
                
    if len(right_date_format)==0:
        date_format_to_try=list_of_date_format[0]
    else:
        ctr = collections.Counter(right_date_format)
        date_format_to_try=ctr.most_common(1)[0][0]

            
    return date_format_to_try
                
    

def messenger_export_processing(file_name, my_name, special_removal=['']):
    list_of_lists=input_into_list(file_name)
    list_of_lists=[x for x in list_of_lists if not x in special_removal]
    date_format=determine_right_dateformat(list_of_lists)
    #try go find the first line with the date on
    print ("date_format for the file is ",date_format)
    date_flag=False
    for i in range(0, int(len(list_of_lists)/2)):
        try:                
            date_object=datetime.strptime(list_of_lists[i], date_format)
            date_flag=True
            break
        except:
            i
            
    if date_flag==True and i < int(len(list_of_lists)/2)-1:
        list_of_lists=list_of_lists[i:len(list_of_lists)]
    else:
        print ("something is wrong with the file")

    #first find the partner name
    ctr = collections.Counter(list_of_lists[0:min(2000, len(list_of_lists))])
    names=ctr.most_common(2)
    potential_names=[x[0] for x in names]
    scoring_similarlity=[difflib.SequenceMatcher(None,my_name,x).ratio() for x in potential_names]
    outgoing_name=potential_names[scoring_similarlity.index(max(scoring_similarlity))]
    incoming_name=[x for x in potential_names if not x==outgoing_name][0]
    
    cleaned_list_of_list=[]
    for i in range(0, len(list_of_lists)):
        check_item=list_of_lists[i]
        if check_item==outgoing_name:
            cleaned_list_of_list.append("Outgoing")
        elif check_item==incoming_name:
            cleaned_list_of_list.append("Incoming")
        else:
            try:
                datetime_object=datetime.strptime(check_item, date_format)
                cleaned_list_of_list.append(datetime_object)
            except:
                cleaned_list_of_list.append(check_item)
    
    i=0
    pd_conv=pd.DataFrame(columns=['Message Date','Type','Text'])
    print ("cleaning messanger data")
    while i < len(cleaned_list_of_list):
        x=cleaned_list_of_list[i]
        if isinstance(x, datetime):
            inserted_date=x.strftime('%Y-%m-%d %H:%M:%S')
            i=i+1
            if i<len(cleaned_list_of_list):
                message_type=cleaned_list_of_list[i]
                i=i+1
                text=''
                while i<len(cleaned_list_of_list) and isinstance(cleaned_list_of_list[i], datetime)==False:
                    text=text+cleaned_list_of_list[i]
                    i=i+1
                pd_conv=pd_conv.append({'Message Date':inserted_date, 'Type': message_type, 'Text': text}, ignore_index=True)
        else:
            i=i+1
            #print ("first line: ",cleaned_list_of_list[i], " is not a date")
           
    pd_conv=pd_conv.sort_values(by=['Message Date'])
    pd_conv=pd_conv.reset_index(drop=True)
    file_name=file_name.replace(".txt", ".csv")
    pd_conv.to_csv(file_name)
    return pd_conv

        
        
def whatapp_export_processing(file_name, my_name):
    """this is the whatspp direct download, file name by default is _chat.txt"""
    list_of_lists=input_into_list(file_name)
    list_of_lists=list_of_lists[1:]
    pd_conv=pd.DataFrame()
    
    #checking split symbol
    if '[' in list_of_lists[0][0:9]:
        split_symbol=']'
    else:
        split_symbol=' - '
    
    first_split=[x.split(split_symbol) for x in list_of_lists]

    date_time_list=[x[0].replace("[", "").strip() for x in first_split]
    date_time_list=[x.replace("\u200e", "") for x  in date_time_list]    
    date_format=determine_right_dateformat(date_time_list)
    print ("file date_format is ", date_format)
    
    final_first_split=[]
    for i in range(0, len(first_split)):
        try:
            datetime.strptime(first_split[i][0].replace("[", "").strip(), date_format).strftime('%Y-%m-%d %H:%M:%S')
            final_first_split.append(first_split[i])
        except:
            i
    
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

def master_preprocessing_script(file_name, my_name, special_removal=['']):
    if 'message' in file_name.lower():
        print ("identified as messengers file: try messengers preprocessing")
        pd_conv= messenger_export_processing(file_name, my_name,special_removal)
    else: 
        try:
            print ("try whatsapp processing")
            pd_conv= whatapp_export_processing(file_name, my_name)
        except:
            print ("try messenger processing")
            pd_conv= messenger_export_processing(file_name, my_name,special_removal)

    return pd_conv
        



