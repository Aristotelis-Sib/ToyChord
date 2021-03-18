from flask import Flask, request, abort
import requests
from threading import Thread
import myglobal

app = Flask(__name__)
master_addr='192.168.1.1:5000'

node=None
m=160
replicas=None
linearization=None

@app.before_first_request
def startup():
    global node,replicas,linearization
    addr = app.config['SERVER_NAME']    # "ip:port"
    node = myglobal.init(addr,m, {})
    replicas=get_replicas()
    myglobal.init_k(replicas)
    myglobal.init_test()
    linearization=get_consistency()
    myglobal.init_linearization(linearization)
    t1=Thread(target=join_dht,args=(addr,))
    t1.start()
    print("This server's id is {0}".format(node.id))

def join_dht(addr):
    """
    Send join request to master.
    """
    try:
        url = "http://{}/dht/join?addr={}".format(master_addr,addr)
        res = requests.post(url)
        return "ok", 200
    except ConnectionError:
        return abort(404)

def get_replicas():
    """
    Send request to master to get number of replicas.
    """
    url = "http://{}/db/get_k".format(master_addr)
    res=requests.get(url)
    return int(res.text)

def get_consistency():
    """
    Send request to master to get type of consistency.
    """
    url = "http://{}/db/get_consistency".format(master_addr)
    res=requests.get(url)
    return bool(res.text)

@app.route('/dht/depart', methods=['GET'])
def depart():
    """
    Depart request.
    """
    succ = node.get_successor()
    pred = node.get_predecessor()
    keys = [s for s in node.dict_db.keys()]
    list_of_keys_replicas = []
    list_of_keys_special = []
    url = "http://{0}/dht/depart_count".format(master_addr)
    res = requests.get(url)
    url = "http://{0}/dht/get_count".format(master_addr)
    res = requests.get(url)
    count=int(res.text)

    for key in keys:
        data = node.dict_db.get(str(key))
        if (count<replicas) and data[1]==replicas:
            continue
        ok = node.transfer(int(key), succ)
        if data[1] != replicas:
            list_of_keys_replicas.append(str(key))
        if data[1] == replicas-1:
            list_of_keys_special.append(str(key))

    # Update successor of previous node and predecessor of next node.
    url = "http://{0}/dht/set_successor_smpl?addr={1}".format(pred, succ)
    res = requests.post(url)
    url = "http://{0}/dht/set_predecessor?addr={1}".format(succ, pred)
    res = requests.post(url)

    # Send to replicas the keys.
    if pred != succ:
        if list_of_keys_replicas:
            print (list_of_keys_replicas)
            url = "http://" + succ + '/db/go_to_succ'
            res = requests.post(url, json={"data": list_of_keys_replicas,"dataextra":list_of_keys_special})
            if res.status_code != 200:
                return False

    shutdown()
    return "ok", 200

@app.route('/shutdown', methods=["GET"])
def shutdown():
    """
    Shutdown.
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Node Shutdown", 200

@app.route('/db/flush', methods=['POST'])
def flush():
    """
    Flush all data from dictionaries and get replica number k and
    type of consistency from master
    """
    myglobal.node.dict_db={}
    myglobal.node.dict_qid={}
    myglobal.node.qid=0

    url = "http://{}/db/get_k".format(master_addr)
    res=requests.get(url)
    myglobal.k=int(res.text)

    url = "http://{}/db/get_consistency".format(master_addr)
    res=requests.get(url)
    myglobal.linear=bool(res.text)
    if myglobal.linear:
        print("Linearization with k= ",myglobal.k)
    else:
        print("Eventual Constistency with k= ",myglobal.k )
    print("New dict_db is ", myglobal.node.dict_db)
    print("New dict_qid is ", myglobal.node.dict_qid)
    return "Flushed", 200
