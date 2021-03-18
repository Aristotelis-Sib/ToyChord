import requests

print("Insert key-value pairs and the run query with *")

for i in range(6):
    url="http://192.168.1.2:5000/db/key {}".format(i)
    res=requests.post(url,data=str("v{}".format(i)).encode())    

url="http://192.168.1.1:5001/db/q/*"
res=requests.get(url)
print(res.text)

