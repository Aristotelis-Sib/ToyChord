from flask import Flask, request, abort
import requests
import myglobal
from myglobal import _find_successor
import time

app = Flask(__name__)
node = None
m = 160
replicas = None
linearization = None


@app.before_first_request
def startup():
    global node, replicas, linearization
    addr = app.config['SERVER_NAME']  # "ip:port"
    node = myglobal.init(addr, m, {})
    replicas = app.config['k']
    linearization = app.config['consistency']
    myglobal.init_k(replicas)
    myglobal.init_linearization(linearization)
    print("This server's id is {0}".format(node.id))
    if linearization:
        print("Linearization with k= ", myglobal.k)
    else:
        print("Eventual Constistency with k= ", myglobal.k)


@app.route('/dht/join', methods=['POST', 'PUT'])
def join():
    """
    Receive join request from a new node.
    Find position of the node in the Chord and updates predecessors and successors.
    """
    addr = str(request.args.get('addr'))
    try:
        succ_of_addr = _find_successor(node.get_hash(addr))

        url = "http://{}/dht/get_predecessor".format(succ_of_addr)
        res = requests.get(url)
        predecessor_of_addr = res.text

        # Update predecessor of new node.
        url = "http://{0}/dht/set_predecessor?addr={1}".format(str(addr), str(predecessor_of_addr))
        res = requests.post(url)

        # Update successor of the predecessor of new node.
        url = "http://{0}/dht/set_successor_smpl?addr={1}".format(predecessor_of_addr, addr)
        res = requests.post(url)

        # Update successor of new node and transfer <keys, values> to new node.
        url = "http://{0}/dht/set_successor?addr={1}".format(addr, succ_of_addr)
        res = requests.post(url)

        # Update predecessor of next node to new node.
        url = "http://{0}/dht/set_predecessor?addr={1}".format(succ_of_addr, addr)
        res = requests.post(url)
        return "ok", 200
    except ConnectionError:
        return abort(404)


@app.route('/db/get_k', methods=['GET'])
def get_k():
    """
    Give number of replicas to a node.
    """
    return str(replicas), 200


@app.route('/db/get_consistency', methods=['GET'])
def get_consistency():
    """
    Give type of consistency: Linearizability or Eventual Consistency
    """
    if linearization:
        return str(linearization), 200
    else:
        return "", 200


@app.route('/pingclient', methods=['GET'])
def pingclient():
    """
    Wait and ping client that sent the http request (so it joins)
    """
    addr = request.args.get("addr")
    time.sleep(0.4)
    url = "http://{}/".format(addr)
    requests.get(url)
    return "ok", 200


@app.route('/db/flush', methods=['POST'])
def flush():
    """
    Flush all data from dictionaries and reset k of replicas and consistency type based
    on arguments
    """
    k = request.args.get('k')
    global replicas, linearization
    if k != None:
        replicas = int(k)
    const = request.args.get('const')

    if const != None:
        if const == "true":
            linearization = True
        else:
            linearization = False

    myglobal.node.dict_db = {}
    myglobal.node.dict_qid = {}
    myglobal.node.qid = 0

    myglobal.k = replicas
    myglobal.linear = linearization

    if myglobal.linear:
        print("Linearization with k= ", myglobal.k)
    else:
        print("Eventual Constistency with k= ", myglobal.k)
    print("New dict_db is ", myglobal.node.dict_db)
    print("New dict_qid is ", myglobal.node.dict_qid)

    return "Flushed", 200
