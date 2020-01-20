import json
from unidecode import unidecode
from os.path import isfile
import datetime
import string
import re
import matplotlib.pyplot as plt
from dateutil.rrule import rrule,DAILY,MONTHLY,YEARLY,WEEKLY
import random
path = 'data\\messages\\inbox\\AliseGilot_A6kYU9nD4A'
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

def decode(s):
    try:
        res = s.encode('latin1','ignore').decode('utf8')
    except:
        res = ''
    return res

def display_message_disparity(messages,start='1000-01-01',end='2100-01-01'):
    count = {}
    participants = []
    start = datetime.datetime.strptime(start,'%Y-%m-%d')
    end = datetime.datetime.strptime(end,'%Y-%m-%d')
    for msg in messages:
        if 'content' in msg:
            date = datetime.datetime.fromtimestamp(msg['timestamp_ms']/1000.0)
            if date < start:
                continue
            if date > end:
                break
            sampleTime = date.strftime('%Y-%m-%d')
            name = decode(msg['sender_name'])
            if not name in participants:
                participants.append(name)
            if not sampleTime in count:
                count[sampleTime] = {}
            if not name in count[sampleTime]:
                count[sampleTime][name]=0
            content = decode(msg['content'])
            contentNoPunct = content.translate(str.maketrans('', '', string.punctuation))
            words = contentNoPunct.strip(' ').split(' ')
            count[sampleTime][name] += len(words)
    time = sorted(list(count.keys()))
    differences = []
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
        differences.append(Acount-Bcount)
    plt.bar(range(len(time)),differences)
    plt.xticks(range(len(time)),time,rotation='vertical')
    plt.title(f'Graphe de la différence du nombre de mots de {participants[0]} - {participants[1]} par mois')
    plt.show()

def display_word_count(messages,start=None,end=None,sampleTime='day'):
    if not start:
        start = datetime.datetime.fromtimestamp(messages[0]['timestamp_ms']/1000.0)
    else:
        start = datetime.datetime.strptime(start,'%Y-%m-%d')
    if not end:
        end = datetime.datetime.fromtimestamp(messages[-1]['timestamp_ms']/1000.0)
    else:
        end = datetime.datetime.strptime(end,'%Y-%m-%d')
    count = {}
    for msg in messages:
        if 'content' in msg:
            date = datetime.datetime.fromtimestamp(msg['timestamp_ms']/1000.0)
            if date < start:
                continue
            if date > end:
                break
            sampleTime = date.strftime('%Y-%m')
            if not sampleTime in count:
                count[sampleTime] = 0
            content = decode(msg['content'])
            contentNoPunct = content.translate(str.maketrans('', '', string.punctuation))
            words = contentNoPunct.strip(' ').split(' ')
            count[sampleTime] += len(words)
    time = []
    for dt in rrule(MONTHLY,dtstart=start,until=end):
        time.append(dt.strftime("%Y-%m"))
    counts = [count[t] if t in count else 0 for t in time]

    plt.bar(time,counts)
    plt.xticks(range(len(time)),time,rotation='vertical')
    plt.show()

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

#display_word_count(data)
while True:
    word = str(input())
    print(search_keyword_random(data,word))

#while True:
#    print(random_message(data))
#    input()