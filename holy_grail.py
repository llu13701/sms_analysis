import numpy as np
from matplotlib import pyplot as plt


def extract_details_conv_on_block_number(block_info_ordered, pd_text, item_range=10):
    '''given the block number, aka, holy grail, go to pd_text and find date and initial conversation about it
    input: block_info_ordered is a np series that ix indexed with block number'''
    top_three_conversation=[]
    for i in range(0, min(item_range, len(block_info_ordered))):
        top_block_number=block_info_ordered.index[i]
        top_three_line=pd_text.loc[pd_text.block_conv==top_block_number, 'Text'][0:5]
        top_three_line=[x for x in top_three_line if x==x]
        date_of_conversation=pd_text.loc[pd_text.block_conv==top_block_number, 'Message Date'].iloc[0]
        top_three_line="/".join(top_three_line)
        top_three_conversation.append((date_of_conversation, top_three_line))
    return top_three_conversation


def add_block_conv(pd_text):
    """preprocessing to add holy grail conversation counts"""
    ###########ANALYZING OF HOLY GRAIL CONVERSATIONS###############
    #checking message blocks, tranverse through the list
    #block conversation means a series of back and forth more intense exchange of message,
    # vs the other style where its more slow stream base.  This is the highest quality of the conversations
    #flush conversations usually happened within couple miunutes
    #block_conv: a.k.a holy grail conversations
    #they are intense and fun and filled with energy
    pd_text['block_conv']=len(pd_text)*[0]
    for i in range(1, len(pd_text)):
        if pd_text.loc[i, 'message_diff_z_score']>2 or pd_text.loc[i, 'message_diff']>1:
            pd_text.loc[i, 'block_conv']= pd_text.loc[i-1, 'block_conv']+1
        else:
            pd_text.loc[i, 'block_conv']= pd_text.loc[i-1, 'block_conv']
    return pd_text

def scoring_holy_grail_normal(pd_text):
    block_quality_score=pd_text.groupby(['block_conv','Type']).count().Text.unstack(level=1)
    block_quality_score=block_quality_score.fillna(0)
    block_quality_score['interactive_score']=block_quality_score['Incoming']/block_quality_score['Outgoing']
    block_quality_score['final_interactive_score']=block_quality_score['Incoming']*block_quality_score['interactive_score']
    final_score=block_quality_score.final_interactive_score[~block_quality_score.final_interactive_score.isin([np.nan, np.inf, -np.inf])]
    final_score=final_score.sort_values(ascending=False)
    return final_score


def holy_grail_analysis(pd_text, method='naive', conversation_cutoff=30, rolling_avg=50):
    block_info=pd_text['block_conv'].value_counts()
    block_info=block_info.sort_index()
    block_info=block_info[block_info > conversation_cutoff]
    print ("there are total ", len(block_info), "holy grail conversations")
    print ("holy grail conversation stands for ", sum(block_info)/len(pd_text), " percentage of total diaologue")

    if method=='naive':
        #plot the conversation numbers
        fig, axs = plt.subplots(2, sharex=True, squeeze=True)
        rolling_mean=block_info.rolling(rolling_avg).mean()
        axs[0].plot(block_info.index, block_info.values)
        axs[0].set_title("holy grail conversation length")
        axs[1].plot(block_info.index, rolling_mean)
        axs[1].set_title("rolling avg holy grail conversation length")
        block_info_ordered=block_info.sort_values(ascending=False)
        top_three_conversation= extract_details_conv_on_block_number(block_info_ordered, pd_text)
        print ("Take a look at the top three conversations ", top_three_conversation)

    #6. holy grail v2: based on both quantity of total interaction but also ratio of incoming and outcoming msg
    #would want to score the block conversation based on interaction ratios:
    else:
        final_score=scoring_holy_grail_normal(pd_text)
        top_conversation= extract_details_conv_on_block_number(final_score, pd_text, item_range=10)
        print ("here are some of the top conversations: adjusted by iteraction ratio scores\n")
        print (top_conversation)
        fig, axs = plt.subplots(2, sharex=True, squeeze=True)
        final_score=final_score.sort_index()
        rolling_mean=final_score.rolling(rolling_avg).mean()
        axs[0].plot(final_score.index, final_score.values)
        axs[0].set_title('holy grail interactive score')
        axs[1].plot(final_score.index, rolling_mean)
        axs[1].set_title('rolling average holy grail interactive score')
    return fig