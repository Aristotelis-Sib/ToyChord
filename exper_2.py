import requests
import random
import concurrent.futures
import time
from compare import compare_query


def return_node():
    rd = random.choice(addresses)
    return str(rd)

keys_values=[]

counter=0
with open('data/query.txt', 'r') as f:
    for f_line in f:
        line = f_line.rstrip()
        keys_values.append(line)
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
for data in keys_values:
    url="http://"+return_node()+"/db/q/"+data.replace(" ",'_')
    res = requests.get(url)
    results.append(res.text)
ttl_time=round(time.time()-start_time,3)
print("It took ",ttl_time ," sec to complete")
print("Read Througput is ",ttl_time/500)

print(results)
if (results==compare_query()):
    print("True same")
else:
    print("False")
