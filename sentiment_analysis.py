
#from stanza.server import CoreNLPClient
from transformers import pipeline
from nlp_script import nlp_name
bert_nlp = pipeline("sentiment-analysis")

'''
def sentiment_analysis_list(list_of_entire_text):
    text_info=[] #include sentiment and ner recognition
    print ("preapring for sentiment analysis")
    with CoreNLPClient(
    annotators=['sentiment', 'pos'],
    memory='32G', be_quiet=True) as client:
        for i in range(0, len(list_of_entire_text)):
            print (i)
            msg=list_of_entire_text[i]
            ann = client.annotate(msg,properties={
                    'annotators': 'sentiment, pos',
                    'outputFormat': 'json',
                    })
            total_sentiment=[int(s["sentimentValue"]) for s in ann["sentences"]]
            try:
                #final_sentiment=(sum(total_sentiment)/len(total_sentiment))
                #final_sentiment=max(total_sentiment)
                final_sentiment=len([x for x in total_sentiment if x >2])/len(total_sentiment)
                
            except:
                final_sentiment=0
            text_info.append((msg,final_sentiment))
    return text_info
'''

def bert_sentiment(list_of_entire_text):
    sentiment_score=[]
    for sentence in list_of_entire_text:
        doc_prompt=nlp_name(sentence)
        prompt_sentence_list=[sent for sent in doc_prompt.sents]
        sentiment_total=[]
        for x in prompt_sentence_list:
            try:
                sentiment_total.append(bert_nlp(x.text)[0]['label'])
            except:
                sentiment_total.append('POSITIVE')
        neg_count=sentiment_total.count('NEGATIVE')
        pos_count=sentiment_total.count('POSITIVE')
        sentiment=(pos_count)/(neg_count+pos_count+0.001)
        sentiment_score.append((sentence,sentiment ))
    return sentiment_score



