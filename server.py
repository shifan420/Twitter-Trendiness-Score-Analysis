# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 16:53:14 2021

@author: Romeel
"""

import requests
import os
import json
import pandas as pd
import spacy
import re
import multiprocessing

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
    
#Prepare for cleaning text 
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

def clean_text(text): 
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

# Open 'tweets.txt' to store formated time and tweets
formated_file = open("tweets.txt", "w", encoding='utf-8')
tweets = []

# Read from Twitter API and output a json file and a formated txt file
def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth, stream=True)
    print(response.status_code)
    print("Remaining rate limit: ", response.headers["x-rate-limit-remaining"])
    if response.status_code == 200:
        results = [] # A list to store multiple dictionaries(json response data)       
        for response_line in response.iter_lines(): # Generate a json string each time
            if response_line: # Parse the string and convert to a Python Dictionary.
                json_response = json.loads(response_line) 
                if json_response["data"]["lang"] == "en": # Append only English dictionary to a list
                    results.append(json_response["data"])                  
                    output_file = open("tweet_json_file.json", 'w')
                    for dic in results: # Dump each dictionary in the list to tweet_json_file.json
                        json.dump(dic, output_file) 
                        output_file.write("\n") # Show one dictionary per line
                    # Write formated data into tweets.txt                    
                    time = str(json_response["data"]["created_at"][0:10]) + "-" + str(json_response["data"]["created_at"][11:19].replace(':','-'))
                    text = str(json_response["data"]["text"])
                    text = clean_text(text)
                    tweet = time + ", " + text
                    tweets.append(tweet)
                    formated_file.write(tweet + "\n")
    # Handle "Too many request" errors               
    elif response.status_code == 429:       
        import time
        from datetime import datetime
        reset_time = response.headers["x-rate-limit-reset"]
        reset_time = int(reset_time)
        current_time = time.time()
        remaining_time = reset_time - current_time
        print("Reach rate limitation. Remaining time (seconds) to retry: ", remaining_time)
        time.sleep(remaining_time)
    # Handle other HTTPerrors and print the accroding status code      
    else: 
        raise HTTPError(
			"Request returned an error: {} {}".format(
			response.status_code, response.text, 
		    )
		)
# Read from specified json file and output a formated txt file			    
def readtweets(filename):
    tweetsList = []
    #Reading JSON file which contains multiple JSON document
    with open(filename) as f:
        for jsonObj in f:  #Load each object in the file to a list
            #print(jsonObj)
            try:
                tweetsDict = json.loads(jsonObj)
                tweetsList.append(tweetsDict)
            except:
                pass
                
    #Format each JSON Decoded Object and dump them to tweets.txt
    for i in range(len(tweetsList)):
        time = str(tweetsList[i]['created_at'][0:10]+ "-" +tweetsList[i]["created_at"][11:19].replace(':','-'))
        text = str(tweetsList[i]['text'])
        text = clean_text(text)
        tweets = time + ", " + text
        #json.dump(tweets, formated_file) 
        formated_file.write(tweets + "\n")


import argparse
parser = argparse.ArgumentParser(description='Read file or twitter API')
parser.add_argument('--filename', help='Take as input a file')
args = parser.parse_args() 

# Handle HTTPError, ConnectionError, and other Requested errors
def main():
    from requests.exceptions import ConnectionError,ReadTimeout,HTTPError,RequestException
    try:
        url = create_url()
        connect_to_endpoint(url)
    except HTTPError:
        print('Http error')
    except ConnectionError:
        print('Connection Error')
    except RequestException as e:
        print('Other errors')
        raise SystemExit(e)

# Read from Twitter API or a json file
if __name__ == "__main__":
    if args.filename:
        readtweets(args.filename)
    else:
        main()   
    
