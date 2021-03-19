from hashlib import sha1
from threading import Lock
import requests


class DHTNode(object):

    def __init__(self, host, m, dict_db):
        self.host = host  # ip:port
        self.m = m
        self.id = self.get_hash(self.host)  # Hashed ip  , must add port
        self.predecessor = self.host
        self.pred_lock = Lock()
        self.successor = self.host
        self.succ_lock = Lock()
        self.dict_db = dict_db  # Just a dictionary
        self.qid = 0
        self.dict_qid = {}

    def get_successor(self):
        """
        Get successor.
        """
        self.succ_lock.acquire()
        succ = self.successor
        self.succ_lock.release()
        return succ

    def get_predecessor(self):
        """
        Get predecessor.
        """
        self.pred_lock.acquire()
        pred = self.predecessor
        self.pred_lock.release()
        return pred

    def get_hash(self, key):
        """
        Hashing.
        """
        return int(int.from_bytes(sha1(key.encode()).digest(), byteorder='big') % 2 ** self.m)

    def update_predecessor(self, pred):
        """
        Update predecessor.
        """
        self.pred_lock.acquire()
        self.predecessor = pred
        self.pred_lock.release()

    def update_successor_smpl(self, succ):
        """
        Update successor.
        """
        self.succ_lock.acquire()
        self.successor = succ
        self.succ_lock.release()

    def update_successor(self, succ):
        """
        Update successor and transfer data.
        """
        self.succ_lock.acquire()
        self.successor = succ
        self.succ_lock.release()
        if succ == self.host:
            return
        url = "http://" + succ + "/db/transfer?addr=" + self.host
        res = requests.post(url)
        if res.status_code != 200:
            print("Keys failed to transfer")

    def set_key(self, key, value, replica):
        """
        Set value and number of replica in key.
        """
        h = self.get_hash(key)
        self.dict_db[str(h)] = (value.decode(), replica) if type(value) == bytes else (value, replica)

    def get_key(self, key):
        """
        Get value of key.
        """
        h = str(self.get_hash(key))
        val = self.dict_db.get(h)

        if val is not None:
            return val.decode() if type(val) == bytes else val
        return ""

    def delete_key(self, key):
        """
        Delete key.
        """
        h = self.get_hash(key)
        self.dict_db.pop(str(h))

    def transfer(self, hash, addr):
        """
        Transfer data to addr.
        """
        if addr == self.host:
            return True
        data = self.dict_db.get(str(hash))
        data_test = {"data": data}
        url = "http://" + addr + '/db/hash/' + str(hash)
        res = requests.post(url, json=data_test)
        if res.status_code != 200:
            return False
        else:
            return True

    def update_replicas(self, list_of_keys, k):
        """
        Update replicas when join.
        """
        to_delete = []
        for el in list_of_keys:
            cur_val = self.dict_db.get(el)
            if cur_val != None:
                if int(cur_val[1]) < k:
                    self.dict_db[el] = (self.dict_db[el][0], self.dict_db[el][1] + 1)
                else:
                    # delete key from last node
                    self.dict_db.pop(el)
                    to_delete.append(el)
            else:
                to_delete.append(el)

        for key in to_delete:
            list_of_keys.remove(key)

        if not list_of_keys:
            return True
        else:
            succ = self.get_successor()
            url = "http://" + succ + '/db/update_replicas'
            res = requests.post(url, json={"data": list_of_keys})
            if res.status_code != 200:
                return False

    def update_replicas_dep(self, list_of_keys, k):
        """
        Update replicas when depart.
        """
        to_delete = []
        for el in list_of_keys:
            cur_val = self.dict_db.get(el)
            if cur_val != None:
                self.dict_db[el] = (self.dict_db[el][0], self.dict_db[el][1] - 1)
                # send key to last node
                if cur_val[1] == k:
                    data_test = {"data": (self.dict_db[el][0], k)}
                    succ = self.get_successor()
                    url = "http://" + succ + '/db/hashdepart/' + str(el)
                    res = requests.post(url, json=data_test)
                    to_delete.append(el)
                    if res.status_code != 200:
                        return False
        for key in to_delete:
            list_of_keys.remove(key)

        if not list_of_keys:
            return True
        else:
            succ = self.get_successor()
            url = "http://" + succ + '/db/update_replicas_depart'
            res = requests.post(url, json={"data": list_of_keys})
            if res.status_code != 200:
                return False

    @staticmethod
    def between_right_inclusive(x, a, b):
        """
        Compare ids.
        """
        if a > b:
            return a < x or b >= x
        elif a < b:
            return a < x and b >= x
        else:
            return a != x
