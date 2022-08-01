import psycopg2
import connection
import pandas as pd
import re

#read data from database tweets_info
connection = psycopg2.connect(dbname="gb760", user="gb760")  
cursor = connection.cursor()
connection.commit()
# Fetch result
cursor.execute("SELECT * from Tweets_Table")
record = cursor.fetchall()
df = pd.DataFrame(record)
#print("Result ", df)
cursor.close()
connection.close()
print("PostgreSQL connection was ran and closed")

#read tweets in the current minute
cur_m = df.iloc[-1,2]
cur_df = df.loc[df[2] == cur_m, [4]]
#cur_text = df[cur_df.columns[4]]
#print(cur_df)



count = 0
cur_l = cur_df.values

cur_l = re.sub('[\.][\.][\.]', '', str(cur_l))
cur_l = re.sub('\d+\s|\s\d+\s|\s\d+', '', str(cur_l))

for s in list(cur_l):
	s = str(s)
	s = set(s.split())
	
	un = len(s)
	
	count+=un

print ("Unique Words in Current Minute Are:")
print (cur_l)
print("Number of Unique Words is:",count)
#compute unique vocabulary from tweets contents

