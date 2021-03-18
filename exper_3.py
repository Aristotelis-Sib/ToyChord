import requests
import random
import concurrent.futures
import time
from compare import compare_requests


def return_node():
    rd = random.choice(addresses)
    return str(rd)

keys_values=[]

counter=0
with open('data/requests.txt', 'r') as f:
    for f_line in f:
        line = f_line.rstrip()
        data = line.split(',')
        keys_values.append(data)
        counter+=1

global addresses

def set_addresses():  # A function that returns current nodes in Chord
    global addresses
    url="http://192.168.1.1:5000/overlay"
    res=requests.post(url)
    global addresses
    addresses=res.text.split("~")[1].split("|")

set_addresses()

start_time=time.time()
results=[]
query_cntr=0
for data in keys_values:
    if data[0] == 'insert':
        url="http://"+return_node()+"/db/"+data[1].replace(" ",'_')
        res = requests.post(url, data=data[2])
    else:
        query_cntr+=1
        url="http://"+return_node()+"/db/q/"+data[1].replace(" ",'_')
        res = requests.get(url)
        results.append(res.text)

ttl_time=round(time.time()-start_time, 3)
print("It took ",ttl_time ," sec to complete")


wrong_cntr=0
for i in zip(results,compare_requests()):
    if i[0]!=i[1]:
        wrong_cntr+=1
        print("Wrong pair is ", i)
print("Wrong results are {} in {} queries thus: {} %".format(wrong_cntr,query_cntr,(wrong_cntr/query_cntr)*100))


