from dht_node import DHTNode
import requests


def init(addr, m, dict_db):
    global node
    node = DHTNode(addr, m, dict_db)
    return node


def init_k(num_k):
    global k
    k = num_k
    return int(k)


def init_linearization(bool):
    global linear
    linear = bool
    return linear


def _find_successor(id):
    succ = node.get_successor()
    if DHTNode.between_right_inclusive(id, node.id, node.get_hash(succ)):
        return succ
    url = "http://{0}/dht/find_successor?id={1}".format(succ, id)
    res = requests.get(url)
    return res.text
