#1.Read tweet.txt file
from string import punctuation

def process_file(): 
    try: # open file and handle errors
        f = open("tweets.txt", "r",encoding='utf-8')
    except IOError as s:
        print(s)
        return None
    try: # read file and handle errors
        readtws = f.read()
    except:
        print("Read File Error!")
        return None
    f.close()  
    return readtws
    
#2.Processing the file，count the frequency of each words，and store them in word_freq
def process_tweets(readtws,phrase):  
    if readtws:
        word_freq = {}
        for i in '!"#$%&()*+-,-./:;<=>?@“”[\\]^_{|}~':
            readtws = readtws.replace(i, " ") # replace special characters
            readtws = readtws.lower() # convert uppercase to lowercase
        count = readtws.count(phrase)       
        return count
        
import argparse
parser = argparse.ArgumentParser(description='Count word frequency')
parser.add_argument('--word', help='Take as input a word or phrase')
args = parser.parse_args() 
        
# run the main function
if __name__ == '__main__':  
    readtws = process_file()
    word_freq = process_tweets(readtws, args.word)
    if word_freq == 0:
        print('Not found')
    else:
        print('Frequency: %d' % word_freq)
