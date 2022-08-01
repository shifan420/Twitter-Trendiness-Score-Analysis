import requests
# import os
import json
import argparse
# import pandas as pd
# import spacy
# import re
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

def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth, stream=True)
    #print(response.status_code)
    with open("tweets.txt", "w") as file:
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                if json_response['data']['lang'] == 'en':
                    for i in list(json_response["data"]):
                        # if i == "id":
                        #     json_response["data"].pop(i)
                        # elif i == "lang":
                        #     if json_response["data"][i] == "en":
                        #         json_response["data"].pop(i)
                        #     else:
                        #         del json_response["data"] #still working on how to remove these empty curly braces, feel free to edit
                        if i == "created_at": #"2021-11-12T23:53:11.000Z"
                            json_response["data"][i] = json_response["data"][i].replace(':','-',1)
                            json_response["data"][i] = json_response["data"][i][::-1].replace(':','-',1)[::-1]
                            json_response["data"][i] = json_response["data"][i].replace('T','-',1)
                            json_response["data"][i] = json_response["data"][i].replace('.000Z','',1)
                    # json_file = json.dumps(json_response, indent=4, sort_keys=True)
                    timestamp = json_response['data']['created_at']
                    # text = json_response['data']['text']
                    text = json_response['data']['text'].splitlines()
                    text = ''.join(str(line) for line in text)
                    file.write(f"{timestamp}, {text}\n")
    file.close()
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text, 
            )
        )

def connect_to_json(filename):
    json_response = json.loads(open(filename, "r").read())
    with open("tweets.txt", "w") as file:
        if json_response['data']['lang'] == 'en':
                for i in list(json_response["data"]):
                    # if i == "id":
                    #     json_response["data"].pop(i)
                    # elif i == "lang":
                    #     if json_response["data"][i] == "en":
                    #         json_response["data"].pop(i)
                    #     else:
                    #         del json_response["data"] #still working on how to remove these empty curly braces, feel free to edit
                    if i == "created_at": #"2021-11-12T23:53:11.000Z"
                        json_response["data"][i] = json_response["data"][i].replace(':','-',1)
                        json_response["data"][i] = json_response["data"][i][::-1].replace(':','-',1)[::-1]
                        json_response["data"][i] = json_response["data"][i].replace('T','-',1)
                        json_response["data"][i] = json_response["data"][i].replace('.000Z','',1)
                # json_file = json.dumps(json_response, indent=4, sort_keys=True)
                timestamp = json_response['data']['created_at']
                text = json_response['data']['text']
                file.write(f"{timestamp}, {text}\n")
    file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str)
    args = parser.parse_args()
    if args.filename:
        connect_to_json(args.filename)
    else:
        url = create_url()
        timeout = 0
        while True:
            connect_to_endpoint(url)
            timeout += 1

if __name__ == "__main__":
    main()