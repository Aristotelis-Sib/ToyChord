import requests
import time
from threading import Thread, Lock

def show_data():
    url="http://192.168.1.1:5000/db/q/*"
    res=requests.get(url)
    print(res.text)
    print("\n")
    print("-"*100)
    print("\n")


show_data()

url="http://192.168.1.1:5000/overlay"
res=requests.post(url)
print(res.text)
print("-"*100)

