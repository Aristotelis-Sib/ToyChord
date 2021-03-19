from flask import Flask, request, abort, Blueprint
import requests
from dht_node import DHTNode
import myglobal
from myglobal import _find_successor
from threading import Thread, Lock, Event

app = Flask(__name__)
bp = Blueprint('cmn_endpoints', __name__)


@bp.route('/dht/find_successor', methods=['GET'])
def find_successor():
    """
    Find successor of id.
    """
    id = int(request.args.get('id'))
    return _find_successor(id), 200


@bp.route('/dht/set_successor_smpl', methods=['POST', 'PUT'])
def set_successor_smpl():
    """
    Update successor of current node.
    """
    addr = request.args.get('addr')
    myglobal.node.update_successor_smpl(addr)
    return "ok", 200


@bp.route('/dht/set_successor', methods=['POST', 'PUT'])
def set_successor():
    """
    Update successor and transfer data to successor.
    """
    addr = request.args.get('addr')
    myglobal.node.update_successor(addr)
    return "ok", 200


@bp.route('/dht/get_successor', methods=['GET'])
def get_successor():
    """
    Return successor of current node.
    """
    return myglobal.node.get_successor(), 200


# Predecessor Stuff
@bp.route('/dht/set_predecessor', methods=['POST', 'PUT'])
def set_predecessor():
    """
    Update predecessor of current node.
    """
    addr = request.args.get('addr')
    myglobal.node.update_predecessor(addr)
    return "ok", 200


@bp.route('/dht/get_predecessor', methods=['GET'])
def get_predecessor():
    """
    Return predecessor of current node.
    """
    return myglobal.node.get_predecessor(), 200


@bp.route('/db/transfer', methods=['POST'])
def transfer():
    """
    Transfer the right <keys,values>.
    """
    addr = request.args.get('addr')
    keys = [s for s in myglobal.node.dict_db.keys()]
    keys_for_replicas = []
    for key in keys:
        if not DHTNode.between_right_inclusive(int(key), myglobal.node.get_hash(addr), myglobal.node.id):
            ok = myglobal.node.transfer(int(key), addr)
            keys_for_replicas.append(key)
            if not ok:
                abort(404)
    myglobal.node.update_replicas(keys_for_replicas, myglobal.k)
    return "updated", 200


@bp.route('/db/update_replicas', methods=['POST'])
def update_replicas():
    """
    Update replicas when a new node joins.
    """
    r = request.json['data']
    myglobal.node.update_replicas(r, myglobal.k)
    return "updated", 200


@bp.route('/db/q/<key>', methods=['GET'])
def get(key):
    """
    Send query request.
    """
    key = key.replace(" ", "_")
    qid = myglobal.node.qid
    myglobal.node.qid += 1
    event = Event()

    if key == "*":
        succ = myglobal.node.get_successor()
        if succ == myglobal.node.host:
            return "Node (ip:port):" + myglobal.node.host + "|" + "Data stored :" + str(
                list(myglobal.node.dict_db.values())) + "\n", 200
        myglobal.node.dict_qid[str(qid)] = (event, "Node (ip:port):" + myglobal.node.host + "|" + "Data stored :" + str(
            list(myglobal.node.dict_db.values())) + "\n")
        url = "http://{}/db/qhelpstar?idhost={}".format(succ, str(qid) + "_" + myglobal.node.host)
        res = requests.post(url)
        if res.status_code != 200:
            return "problem in network", 404

        event.wait(100)

        tmp = myglobal.node.dict_qid.get(str(qid))[1]
        myglobal.node.dict_qid.pop(str(qid))
        return tmp, 200

    val = myglobal.node.get_key(key)
    if val != "":
        if myglobal.linear:
            if val[0] and val[1] == myglobal.k:
                return val[0], 200
        else:
            if val[0]:
                return val[0], 200

    h = myglobal.node.get_hash(key)
    if DHTNode.between_right_inclusive(h, myglobal.node.get_hash(myglobal.node.get_predecessor()),
                                       myglobal.node.id) and val == "":
        return "Key not found", 404

    succ = myglobal.node.get_successor()
    myglobal.node.dict_qid[str(qid)] = (event, "")
    url = "http://{}/db/qhelp/{}?idhost={}".format(succ, key, str(qid) + "_" + myglobal.node.host)
    res = requests.post(url)
    if res.status_code != 200:
        return "problem in network", 404

    event.wait(100)
    if myglobal.node.dict_qid.get(str(qid))[1] == "":
        return "No Response from Chord,Network error", 404

    tmp = myglobal.node.dict_qid.get(str(qid))[1]
    myglobal.node.dict_qid.pop(str(qid))
    return tmp, 200


@bp.route('/db/qhelp/<key>', methods=['POST'])
def qhelp(key):
    idhost = request.args.get('idhost')
    qid = idhost.split("_")[0]
    host = idhost.split("_")[1]

    def inthread(key, qid, host):
        """
        Immediate response to nodes using threads.
        """
        val = myglobal.node.get_key(key)
        if val != "":
            if myglobal.linear:
                if val[0] and val[1] == myglobal.k:
                    url = "http://{}/db/qresponse?qid={}".format(host, str(qid))
                    res = requests.post(url, data=(val[0]))
                    return
            else:
                if val[0]:
                    url = "http://{}/db/qresponse?qid={}".format(host, str(qid))
                    res = requests.post(url, data=(val[0]))
                    return

        h = myglobal.node.get_hash(key)
        if DHTNode.between_right_inclusive(h, myglobal.node.get_hash(myglobal.node.get_predecessor()),
                                           myglobal.node.id) and val == "":
            url = "http://{}/db/qresponse?qid={}".format(host, str(qid))
            res = requests.post(url, data="Key not found")
            return

        succ = myglobal.node.get_successor()
        url = "http://{}/db/qhelp/{}?idhost={}".format(succ, key, str(qid) + "_" + host)
        res = requests.post(url)

    t = Thread(target=inthread, args=(key, qid, host,))
    t.start()
    return "ok", 200


@bp.route('/db/qresponse', methods=['POST', 'PUT'])
def qresponse():
    """
    Send to first node data, that asked about.
    """
    qid = request.args.get('qid')
    from_node = request.args.get('from')
    if from_node == None:
        data = request.data
        myglobal.node.dict_qid[str(qid)] = (myglobal.node.dict_qid[str(qid)][0], data)
        myglobal.node.dict_qid[str(qid)][0].set()
        return "ok", 200
    else:
        if from_node == myglobal.node.get_predecessor():
            data = request.json["data"]
            myglobal.node.dict_qid[str(qid)] = (
            myglobal.node.dict_qid[str(qid)][0], myglobal.node.dict_qid[str(qid)][1] + data)
            myglobal.node.dict_qid[str(qid)][0].set()
            return "ok", 200
        else:
            data = request.json["data"]
            myglobal.node.dict_qid[str(qid)] = (
            myglobal.node.dict_qid[str(qid)][0], myglobal.node.dict_qid[str(qid)][1] + data)
            return "ok", 200


@bp.route('/db/qhelpstar', methods=['POST'])
def get_all():
    """
    Returns key value stored in this DHT for all nodes
    """
    idhost = request.args.get('idhost')
    qid = idhost.split("_")[0]
    host = idhost.split("_")[1]

    def inthread(qid, host):
        url = "http://{}/db/qresponse?qid={}&from={}".format(host, str(qid), myglobal.node.host)
        res = requests.post(url, json={"data": "Node (ip:port):" + myglobal.node.host + '|' + "Data stored :" + str(
            list(myglobal.node.dict_db.values())) + "\n"})

        succ = myglobal.node.get_successor()
        if succ != host:
            url = "http://{}/db/qhelpstar?idhost={}".format(succ, str(qid) + "_" + host)
            res = requests.post(url)

    t = Thread(target=inthread, args=(qid, host,))
    t.start()
    return "ok", 200


@bp.route('/db/hash/<hash>', methods=['POST', 'PUT'])
def put_hash(hash):
    """
    Inserts the hash into the DHT. This is for transfering keys
    """
    # print("put hash data read is ", request.json["data"])
    myglobal.node.dict_db[str(hash)] = (request.json["data"][0], request.json["data"][1])
    return "ok", 200


@bp.route('/overlay', methods=['POST'])
def overlay():
    """
    Return overlay (nodes in DHT) with proper order
    """
    start_id = request.args.get('startid')
    if start_id == None:
        res_for_cli = str(myglobal.node.host)
        results = "Starting overlay from node with ip:port address " + str(myglobal.node.host) + "\n\n" + str(
            myglobal.node.host)
        results = results + "\n   |\n   v\n"
        succ = myglobal.node.get_successor()
        url = "http://{0}/overlay?startid={1}".format(succ, myglobal.node.id)
        res = requests.post(url)
        results = results + res.text.split("~")[0]
        if res.text.split("~")[1] != " ":
            res_for_cli = res_for_cli + "|" + res.text.split("~")[1]
        if res.status_code != 200:
            return abort(404)
        return results + "~" + res_for_cli, 200

    start_id = int(start_id)

    if start_id == myglobal.node.id:
        return "END (" + myglobal.node.host + ")\n" + "~ ", 200
    res_for_cli = str(myglobal.node.host)
    results = str(myglobal.node.host)
    results = results + "\n   |\n   v\n"
    succ = myglobal.node.get_successor()
    url = "http://{0}/overlay?startid={1}".format(succ, start_id)
    res = requests.post(url)
    results = results + res.text.split("~")[0]
    if res.text.split("~")[1] != " ":
        res_for_cli = res_for_cli + "|" + res.text.split("~")[1]

    if res.status_code != 200:
        return abort(404)
    return results + "~" + res_for_cli, 200


@bp.route('/', methods=['GET'])
def ping():
    """
    Returns when the server is ready.
    """
    return 'Pinged', 200


@bp.route('/db/<key>', methods=['POST', 'PUT'])
def put(key):
    key = key.replace(" ", "_")

    """
    Inserts the key into the DHT. The value is equal to the body of the HTTP
    request.
    """

    def eventual_update(kminus1, succ1, key, data):
        url = "http://{0}/db/{1}/{2}".format(succ1, key, kminus1)
        res = requests.post(url, data=data)

    h = myglobal.node.get_hash(key)
    succ = _find_successor(h)

    if succ == myglobal.node.host:
        myglobal.node.set_key(key, request.data, 1)
        succ1 = myglobal.node.get_successor()
        if myglobal.k - 1 != 0:
            if myglobal.linear:
                url = "http://{0}/db/{1}/{2}".format(succ1, key, str(myglobal.k - 1))
                res = requests.post(url, data=request.data)
                return res.text, res.status_code
            else:
                thread = Thread(target=eventual_update, args=(myglobal.k - 1, succ1, key, request.data,))
                thread.start()
        return "ok", 200

    if succ:
        url = "http://{}/db/{}".format(succ, key)
        res = requests.post(url, data=request.data)
        if res.status_code != 200:
            return abort(404)
        return "ok", 200
    return abort(404)


@bp.route('/db/<key>/<replic>', methods=['POST', 'PUT'])
def put_to_replicas(key, replic):
    """
    Insert the key to replicas.
    """
    myglobal.node.set_key(key, request.data, myglobal.k + 1 - int(replic))
    if int(replic) - 1 != 0:
        succ = myglobal.node.get_successor()
        url = "http://{0}/db/{1}/{2}".format(succ, key, str(int(replic) - 1))
        res = requests.post(url, data=request.data)
    return "ok", 200


# Delete for eventual Const
@bp.route('/db/<key>', methods=['DELETE'])
def delete(key):
    """
    Deletes the key from the DHT if it exists, noop otherwise.
    """

    key = key.replace(" ", "_")

    def eventual_delete(succ, key, kminus1):
        url = "http://{}/db/{}/{}".format(succ, key, kminus1)
        res = requests.delete(url)

    h = myglobal.node.get_hash(key)
    succ = _find_successor(h)

    if succ == myglobal.node.host:
        if myglobal.node.get_key(key) == "":
            return "Key not in Chord", 200

        myglobal.node.delete_key(key)
        succ1 = myglobal.node.get_successor()
        if myglobal.k - 1 != 0:
            if myglobal.linear:
                url = "http://{}/db/{}/{}".format(succ1, key, str(myglobal.k - 1))
                res = requests.delete(url)
                if res.status_code != 200:
                    return abort(404)
            else:
                thread = Thread(target=eventual_delete, args=(succ1, key, myglobal.k - 1))
                thread.start()
        return "Deleted", 200

    if succ:
        url = "http://{}/db/{}".format(succ, key)
        res = requests.delete(url)
        if res.status_code != 200:
            return abort(404)
        return res.text, 200
    return abort(404)


@bp.route('/db/<key>/<replica>', methods=['DELETE'])
def delete_from_replicas(key, replica):
    """
    Delete the key from replicas.
    """
    myglobal.node.delete_key(key)
    if int(replica) - 1 != 0:
        succ = myglobal.node.get_successor()
        url = "http://{}/db/{}/{}".format(succ, key, str(int(replica) - 1))
        res = requests.delete(url)
    return "ok", 200


@bp.route('/db/go_to_succ', methods=['POST'])
def go_to_succ():
    """
    Go to successor with a key list to update replicas when a node departs.
    """
    succ = myglobal.node.get_successor()
    data = request.json['data']
    keysextra = request.json['dataextra']
    to_delete = []
    keys = [s for s in myglobal.node.dict_db.keys()]
    for key in keysextra:
        data_test = {"data": (myglobal.node.dict_db[key][0], myglobal.k)}
        succ = myglobal.node.get_successor()
        url = "http://" + succ + '/db/hash/' + str(key)
        res = requests.post(url, json=data_test)
        to_delete.append(key)

    for key in to_delete:
        data.remove(key)

    url = "http://" + succ + '/db/update_replicas_depart'
    res = requests.post(url, json={"data": data})
    return "updated", 200


@bp.route('/db/update_replicas_depart', methods=['POST'])
def update_replicas_depart():
    """
    Update replicas when a node departs.
    """
    r = request.json['data']
    myglobal.node.update_replicas_dep(r, myglobal.k)
    return "updated", 200
