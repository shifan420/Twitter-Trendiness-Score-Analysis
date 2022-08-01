import psycopg2
import requests
import os
import json
import pandas as pd
import spacy
import re
import multiprocessing
import time
from datetime import datetime


bearer_token = "AAAAAAAAAAAAAAAAAAAAAPvIUgEAAAAAYT52qKny6B4Kg%2FcLZxGDMP%2FCQ%2BM%3DaUQwwWeeBgOAgfRtNs36d0ymOLCwtVhzgdr1skzZX1Ge3ANYYu"

def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream?tweet.fields=created_at,lang"

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

def clean_text(text): #open the file
    if type(text) != str:
        text = text.decode("utf-8")
    doc = re.sub(regex, '', text, flags=re.MULTILINE) # remove URLs
    doc = re.sub('@[^\s]+','',text)
    sentences = []
    for sentence in doc.split("\n"):
        if len(sentence) == 0:
            continue
        sentences.append(sentence)
    doc = nlp("\n".join(sentences))
    doc = " ".join([token.lemma_.lower().strip() for token in doc
                        if (not token.is_stop)
                            and (not token.like_url)
                            and (not token.lemma_ == "-PRON-")
                            and (not len(token) < 4)])
    return doc


a_file = open("tweets.txt", "w")
results = []
tweets = []
#creating data table
conn = psycopg2.connect("dbname=gb760 user=gb760")
cur = conn.cursor()

def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth, stream=True)
    #print(response.status_code)
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            if json_response["data"]["lang"] == "en":
                results.append(json_response["data"])
                output_file = open("tweet_json_file.json","w")
                for dic in results:
                    json.dump(dic,output_file)
                    output_file.write("\n")
                time = str(json_response["data"]["created_at"][0:10]) + "-" + str(json_response["data"]["created_at"][11:19])
                text = str(json_response["data"]["text"])
                text = clean_text(text)
                tweet = time + ", " + text
                tweets.append(tweet)
                time_date = time[0:10]
                time_hour = time[11:13]
                time_min = time[14:16]
                time_sec = time[17:19]
                cur.execute('INSERT INTO Tweets_Table(CreationDate, CreationHour, CreationMinute, CreationSeconds, Text) VALUES (%s, %s, %s, %s, %s)', (time_date, time_hour, time_min, time_sec, text))
                conn.commit()
                a_file.write(tweet + "\n")
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text, 
            )
        )

def main():
    url = create_url()
    timeout = 0
    while True:
        connect_to_endpoint(url)
        timeout += 1

def readtweets(filename):
    tweetsList = []
    with open(filename) as f:
        for jsonObj in f:  #Load each object in the file to a list
            #print(jsonObj)
            try:
                tweetsDict = json.loads(jsonObj)
                tweetsList.append(tweetsDict)
            except:
                pass

    #Format each JSON Decoded Object and write them to tweets.txt
    for i in range(len(tweetsList)):
        time = str(tweetsList[i]['created_at'][0:10]+ "-" +tweetsList[i]["created_at"][11:19].replace(':','-'))
        text = str(tweetsList[i]['text'])
        text = clean_text(text)
        tweets = time + ", " + text
        time_date = time[0:10]
        time_hour = time[11:13]
        time_min = time[14:16]
        time_sec = time[17:19]
        cur.execute('INSERT INTO Tweets_Table(CreationDate, CreationHour, CreationMinute, CreationSeconds, Text) VALUES (%s, %s, %s, %s, %s)', (time_date, time_hour, time_min, time_sec, text))
        conn.commit()
#json.dump(tweets, formated_file) 
        a_file.write(tweets + "\n")


import argparse
parser = argparse.ArgumentParser(description='Read file or twitter API')
parser.add_argument('--filename', help='Take as input a file')
args = parser.parse_args() 



if __name__ == "__main__":
    if args.filename:
        readtweets(args.filename)
    else:
        main()

