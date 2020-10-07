from matplotlib import pyplot as plt
import pandas as pd

def count_total_incoming_outgoing_words(pd_text):
    outgoing_msg=pd_text[pd_text['Type']=='Outgoing'].Text.tolist()
    outgoing_msg= [x for x in outgoing_msg if str(x) != 'nan']
    incoming_msg=pd_text[pd_text['Type']=='Incoming'].Text.tolist()
    incoming_msg= [x for x in incoming_msg if str(x) != 'nan']

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
    #print ("average number of word per incoming to outgoing word is ", average_incoming_length/average_outgoing_length)

    return outgoing_msg_word,incoming_msg_word,average_outgoing_length, average_incoming_length


def create_adjusted_sent_info(pd_text):
    """this is to adjust for cases of multiple incoming.outgoing message, for example, 1-2-1 vs 1-1-1-1 is different"""
    pd_adjusted_sent=pd.DataFrame(columns=['Message Date', 'Type', 'Count'])
    i=0
    while i < len(pd_text):
        type_a=pd_text.loc[i, 'Type']
        count=i+1
        while count < len(pd_text) and pd_text.loc[count, 'Type']==type_a and pd_text.loc[count, 'message_diff'] < 0.034: #2mins
            count=count+1
        number_of_count_a=count-i
        pd_adjusted_sent=pd_adjusted_sent.append({'Message Date': pd_text.loc[i, 'Message Date'], 'Type': pd_text.loc[i, 'Type'], 'Count': number_of_count_a}, ignore_index=True)
        i=count
    #adjusting the pd so that it will have both interaction
    pd_final_adjusted_sent=pd.DataFrame(columns=['Message Date', 'Type', 'Count'])
    i=0
    original_target=pd_adjusted_sent.loc[0, 'Type']

    while i < len(pd_adjusted_sent):
        if pd_adjusted_sent.loc[i, 'Type']==original_target:
            pd_final_adjusted_sent=pd_final_adjusted_sent.append(pd_adjusted_sent.loc[i, ])
            i=i+1
        else:
            pd_final_adjusted_sent=pd_final_adjusted_sent.append({'Message Date': pd_final_adjusted_sent['Message Date'].iloc[len(pd_final_adjusted_sent)-1], 'Type': original_target, 'Count': 0}, ignore_index=True)

        if original_target=='Incoming':
            original_target='Outgoing'
        else:
            original_target='Incoming'
    return pd_final_adjusted_sent


def message_ratio_ordered_adjusted(pd_adjusted_text):
    """ordered message adjusted ratio"""
    pd_adjusted_text['count_shift']=pd_adjusted_text['Count'].shift(periods=1)
    pd_adjusted_paired=pd_adjusted_text.loc[pd_adjusted_text.Type=='Outgoing', ]
    pd_adjusted_paired=pd_adjusted_paired.drop(['Type'], axis=1)
    pd_adjusted_paired.columns=['Message Date', 'Outgoing', 'Incoming']
    pd_adjusted_paired=pd_adjusted_paired.replace(0,0.00001)
    pd_adjusted_paired['Message Ratio']=pd_adjusted_paired['Incoming']/pd_adjusted_paired['Outgoing']
    incoming_to_outcoming=pd_adjusted_paired['Message Ratio'].median()
    return incoming_to_outcoming


def count_number_of_incoming_outcoming(pd_text, to_graph=True):
    outgoing_msg_count=pd_text[pd_text['Type']=='Outgoing'].Text.count()
    incoming_msg_count=pd_text[pd_text['Type']=='Incoming'].Text.count()
    fig=''
    if to_graph:
        msg_count_rolling=pd_text.groupby(['Message_Day','Type']).count().Text.unstack(level=1)
        msg_count_rolling=msg_count_rolling.fillna(0)
        msg_count_rolling['Rolling_incoming']=msg_count_rolling['Incoming'].rolling(7).mean()
        msg_count_rolling['Rolling_outgoing']=msg_count_rolling['Outgoing'].rolling(7).mean()
        msg_count_rolling['incoming_outgoing_ratio']=msg_count_rolling['Rolling_incoming']/msg_count_rolling['Rolling_outgoing']

        fig, axs = plt.subplots(2,sharex=True, squeeze=True)
        axs[0].plot(msg_count_rolling.index, msg_count_rolling.Rolling_incoming,'-b', label='send by him')
        axs[0].plot(msg_count_rolling.index, msg_count_rolling.Rolling_outgoing,'-r', label='send by me')
        leg = axs[0].legend();
        axs[0].set_title('Avg Incoming vs Avg Outgoing')
        axs[1].plot(msg_count_rolling.index, msg_count_rolling.incoming_outgoing_ratio)
        axs[1].set_title('Rolling Incoming/Outgoing Ratio')

    #print ("Overall incoming to outgoing number of msg ratio is ", incoming_msg_count/outgoing_msg_count)
    return incoming_msg_count,outgoing_msg_count, fig