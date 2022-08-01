import time
from time import sleep
import datetime
import argparse
parser = argparse.ArgumentParser(description='Count word frequency')
parser.add_argument('--word', help='Take as input a word or phrase')
args = parser.parse_args() 

#Read the tweets info table from database
from string import punctuation
import psycopg2
import pandas as pd
import connection

#read data from database tweets_info
connection = psycopg2.connect(dbname="gb760", user="gb760")  
cursor = connection.cursor()
connection.commit()
# Fetch result
cursor.execute("SELECT * from Tweets_Table") 
record = cursor.fetchall()
df = pd.DataFrame(record)

"""
cur_date = df.iloc[-1,0]
cur_hour = df.iloc[-1,1]
cur_min = df.iloc[-1,2]
cur_sec = df.iloc[-1,3]
"""
cur_list = []
pri_list = []


#return a list of words in the minute x
def list_c(lis):
	cur_date = lis[0]
	cur_hour = lis[1]
	cur_min = lis[2]
	for i in range(len(df)):
		if df.iloc[i,0] == cur_date and df.iloc[i,1] == cur_hour and df.iloc[i,2] == cur_min:
			new_line = df.iloc[i]
			cur_list.append(new_line)
		else:
			pass
	cur_df = pd.DataFrame(cur_list)
	return cur_df

#count the number of a certain word in a dataframe
def process_a_tweets(a_df,phrase):  
	text = ""
	for m in range(len(a_df)):
		text += a_df.iloc[m,4]
	for i in '!"#$%&()*+-,-./:;<=>?@“”[\\]^_{|}~':
		text = text.replace(i, " ") # replace special characters
		text = text.lower() # convert uppercase to lowercase
	count = text.count(phrase)       
	return count
    
#get a list words in the x-1 minute
def list_p(lis2):
	cur_date = lis2[0]
	cur_hour = lis2[1]
	cur_min = lis2[2]-1
	for i in range(len(df)):
		if df.iloc[i,0] == cur_date and df.iloc[i,1] == cur_hour and df.iloc[i,2] == cur_min-1:
			new_line1 = df.iloc[i]
			pri_list.append(new_line1)
		else:
			pass
	pri_df = pd.DataFrame(pri_list)
	return pri_df

"""
cursor.close()
connection.close()
"""

#total word in a dataframe
def process_tt(df3):
	text3 = ""
	for i3 in range(len(df3)):
        	text3 += df3.iloc[i3,4]
	for j3 in '!"#$%&()*+-,-./:;<=>?@“”[\\]^_{|}~':
        	text3 = text3.replace(j3, " ") # replace special characters
        	text3 = text3.lower() # convert uppercase to lowercase
	t3 = len(text3.split())     
	return t3

#unique word in the dataframe
def process_un(df3):
	text3 = ""
	for i3 in range(len(df3)):
		text3 += df3.iloc[i3,4]
	for j3 in '!"#$%&()*+-,-./:;<=>?@“”[\\]^_{|}~':
		text3 = text3.replace(j3, " ") # replace special characters
		text3 = text3.lower() # convert uppercase to lowercase
	l3 = set(text3.split())
	u3 = len(l3)     
	return u3



#Probability of seeing the phrases in current/prior minute
def Pro(f,v,t):
	p = (1 + f) / (v + t)
	return p
	

#trendiness score
import math
def trend(p1, p2):
	tre = math.log10(p1) - math.log10(p2)
	return tre
	


# run the main function

if __name__ == '__main__':  
	now = datetime.datetime.now()
	now_l = [now.day, now.hour, now. minute]
	cur_df = list_c(now_l)
	pri_df = list_p(now_l)
	word_c = process_a_tweets(cur_df, args.word) #word freq current
	word_p = process_a_tweets(pri_df, args.word) #word freq prior
	un_c = process_un(cur_df) #unique word current minute
	un_p = process_un(pri_df) #unique word prior minute
	tt_c = process_tt(cur_df) #total word current
	tt_p = process_tt(pri_df) #total word prior
	prob_c = Pro(word_c,un_c,tt_c)
	prob_p = Pro(word_p,un_p,tt_p)
	tre = trend(prob_c,prob_p)
	if word_c == 0:
    		print('Not found')
	else:
    		print('Trendiness Score = ', tre)
