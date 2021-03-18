import requests
import random
import time


def return_node():
    rd = random.choice(addresses)
    return str(rd)


keys_values = []

counter = 0
with open('data/insert.txt', 'r') as f:
    for f_line in f:
        line = f_line.rstrip()
        c = line.split(',')
        keys_values.append(c)
        counter += 1

global addresses


def set_addresses():  # A function that returns current nodes in Chord
    global addresses
    url = "http://192.168.1.1:5000/overlay"
    res = requests.post(url)
    global addresses
    addresses = res.text.split("~")[1].split("|")


set_addresses()
start_time = time.time()
for data in keys_values:
    data[0] = data[0].replace("/", "_")
    url = "http://" + return_node() + "/db/" + data[0].replace(" ", '_')
    res = requests.post(url, data=data[1])

ttl_time = round(time.time() - start_time, 3)
print("It took ", ttl_time, " sec to complete")
print("Througput is ", ttl_time / 500)
