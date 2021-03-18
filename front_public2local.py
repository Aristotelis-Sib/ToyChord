from flask import Flask, render_template, url_for, flash, redirect, request
import requests
import time
import random
from hashlib import sha1

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
m = 160

global hashed_ips
hashed_ips = []


def get_hash(key):
    return int(int.from_bytes(sha1(key.encode()).digest(), byteorder='big') % 2 ** m)


def set_addresses():  # A function that returns current nodes in Chord
    url = "http://192.168.1.1:5000/overlay"
    res = requests.post(url)
    global addresses
    addresses = res.text.split("~")[1].split("|")


def random_addr():
    return random.choice(addresses)


@app.route("/nodes", methods=['GET', 'POST'])
def nodes():
    global hashed_ips
    set_addresses()
    ip_adds = addresses
    ids = []
    for i in ip_adds:
        ids.append(get_hash(i))  # Hashing ip_addresses:ports

    hashed_ips = list(zip(ids, ip_adds))
    hashed_ips = sorted(hashed_ips,
                        key=lambda x: x[0])  # a list of IDs in increasing order according to initial Chord's topology
    ret_text = ""
    for i, x in enumerate(hashed_ips):
        ret_text = ret_text + "Node {} -->{}|".format(i + 1, x[1])
        # print("Node {} has ip:port: {}".format(i+1,x[1]))

    return ret_text, 200


try:
    nodes()
except:
    print("No master node found")


@app.route("/insert", methods=['GET', 'POST'])
def insert():
    key = request.args.get('key')
    node = request.args.get('node')
    data = request.data
    if node == "0":
        url = "http://{}/db/{}".format(random_addr(), key)
    else:
        print("sent at", hashed_ips[int(node) - 1][1])
        url = "http://{}/db/{}".format(hashed_ips[int(node) - 1][1], key)
    res = requests.post(url, data=data)
    return res.text, res.status_code


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    key = request.args.get('key')
    node = request.args.get('node')
    if node == "0":
        url = "http://{}/db/{}".format(random_addr(), key)
    else:
        url = "http://{}/db/{}".format(hashed_ips[int(node) - 1][1], key)
    res = requests.delete(url)
    return res.text, res.status_code


@app.route("/query", methods=['GET', 'POST'])
def query():
    key = request.args.get('key')
    node = request.args.get('node')
    if node == "0":
        url = "http://{}/db/q/{}".format(random_addr(), key)
    else:
        url = "http://{}/db/q/{}".format(hashed_ips[int(node) - 1][1], key)
    res = requests.get(url)
    return res.text, res.status_code


@app.route("/depart", methods=['GET', 'POST'])
def depart():
    node = request.args.get('node')
    url = "http://{}/dht/depart".format(hashed_ips[int(node) - 1][1])
    res = requests.get(url)
    nodes()
    return res.text, res.status_code


@app.route("/about", methods=['GET'])
def about():
    url = "http://192.168.1.1:5000/db/get_k"
    res = requests.get(url)
    k = res.text
    url = "http://192.168.1.1:5000/db/get_consistency"
    res = requests.get(url)
    if res.text:
        const = "Linearization"
    else:
        const = "Eventual Consistency"
    return k + ":" + const, 200


@app.route("/reset", methods=['GET'])
def reset():
    k = request.args.get('k')
    const = request.args.get('const')
    url = "http://192.168.1.1:5000/db/flush?k={}&const={}".format(k, const)
    res = requests.post(url)

    for addr in addresses:
        url = "http://{}/db/flush".format(addr)
        res = requests.post(url)
        time.sleep(0.2)

    time.sleep(0.3)
    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True, host="83.212.76.15", port=5000)
