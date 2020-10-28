
from next_sentence_prediction import next_sentence_prediction

def count_nr_initiation_again(pd_text, all_potential_initiation, text_type='Outgoing'):
    """track situation where you repeatively initiated a conversation again"""
    nr_outgoing_again=0
    nr_outgoing_again_Index=[]
    for i in range(0, len(all_potential_initiation)):
        index_to_search=all_potential_initiation[i]
        if pd_text.loc[index_to_search, 'Type']==text_type:
            if index_to_search==0:
                nr_outgoing_again=nr_outgoing_again+1
                nr_outgoing_again_Index.append(index_to_search)
            elif pd_text.loc[index_to_search-1, 'Type']==text_type:
                nr_outgoing_again=nr_outgoing_again+1
                nr_outgoing_again_Index.append(index_to_search)
    return nr_outgoing_again_Index

def addition_initiation(pd_text, all_potential_initiation, analyzing_type): #incoming for guys initiation counts
    """where one ends and then the other party reponded the next morning"""
    guy_initiation_all_index=[]
    guy_initiation_real_index=[]
    for i in range(0, len(all_potential_initiation)):
        index_to_search=all_potential_initiation[i]
        if pd_text.loc[index_to_search, 'Type']==analyzing_type:            
            guy_initiation_all_index.append(index_to_search)
            all_list_content=pd_text.loc[index_to_search-5:index_to_search-1, 'Text'].tolist()
            all_list_content=[x for x in all_list_content if x==x]
            all_list_content=[x for x in all_list_content if not 'www.' in x]
            temp=index_to_search
            respond_msg=pd_text.loc[temp, 'Text']
            while not respond_msg==respond_msg:
                temp=temp+1
                respond_msg=pd_text.loc[temp, 'Text']
            all_list_content_master=". ".join(all_list_content)
            if 'www.' in respond_msg:
                is_reponse=False
            else:
                is_reponse=next_sentence_prediction(all_list_content_master,respond_msg)
            if is_reponse==False:
                guy_initiation_real_index.append(index_to_search)
            all_list_content.append(respond_msg)
    return guy_initiation_all_index,guy_initiation_real_index


def summary_initiation_count(pd_text, all_potential_initiation):
    nr_outgoing_again_Index= count_nr_initiation_again(pd_text, all_potential_initiation, text_type='Outgoing')
    all_potential_initiation=[x for x in all_potential_initiation if not x in nr_outgoing_again_Index]
    nr_incoming_again_Index= count_nr_initiation_again(pd_text, all_potential_initiation, text_type='Incoming')
    all_potential_initiation=[x for x in all_potential_initiation if not x in nr_incoming_again_Index]
    guy_initiation,guy_initiation_index= addition_initiation(pd_text, all_potential_initiation,'Incoming')
    all_potential_initiation=[x for x in all_potential_initiation if not x in guy_initiation]
    girl_initiation,girl_initiation_index= addition_initiation(pd_text, all_potential_initiation, 'Outgoing')
    return  nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index

def find_initiator_ender(pd_day_text):
    if pd_day_text['Type'][0]=='Incoming':
        initiator='partner'
    else:
        initiator='me'

    if pd_day_text['Type'][len(pd_day_text)-1]=='Incoming':
        ender='partner'
    else:
        ender='me'
    return initiator,ender

def identify_initiation_with_new_topic(initiator,initial_time_index, nr_incoming_again_Index,guy_initiation_index, nr_outgoing_again_Index, girl_initiation_index):
    """if this is a new topic. who is the initiator"""
    if initiator=='partner':
        if initial_time_index in nr_incoming_again_Index:
            new_topic=True
        elif initial_time_index in guy_initiation_index:
            new_topic=True
        else:
            new_topic=False

    else:
        if initial_time_index in nr_outgoing_again_Index:
            new_topic=True
        elif initial_time_index in girl_initiation_index:
            new_topic=True
        else:
            new_topic=False
    return new_topic



