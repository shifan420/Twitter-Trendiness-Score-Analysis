import psycopg2
import requests
import os
import pandas as pd
import spacy
import re
import multiprocessing
import time
from datetime import datetime
from kafka import KafkaConsumer
from json import loads
import json
from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'gb760',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     api_version=(0,11,5),
     group_id='my-group',
     value_deserializer=lambda x: x.decode('utf-8'))

#for message in consumer:
    #print(message)
    
conn = psycopg2.connect("dbname=gb760 user=gb760")
cur = conn.cursor()

results = []
tweets = []


def process_data():        
        
    for message in consumer:
        
        content = json.loads(mseeage) #"load" -- converting to json  #data receiving from producer
        if content["data"]["lang"] == "en":
            results.append(content["data"])
            output_file = open("tweet_json_file.json","w")
            for dic in results:
                json.dump(dic,output_file)
                output_file.write("\n")
            time = str(content["data"]["created_at"][0:10]) + "-" + str(content["data"]["created_at"][11:19])
            text = str(content["data"]["text"])
            text = clean_text(text)
            tweet = time + ", " + text
            tweets.append(tweet)
            time_date = time[0:10]
            time_hour = time[11:13]
            time_min = time[14:16]
            time_sec = time[17:19]
            cur.execute('INSERT INTO Tweets_Table(CreationDate, CreationHour, CreationMinute, CreationSeconds, Text) VALUES (%s, %s, %s, %s, %s)', (time_date, time_hour, time_min, time_sec, text))
            conn.commit()


if __name__ == "__main__":
    process_data()

#Lack of datebase conf info 


