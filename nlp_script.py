#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 21:07:05 2019

@author: louisalu

# to load the library and be used by all
"""
from math import ceil
import pandas as pd

import spacy
nlp = spacy.load("en_core_web_lg")
pd_echo_lib=pd.read_csv("common_text.csv")
pd_echo_lib=pd_echo_lib.fillna(0)


import re
nlp_name=spacy.load("en_core_web_lg")
wiki_string='https://en.wikipedia.org/wiki/'


def clean_string_master(string_name, lower_case=True, replace_dash=False):
    string_name=re.sub(r"[^a-zA-Z0-9]+", ' ', string_name)
    string_name=string_name.replace('b ', '')
    string_name=string_name.strip()
    if lower_case==True:
        string_name=string_name.lower()
    if replace_dash==True:
        string_name=string_name.replace("_", " ")  
    return string_name


country_list=['India','United States','Indonesia','Brazil','Pakistan','Nigeria','Bangladesh','Russia','Mexico','Japan','Philippines','Egypt','Ethiopia','Vietnam',
'Democratic Republic of the Congo','Germany','Iran','Turkey','France','United Kingdom','Thailand','Italy','South Africa','Tanzania','Myanmar','Kenya','South Korea',
'Colombia','Spain','Argentina','Algeria','Ukraine','Sudan','Uganda','Iraq','Poland','Canada','Morocco',
'Saudi Arabia','Uzbekistan','Malaysia','Peru','Afghanistan','Venezuela','Ghana',
'Angola','Nepal','Yemen','Mozambique','Ivory Coast','North Korea','Australia',
'Madagascar','Cameroon','Taiwan','Niger','Sri Lanka','Burkina Faso','Mali',
'Romania','Chile','Kazakhstan','Guatemala','Malawi','Zambia','Netherlands',
'Ecuador','Syria','Cambodia','Senegal','Chad','Somalia', 'Zimbabwe','Belgium',
'South Sudan','Rwanda','Guinea','Benin','Haiti','Tunisia','Bolivia','Cuba',
'Burundi','Greece','Czech Republic','Jordan','Dominican Republic','Portugal',
'Sweden','Azerbaijan','United Arab Emirates','Hungary','Belarus','Honduras',
'Israel','Tajikistan','Austria','Papua New Guinea','Switzerland','Sierra Leone',
'Togo','Hong Kong','Paraguay','Laos','Bulgaria','Serbia','Lebanon','Libya','El Salvador',
'Nicaragua','Kyrgyzstan','Turkmenistan','Denmark','Singapore','Finland','Central African Republic',
'Slovakia','Republic of the Congo','Norway','Costa Rica','Palestine','New Zealand',
'Ireland','Oman','Liberia','Kuwait','Panama','Croatia','Mauritania','Georgia','Uruguay',
'Eritrea','Bosnia and Herzegovina','Mongolia','Puerto Rico','Armenia', 'Albania','Lithuania',
'Jamaica','Moldova','Qatar','Namibia','The Gambia','Botswana','Gabon','Slovenia','North Macedonia',
'Lesotho','Latvia','Kosovo','Guinea-Bissau','Bahrain','East Timor','Trinidad and Tobago','Equatorial Guinea',
'Estonia','Mauritius','Eswatini','Djibouti','Fiji','Comoros','Cyprus','Guyana','Bhutan',
'Solomon Islands','Macau','Montenegro','Luxembourg','Western Sahara ','Suriname','Cape Verde',
'Malta','Transnistria ','Brunei','Belize','Bahamas','Maldives','Iceland','Northern Cyprus ',
'Vanuatu','Barbados','New Caledonia','French Polynesia','Abkhazia ','Samoa','Saint Lucia',
'Guam','Curacao','Artsakh ','Kiribati','Aruba','Grenada','Saint Vincent and the Grenadines',
'Jersey(UK)','United States Virgin Islands','Federated States of Micronesia','Tonga',
'Antigua and Barbuda','Seychelles','Isle of Man','Andorra','Dominica','Cayman Islands','Bermuda',
'Guernsey','American Samoa','Northern Mariana Islands','Greenland','Marshall Islands',
'South Ossetia ','Saint Kitts and Nevis','Faroe Islands','Turks and Caicos Islands',
'Sint Maarten','Liechtenstein','Monaco','Saint-Martin','Gibraltar','San Marino',
'British Virgin Islands','Palau','Cook Islands','Anguilla','Wallis and Futuna','Nauru', 'Tuvalu','Saint Pierre and Miquelon','Saint Helena Ascension','Tristan da Cunha',
'Montserrat','Falkland Islands','Christmas Island','Norfolk Island','Niue','Tokelau',
'Vatican City','Cocos Islands','Pitcairn Islands']

us_state_abbrev = {
    'AL':'Alabama',
    'AK':'Alaska' ,
    'AZ':'Arizona',
    'AR':'Arkansas',
    'CA':'California',
    'CO':'Colorado',
    'CT':'Connecticut',
    'DE':'Delaware',
    'DC':'District of Columbia',
    'FL':'Florida',
    'GA': 'Georgia (U.S. state)',
    'HI':'Hawaii',
    'ID':'Idaho',
    'IL':'Illinois',
    'IN':'Indiana',
    'IA':'Iowa',
    'KS':'Kansas',
    'KY':'Kentucky',
    'LA':'Louisiana',
    'ME':'Maine',
    'MD':'Maryland',
    'MA':'Massachusetts',
    'MI':'Michigan',
    'MN':'Minnesota',
    'MS':'Mississippi',
    'MO':'Missouri',
    'MT':'Montana',
    'NE':'Nebraska',
    'NV':'Nevada',
    'NH':'New Hampshire' ,
    'NJ':'New Jersey' ,
    'NM':'New Mexico',
    'NY':'New York (state)',
    'NC':'North Carolina',
    'ND':'North Dakota',
    'MP':'Northern Mariana Islands',
    'OH':'Ohio',
    'OK':'Oklahoma',
    'OR':'Oregon',
    'PW':'Palau',
    'PA':'Pennsylvania',
    'PR':'Puerto Rico',
    'RI':'Rhode Island',
    'SC':'South Carolina',
    'SD':'South Dakota',
    'TN':'Tennessee',
    'TX':'Texas',
    'UT':'Utah',
    'VT':'Vermont',
    'VI':'Virgin Islands',
    'VA':'Virginia',
    'WA':'Washington (state)',
    'WV':'West Virginia',
    'WI':'Wisconsin',
    'WY':'Wyoming',
}

Cat_entertain=['tv', 'show', 'shows', 'drama', 'media', 'television',
               'network', 'series', 'trailer', 'cast', 'casting','studio', 'album',
               'track','song', 'songs', 'albums', 'concert', 'singer','band', 'movies',
              'actress','actresses', 'actor','actors', 'dancer', 'film', 'rotten tomatoes', 'video', 'videos',
              'imdb', 'movie', 'entertainment', 'pictures', 'thriller', 'directed',
              'documentary', 'story', 'stories', 'official movie', 'starring', 'prime video',
              'watch', 'review', 'book', 'ebook', 'goodreads', 'readers', 
              'bestseller', 'bestselling', 'paperback', 'novel', 'read', 'summary',
              'characters', 'amazon.com', 'broadway', 'play', 'theater',
              'box office', 'tickets', 'sparknotes', 'chapter', 'summaries', 
              'quotes', 'game', 'card game', 'deck', 'frictional', 'hasbro', 'board game',
              'producers', 'watch', 'watched', 'season', 'finales', 'finale', 'seasons', 'premier',
              'albums', 'album', 'recorded', 'music']


cat_agg_list_single=['politics', 'law', 'government',  'humanities', 'recreation',
              'life', 'relationship', 'self', 'science', 'technology', 'engineering', 'mathematics', 
              'sports', 'travel', 'literature', ' languages', 'home', 'electronics',
              'business','finance', 'work',  'art', 'fashion', 'medicine healthcare',
              'food', 'cooking', 'education', 'news', 'entertainment', 'pop culture', 'concepts', 'award']   
cat_agg_list_single=[s.replace('\u200e', '') for s in cat_agg_list_single]


cat_agg_list=['politics law government judiciary', 'humanities',
              'life relationship self', 'science technology engineering mathematics', 
              'recreation sports travel activities', 'literature languages communication',
              'business work careers', 'art design style', 'medicine healthcare',
              'food cuisines cooking', 'education schools learning', 
              'news entertainment pop culture', 'major concepts', 'honors recognition']        
cat_agg_list=[s.replace('\u200e', '') for s in cat_agg_list]

B=['Wikipedia:', 'Talk:', 'Category:','Help:','Main Page','All-1to10', '(disambiguation)',
   'Wikipedia talk:', 'File talk:', 'Portal:', 'Template:', 'Module talk:', 'Wikipedia', 
   'NONE', 'NONE999', 'don (tv series)', 'MediaWiki:', 'Help talk:', 'User:']
blacklist = re.compile('|'.join([re.escape(word) for word in B]))


text_file = open("total_stopword.txt", "r")
total_stopword = text_file.read().split('\n')
total_stopword=set(total_stopword[0:(len(total_stopword)-1)])
wiki_string='https://en.wikipedia.org/wiki/'


def flat_list_of_list(list_of_list):
    if len(list_of_list)==0:
        return list_of_list
    elif isinstance(list_of_list[0], list):
        return [sublist for x in list_of_list for sublist in x]
    else:
        return list_of_list


def find_kneeling_point(list_of_count, curve='concave', direction='increasing'):
    if len(list_of_count)==0:
        return 0
    if max(list_of_count)==min(list_of_count):
        return list_of_count[0]-1
    y=list_of_count
    x=list(range(0, len(y)))
    try:
        kneedle = KneeLocator(x, y, S=1.0, curve=curve, direction=direction)
    except:
        try:
            kneedle = KneeLocator(x, y, S=1.0, curve='convex', direction=direction)
        except:
            return list_of_count[ceil(len(list_of_count)/2)-1]
    try:
        filtered_value=list_of_count[kneedle.knee-1]
    except:
        return 0
    return filtered_value



