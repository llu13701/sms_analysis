# For those who would like to get it run on the cloud, I have a website setup here: check out http://bluetick.group/

## sms_analysis

A stats analysis on how much you text to your friend. (Whatsapp only)

Step 0:
Collecting whatsapp chat message history. For details, please refer to this link: https://www.zapptales.com/en/how-to-export-whatsapp-chat-android-iphone-ios/
unzip the file

Step 1:
Run the simple_stats.py and the program will prompt you enter the text file and your name. The file needs to have at least 10 days of chatting history in order to generate the summary pdf report.

For a detailed overview on this project, refer to my medium article: https://medium.com/@luyilousia/improving-my-dating-life-one-text-analysis-at-a-time-a802cb8c2876

Required libraries for this project: <br />
pandas <br />
matplotlib <br />
emoji <br />
spacy <br />
nltk <br />
collections <br />
transformers <br />
torch <br />

For Spacy, we need to download additional two libraries, by typing: <br />
python -m spacy download en_vectors_web_lg <br />
python -m spacy download en_core_web_lg <br />

Current version only works for Whatsapp US. If there are languages other than English, the sentiment and the initiation score could be off. 

If you run into any questions, email me at luyilousia@gmail.com
