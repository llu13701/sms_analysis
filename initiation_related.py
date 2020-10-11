import difflib

from nlp_script import clean_string_master, pd_echo_lib
from text_cleanup import clean_up_phrases_no_stopwords_no_short_letters_no_numeric
from stanza.server import CoreNLPClient
from quer_transformer import extract_keywords_with_rake
from next_sentence_prediction import next_sentence_prediction
question_words = ['who', 'what', 'when', 'where', 'why', 'how', 'is', 'does', 'do', 'is', 'can', 'does', 'do', 'are']

def matches(sentence, short_phrases, threshold=0.85):
    """fuzzy search to see if a substring fuzzy matches the short phrase and then just remove the substring"""
    lenth_of_short_phrases=len(short_phrases.split(" "))
    sentence=clean_string_master(sentence)
    sentence_list=sentence.split(" ")

    potential_list=[]
    phrase=''
    if len(sentence_list)>lenth_of_short_phrases: #if the sentence is longer
        for i in range(0, len(sentence_list)-lenth_of_short_phrases+1):
            potential_list.append(" ".join(sentence_list[i:i+lenth_of_short_phrases]))
    else:
        potential_list.append(sentence)

    matching_score_pair=[]
    for i in range(0, len(potential_list)):
        score=difflib.SequenceMatcher(None,potential_list[i],short_phrases).ratio()
        matching_score_pair.append((potential_list[i],score ))
        if max([x[1] for x in matching_score_pair]) > threshold:
            phrase=[x[0] for x in matching_score_pair if x[1]==max([x[1] for x in matching_score_pair])][0]
    return phrase


def cleaning_text_message(sentence, pd_echo_lib):
    """remove text that has very similar to common text"""
    abbrev=pd_echo_lib['Abbreviations'].tolist()
    in_sample_abbrv=[x for x in abbrev if x.lower() in sentence.lower().split(" ")]
    in_sample_abbrv=[x.lower() for x in in_sample_abbrv]
    sentence=" ".join([x for x in sentence.lower().split() if x not in in_sample_abbrv])

    short_phrases_list=pd_echo_lib['Meaning'].tolist()
    short_phrases_list=[x.lower() for x in short_phrases_list]

    phrases_to_remove=[]
    for x in short_phrases_list:
        phrases_to_remove.append(matches(sentence, x))

    phrases_to_remove=[x for x in phrases_to_remove if not x=='']
    phrases_to_remove=list(set(phrases_to_remove))
    phrases_to_remove.sort(key=lambda s: len(s), reverse=True)
    for i in range(len(phrases_to_remove)):
        sentence=sentence.replace(phrases_to_remove[i], '')
    return sentence


def identify_initiation_sentence(all_list_content, respond_msg):
    """identify whether the respond message is a initiatian"""
    """replaced by bert, not used anymore"""
    if not respond_msg==respond_msg:
        respond_msg=''

    non_initial_score=0
    initial_score=0
    last_sentence=all_list_content[len(all_list_content)-1]
    cleaned_last_sentence=clean_up_phrases_no_stopwords_no_short_letters_no_numeric(last_sentence)
    cleaned_respond_msg=clean_up_phrases_no_stopwords_no_short_letters_no_numeric(respond_msg)
    #length comes first
    if len(cleaned_respond_msg)< 3 and not cleaned_respond_msg.lower()=='hi':
        non_initial_score=non_initial_score+100
    #check out keywords to make sure that they are together
    respond_msg_short= cleaning_text_message(respond_msg, pd_echo_lib)
    all_list_content_master=". ".join(all_list_content)
    respond_msg_short=clean_up_phrases_no_stopwords_no_short_letters_no_numeric(respond_msg, False)
    all_list_content_master_clean=clean_up_phrases_no_stopwords_no_short_letters_no_numeric(all_list_content_master)
    #context understanding
    last_sentence_short= cleaning_text_message(last_sentence, pd_echo_lib)
    cleaned_last_sentence_list=last_sentence_short.split(" ")
    reponse_list=respond_msg_short.split(" ")
    any_overlapping_words=list(set(cleaned_last_sentence_list) & set(reponse_list))
    any_overlapping_words=[x for x in any_overlapping_words if not x=='']
    if len(any_overlapping_words)>0:
        non_initial_score=non_initial_score+2
    else:
        initial_score=initial_score+1
        
    #the rest is there
    if len(cleaned_last_sentence.split(" "))<5:
        initial_score=initial_score+1
    else:
        non_initial_score=non_initial_score+1
    #if the response is long, then it is more likely to be an initiation, vice se versa

    if len(cleaned_respond_msg.split(" "))>5:
        initial_score=initial_score+1
    else:
        non_initial_score=non_initial_score+1
    return initial_score, non_initial_score


def identify_whether_question(all_last_sentence):
    """given a list of sentence and their id, check if they are question or  not"""
    """obselete by using bert. but would like to keep it for future use"""
    sentence_status=[] #their id, content and also 1 as question
    coded_sentence=[]
    for i in range(0, len(all_last_sentence)):
        last_sentence=all_last_sentence[i][1]
        if last_sentence==last_sentence:
            if "?" in last_sentence[len(last_sentence)-3: len(last_sentence)]:
                sentence_status.append((all_last_sentence[i][0], all_last_sentence[i][1], 1))
                coded_sentence.append(all_last_sentence[i][0])
            elif "www." in last_sentence.lower():
                sentence_status.append((all_last_sentence[i][0], all_last_sentence[i][1], 0))
                coded_sentence.append(all_last_sentence[i][0])
            elif "http" in last_sentence.lower():
                sentence_status.append((all_last_sentence[i][0], all_last_sentence[i][1], 0))
                coded_sentence.append(all_last_sentence[i][0])
            elif "!" in last_sentence[len(last_sentence)-3: len(last_sentence)]:
                sentence_status.append((all_last_sentence[i][0], all_last_sentence[i][1], 0))
                coded_sentence.append(all_last_sentence[i][0])

            elif last_sentence.split(" ")[0].lower() in question_words:
                sentence_status.append((all_last_sentence[i][0], all_last_sentence[i][1],1))
                coded_sentence.append(all_last_sentence[i][0])
    #remove all the coded ones
    all_left_last_sentence=[x for x in all_last_sentence if not x[0] in coded_sentence ]
    with CoreNLPClient(
        annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref'],
        memory='32G', be_quiet=True) as client:
            for i in range(0, len(all_left_last_sentence)):
                last_sentence=all_left_last_sentence[i][1]
                if last_sentence==last_sentence:
                    ann = client.annotate(last_sentence,properties={
                            'annotators': 'parse',
                            'outputFormat': 'json',
                            #'timeout': 10000,
                            }
        )

                if ('SQ' or 'SBARQ') in ann['sentences'][len(ann['sentences'])-1]["parse"]==True:
                    sentence_status.append((all_left_last_sentence[i][0], all_left_last_sentence[i][1],1))
                else:
                    sentence_status.append((all_left_last_sentence[i][0], all_left_last_sentence[i][1],0))

    return sentence_status


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

#index to check [2, 3, 5, 6, 8, 9, 11, 13, 14, 16, 18, 19, 20, 21, 24, 26, 28, 30, 32, 34]
def addition_initiation(pd_text, all_potential_initiation, analyzing_type): #incoming for guys initiation counts
    """where one ends and then the other party reponded the next morning"""
    guy_initiation_all_index=[]
    guy_initiation_real_index=[]
    temp_matrix=[]
    for i in range(0, len(all_potential_initiation)):
        #print (i)
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
            
            #create temp  data here, to check quality
            all_list_content.append(respond_msg)
            if is_reponse==False:
                temp_matrix.append(("/".join(all_list_content), 1))
            else:
                temp_matrix.append(("/".join(all_list_content), 0))
            
    return guy_initiation_all_index,guy_initiation_real_index


def summary_initiation_count(pd_text, all_potential_initiation):
    nr_outgoing_again_Index= count_nr_initiation_again(pd_text, all_potential_initiation, text_type='Outgoing')
    all_potential_initiation=[x for x in all_potential_initiation if not x in nr_outgoing_again_Index]
    nr_incoming_again_Index= count_nr_initiation_again(pd_text, all_potential_initiation, text_type='Incoming')
    all_potential_initiation=[x for x in all_potential_initiation if not x in nr_incoming_again_Index]
    #all_last_sentence=[(all_potential_initiation[i], pd_text.loc[max(0, all_potential_initiation[i]-1), 'Text']) for i in range(0, len(all_potential_initiation))]
    #sentence_status= identify_whether_question(all_last_sentence)
    guy_initiation,guy_initiation_index= addition_initiation(pd_text, all_potential_initiation,'Incoming')
    all_potential_initiation=[x for x in all_potential_initiation if not x in guy_initiation]
    girl_initiation,girl_initiation_index= addition_initiation(pd_text, all_potential_initiation, 'Outgoing')
    return  nr_outgoing_again_Index,nr_incoming_again_Index, guy_initiation_index,girl_initiation_index


def find_initiator_ender(pd_day_text):
    if pd_day_text['Type'][0]=='Incoming':
        initiator='him'
    else:
        initiator='me'

    if pd_day_text['Type'][len(pd_day_text)-1]=='Incoming':
        ender='him'
    else:
        ender='me'
    return initiator,ender


def identify_initiation_with_new_topic(initiator,initial_time_index, nr_incoming_again_Index,guy_initiation_index, nr_outgoing_again_Index, girl_initiation_index):
    """if this is a new topic. who is the initiator"""
    if initiator=='him':
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

def identify_potential_initiation_point(pd_text):
    z_all_potential_initiation=pd_text[pd_text['message_diff_z_score']>2].index.tolist()
    hour_all_potential_initiation=pd_text[pd_text['message_diff']>1].index.tolist() 
    initial_day_index=pd_text['Message_Day'].drop_duplicates().index.tolist()
    all_potential_initiation=list(set(z_all_potential_initiation+hour_all_potential_initiation+initial_day_index))
    all_potential_initiation.sort()
    return all_potential_initiation


