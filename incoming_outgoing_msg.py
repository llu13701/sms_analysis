from matplotlib import pyplot as plt
import pandas as pd
from nlp_script import total_stopword,find_kneeling_point
import collections
import statistics

def count_total_incoming_outgoing_words(pd_text, no_stopwords=True, custom_stopwords=[]):
    outgoing_msg=pd_text[pd_text['Type']=='Outgoing'].Text.tolist()
    outgoing_msg= [x for x in outgoing_msg if str(x) != 'nan']
    incoming_msg=pd_text[pd_text['Type']=='Incoming'].Text.tolist()
    incoming_msg= [x for x in incoming_msg if str(x) != 'nan']
    
    if no_stopwords==False:
        outgoing_msg_word,incoming_msg_word,average_outgoing_length, average_incoming_length=\
        count_average_incoming_outcoming_length(outgoing_msg,incoming_msg)
        return outgoing_msg_word,incoming_msg_word,average_outgoing_length, average_incoming_length
    else:
        
        outgoing_msg_nostopwords=remove_stopwords_inlist(outgoing_msg, custom_stopwords)
        incoming_msg_nostopwords=remove_stopwords_inlist(incoming_msg, custom_stopwords)
        outgoing_msg_word_nostopwords,incoming_msg_word_nostopwords,average_outgoing_length_nostopwords, average_incoming_length_nostopwords=\
        count_average_incoming_outcoming_length(outgoing_msg_nostopwords,incoming_msg_nostopwords)
        return outgoing_msg_word_nostopwords,incoming_msg_word_nostopwords,average_outgoing_length_nostopwords,average_incoming_length_nostopwords



def count_average_incoming_outcoming_length(outgoing_msg,incoming_msg):
    outgoing_msg_word=len(" ".join(outgoing_msg).split(" "))
    incoming_msg_word=len(" ".join(incoming_msg).split(" "))
    #print ("incoming to outgoing word count is ", incoming_msg_word/outgoing_msg_word)
    
    try:
        average_outgoing_length=sum([len(x.split()) for x in outgoing_msg])/len(outgoing_msg)
    except:
        average_outgoing_length=0
    try:
        average_incoming_length=sum([len(x.split()) for x in incoming_msg])/len(incoming_msg)
    except:
        average_incoming_length=0
    return outgoing_msg_word,incoming_msg_word,average_outgoing_length, average_incoming_length


def identify_custom_stopwords(list_of_sentence):
    large_document=" ".join (list_of_sentence).split(" ")
    large_document=[x.lower() for x in large_document]
    counter=list(collections. Counter(large_document).items())
    counter=sorted(counter, key=lambda x: x[1], reverse=True)
    list_of_count=[x[1] for x in counter]
    list_of_count_shift_one=list_of_count[1:len(list_of_count)]
    list_of_count_shift_one.append(0)
    diff=[x-y for x, y in list(zip(list_of_count_shift_one,list_of_count))]
    one_stdev=statistics.mean(diff)-0.7*statistics.stdev(diff)
    diff_cutoff=len([x for x in diff if x < one_stdev])
    total_stopwords=[x[0] for x in counter[0:diff_cutoff]]
    return total_stopwords

def remove_stopwords_inlist(list_of_sentence,custom_stopwords):
    #adding the customized stopwords
    #wait here
    agg_stopwords=list(set(custom_stopwords+list(total_stopword)))
    outgoing_msg_nostopwords=[]
    for x in list_of_sentence:
        x_list=x.split(" ") 
        new_sentence=[]
        for word in x_list:
            if word.lower() not in agg_stopwords:
                new_sentence.append(word)
        outgoing_msg_nostopwords.append(" ".join(new_sentence))
    return outgoing_msg_nostopwords


def create_adjusted_sent_info(pd_text):
    """this is to adjust for cases of multiple incoming.outgoing message, for example, 1-2-1 vs 1-1-1-1 is different"""
    pd_adjusted_sent=pd.DataFrame(columns=['Message Date', 'Type', 'Count', 'total_words'])
    i=0
    while i < len(pd_text):
        type_a=pd_text.loc[i, 'Type']
        count=i+1
        try:
            total_words=len(pd_text.loc[i, 'Text'].split(" "))
        except:
            total_words=0
        
        while count < len(pd_text) and pd_text.loc[count, 'Type']==type_a and pd_text.loc[count, 'message_diff'] < 0.034: #2mins
            try:
                length_sentence=len(pd_text.loc[count, 'Text'].split(" "))
            except:
                length_sentence=0
            total_words=total_words+length_sentence
            count=count+1
        number_of_count_a=count-i
        pd_adjusted_sent=pd_adjusted_sent.append({'Message Date': pd_text.loc[i, 'Message Date'], 'Type': pd_text.loc[i, 'Type'], 'Count': number_of_count_a, 'total_words':total_words}, ignore_index=True)
        i=count
        
    #adjusting the pd so that it will have both interaction
    pd_final_adjusted_sent=pd.DataFrame(columns=['Message Date', 'Type', 'Count'])
    i=0
    original_target=pd_adjusted_sent.loc[0, 'Type']

    while i < len(pd_adjusted_sent):
        if pd_adjusted_sent.loc[i, 'Type'] not in ['Outgoing', 'Incoming']:
            pd_adjusted_sent.loc[i, 'Type']='Outgoing'
            print ("something wrong, change the text type")
        
        if pd_adjusted_sent.loc[i, 'Type']==original_target:
            pd_final_adjusted_sent=pd_final_adjusted_sent.append(pd_adjusted_sent.loc[i, ])
            i=i+1
        else:
            pd_final_adjusted_sent=pd_final_adjusted_sent.append({'Message Date': pd_final_adjusted_sent['Message Date'].iloc[len(pd_final_adjusted_sent)-1], 'Type': original_target, 'Count': 0, 'total_words': 0}, ignore_index=True)

        if original_target=='Incoming':
            original_target='Outgoing'
        else:
            original_target='Incoming'
    return pd_final_adjusted_sent


def message_ratio_ordered_adjusted(pd_adjusted_text, adjustment_type='Count'):
    """ordered message adjusted ratio"""
    pd_adjusted_text['count_shift']=pd_adjusted_text[adjustment_type].shift(periods=1)
    pd_adjusted_paired=pd_adjusted_text.loc[pd_adjusted_text.Type=='Outgoing', ]
    pd_adjusted_paired=pd_adjusted_paired[['Message Date',adjustment_type, 'count_shift']]
    pd_adjusted_paired.columns=['Message Date', 'Outgoing', 'Incoming']
    pd_adjusted_paired=pd_adjusted_paired.replace(0,0.00001)
    pd_adjusted_paired['Message Ratio']=pd_adjusted_paired['Incoming']/pd_adjusted_paired['Outgoing']
    incoming_to_outcoming=pd_adjusted_paired['Message Ratio'].median()
    return incoming_to_outcoming


def count_number_of_incoming_outcoming(pd_text,pd_master, to_graph=True):
    outgoing_msg_count=pd_text[pd_text['Type']=='Outgoing'].Text.count()
    incoming_msg_count=pd_text[pd_text['Type']=='Incoming'].Text.count()
    fig=''
    if to_graph:
        msg_count_rolling=pd_text.groupby(['Message_Day','Type']).count().Text.unstack(level=1)
        msg_count_rolling['adjusted_ratio']=pd_master['adjusted text ratio'].tolist()
        msg_count_rolling=msg_count_rolling.fillna(1)
        msg_count_rolling['adjusted_ratio']=msg_count_rolling['adjusted_ratio'].rolling(7).median()
        msg_count_rolling=msg_count_rolling.fillna(1)
        msg_count_rolling['Rolling_incoming']=msg_count_rolling['Incoming'].rolling(7).mean()
        msg_count_rolling['Rolling_outgoing']=msg_count_rolling['Outgoing'].rolling(7).mean()
        msg_count_rolling['incoming_outgoing_ratio']=msg_count_rolling['Incoming']/msg_count_rolling['Outgoing']
        msg_count_rolling['incoming_outgoing_ratio']=msg_count_rolling['incoming_outgoing_ratio'].rolling(7).mean()
        
        fig, axs = plt.subplots(2,sharex=True, squeeze=True)
        #index_range=range(0, len(msg_count_rolling.index))
        axs[0].plot(msg_count_rolling.index, msg_count_rolling.Rolling_incoming,'-b', label='partner')
        axs[0].plot(msg_count_rolling.index, msg_count_rolling.Rolling_outgoing,'-r', label='me')
        leg = axs[0].legend();
        axs[0].set_title('Avg Sent by Partner vs by Me (7d avg)')
        axs[1].plot(msg_count_rolling.index, msg_count_rolling.incoming_outgoing_ratio,'-b', label='normal ratio')
        axs[1].plot(msg_count_rolling.index, msg_count_rolling.adjusted_ratio,'-r', label='spatial-adjusted ratio')
        leg = axs[1].legend();
        fig.autofmt_xdate()
        axs[1].set_title('Ratio - Sent by Partner / by Me (7d avg)')

    #print ("Overall incoming to outgoing number of msg ratio is ", incoming_msg_count/outgoing_msg_count)
    return incoming_msg_count,outgoing_msg_count, fig