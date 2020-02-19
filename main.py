import json
from unidecode import unidecode
from os.path import isfile
import datetime
import string
import re
import matplotlib.pyplot as plt
from dateutil.rrule import rrule,DAILY,MONTHLY,YEARLY,WEEKLY
import random
path = "TestData"
cache = []

def load_messages(path):
    global cache
    if cache:
        return cache
    data = []
    i=1
    while isfile(path + '\\message_'+str(i)+'.json'):
        with open(path + '\\message_'+str(i)+'.json') as d:
            data += json.load(d)['messages']
        i+=1
    cache = sorted(data, key=lambda message : message['timestamp_ms'])
    return cache

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

def decode(s):
    try:
        #res = unidecode(unicode(s,encoding='latin1'),decode='utf8')
        res = s.encode('latin1','ignore').decode('utf8')
    except:
        res = ''
    return res

def get_signature(timescale):
    if timescale == DAILY:
        return '%Y-%m-%d'
    if timescale == WEEKLY:
        return '%Y-%m-%w'
    if timescale == MONTHLY:
        return '%Y-%m'
    if timescale == YEARLY:
        return '%Y'
    raise ValueError('Timescale incorrect')

def plot_time(values,timescale,start,end,defaultValue = 0,title = ''):
    time = []
    signature = get_signature(timescale)
    for dt in rrule(timescale,dtstart=start,until=end):
        time.append(dt)
    Y = []
    for t in time:
        if t.strftime(signature) in values:
            Y.append(values[t.strftime(signature)])
        else:
            Y.append(defaultValue)
    fig,ax = plt.subplots()
    ax.bar(time,Y,width=10)
    fig.autofmt_xdate()
    #plt.xticks(range(len(time)),time,rotation='vertical')
    plt.title(title)
    plt.show()

def display_message_disparity(messages,start=None,end=None,sampleTime=MONTHLY):
    count = {}
    participants = []
    signature = get_signature(sampleTime)
    start,end = get_start_end(messages,start,end,signature)
    for msg in messages:
        if 'content' in msg:
            date = datetime.datetime.fromtimestamp(msg['timestamp_ms']/1000.0)
            if date < start:
                continue
            if date > end:
                break
            sample = date.strftime(signature)
            name = decode(msg['sender_name'])
            if not name in participants:
                participants.append(name)
            if not sample in count:
                count[sample] = {}
            if not name in count[sample]:
                count[sample][name]=0
            content = decode(msg['content'])
            contentNoPunct = content.translate(str.maketrans('', '', string.punctuation))
            words = contentNoPunct.strip(' ').split(' ')
            count[sample][name] += len(words)
    time = sorted(list(count.keys()))
    differences = {}
    for t in time:
        A = participants[0]
        B = participants[1]
        sample = count[t]
        if A in sample:
            Acount = sample[A]
        else:
            Acount = 0
        if B in sample:
            Bcount = sample[B]
        else:
            Bcount = 0
        differences[t]=(Acount-Bcount)
    plot_time(differences,sampleTime,start,end)
def get_start_end(data,start,end,signature):
    if not start:
        start = datetime.datetime.fromtimestamp(data[0]['timestamp_ms']/1000.0)
    else:
        start = datetime.datetime.strptime(start,signature)
    if not end:
        end = datetime.datetime.fromtimestamp(data[-1]['timestamp_ms']/1000.0)
    else:
        end = datetime.datetime.strptime(end,signature)
    return(start,end)


def display_word_count(messages,start=None,end=None,sampleTime=MONTHLY):
    signature = get_signature(sampleTime)
    start,end = get_start_end(messages,start,end,signature)
    count = {}
    for msg in messages:
        if 'content' in msg:
            date = datetime.datetime.fromtimestamp(msg['timestamp_ms']/1000.0)
            if date < start:
                continue
            if date > end:
                break
            sample = date.strftime(signature)
            if not sample in count:
                count[sample] = 0
            content = decode(msg['content'])
            contentNoPunct = content.translate(str.maketrans('', '', string.punctuation))
            words = contentNoPunct.strip(' ').split(' ')
            count[sample] += len(words)
    plot_time(count,sampleTime,start,end)

def total_word_count(messages):
    total = 0
    for msg in messages:
        if 'content' in msg:
            content = decode(msg['content'])
            contentNoPunct = content.translate(str.maketrans('', '', string.punctuation))
            words = contentNoPunct.strip(' ').split(' ')
            total += len(words)
    return total

def total_message_count(messages):
    return(len(messages))

def random_message(messages):
    flag = True
    while flag:
        msg = random.choice(messages)
        if 'content' in msg:
            flag = False
    return decode(msg['sender_name'] + ' : ' + msg['content'])

def most_used_words(messages,maxRank = 20,excluded=[],start=None,end=None):
    count = {}
    start,end = get_start_end(messages,start,end,get_signature(DAILY))
    for msg in messages:
        if 'content' in msg:
            date = datetime.datetime.fromtimestamp(msg['timestamp_ms']/1000.0)
            if date < start:
                continue
            if date > end:
                break
            content = deEmojify(decode(msg['content'])).lower()
            contentNoPunct = content.translate(str.maketrans('', '', string.punctuation))
            words = contentNoPunct.strip(' ').split(' ')
            for word in words:
                if word not in excluded:
                    if word in count:
                        count[word]+=1
                    else:
                        count[word] = 1
    
    #print(sorted([[key,value] for key,value in count.items()],key = lambda x: x[1],reverse=True)[:20])
    X,Y = [list(a) for a in zip(*sorted([[key,value] for key,value in count.items()],key = lambda x: x[1],reverse=True)) ]
    plt.bar(X[:maxRank],Y[:maxRank])
    plt.xticks(rotation=45, ha='right')
    plt.show()

def search_keyword_random(messages,keyword=None):
    match = []
    if not keyword:
        msg = random.choice(messages)
        content = decode(msg['content'])
        return decode(msg['sender_name']) + ' : ' + content
    for msg in messages:
        if 'content' in msg:
            content = decode(msg['content'])
            if keyword in content:
                match.append(decode(msg['sender_name']) + ' : ' + content)
    return random.choice(match)

data = load_messages(path)

#display_message_disparity(data)
#while True:
#    word = str(input())
#    print(search_keyword_random(data,word))

#while True:
#    print(random_message(data))
#    input()
mots = ['','je','a','pas','de','que','tu','mais','Je','le','en','et','la','me','un','te','du','des']
most_used_words(data,excluded=mots)