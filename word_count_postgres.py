#1.Read tweet.txt file
from string import punctuation
import psycopg2
import pandas as pd

#creating data table
conn = psycopg2.connect("dbname=gb760 user=gb760")
cur = conn.cursor()
conn.commit()

cur.execute("SELECT * FROM Tweets_Table")
record = cur.fetchall()
df = pd.DataFrame(record)
cur_date = df.iloc[-1,0]
cur_hour = df.iloc[-1,1]
cur_min = df.iloc[-1,2]
cur_sec = df.iloc[-1,3]
row_list = []
for i in range(len(df)):
    if df.iloc[i,0] == cur_date and df.iloc[i,1] == cur_hour and df.iloc[i,2] == cur_min and df.iloc[i,3] <= 59:
        new_line = df.iloc[i]
        row_list.append(new_line)
    else:
        pass
new_df = pd.DataFrame(row_list)

def process_tweets(new_df,phrase):  
    text = ""
    for m in range(len(new_df)):
        text += new_df.iloc[m,4]
    for i in '!"#$%&()*+-,-./:;<=>?@“”[\\]^_{|}~':
        text = text.replace(i, " ") # replace special characters
        text = text.lower() # convert uppercase to lowercase
    count = text.count(phrase)       
    return count
#print(new_df)
        
import argparse
parser = argparse.ArgumentParser(description='Count word frequency')
parser.add_argument('--word', help='Take as input a word or phrase')
args = parser.parse_args() 
        
# run the main function
if __name__ == '__main__':  
    word_freq = process_tweets(new_df, args.word)
    if word_freq == 0:
        print('Not found')
    else:
        print('Current Time Frequency: %d' % word_freq)
