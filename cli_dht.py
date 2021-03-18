import click
import requests
import time
import random
from hashlib import sha1

m = 160


# Update 1.1

@click.group()
def main():
    pass


global hashed_ips
hashed_ips = []


def get_hash(key):
    return int(int.from_bytes(sha1(key.encode()).digest(), byteorder='big') % 2 ** m)


def set_addresses():  # A function that returns current nodes in Chord
    #    print("HERE")
    url = "http://192.168.1.1:5000/overlay"
    res = requests.post(url)
    global addresses
    addresses = res.text.split("~")[1].split("|")


def nodes2():
    global hashed_ips
    set_addresses()
    ip_adds = addresses
    ids = []
    for i in ip_adds:
        ids.append(get_hash(i))  # Hashing ip_addresses:ports

    hashed_ips = list(zip(ids, ip_adds))
    hashed_ips = sorted(hashed_ips,
                        key=lambda x: x[0])  # a list of IDs in increasing order according to initial Chord's topology


@main.command(name='nodes', help='Give nodes id(0-9) and corresponding ip:host')
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
    for i, x in enumerate(hashed_ips):
        print("Node {} has ip:port: {}".format(i + 1, x[1]))


def random_addr():
    return random.choice(addresses)


@main.command(name='insert', help='Insert key-value pair')
@click.option('--node', '-n', required=False, default=-1, type=int,
              help='Give num of node to send request according to its position to Chord, eg. press "1" to send to 1st node')
@click.option('--key', '-k', required=True, type=str, help='Give Key to be inserted')
@click.option('--value', '-v', required=True, type=str, help='Give Value to be inserted')
def insert(node, key, value):
    if node == -1:
        url = "http://{}/db/{}".format(random_addr(), key)
    else:
        url = "http://{}/db/{}".format(hashed_ips[node - 1][1], key)
    print()
    res = requests.post(url, data=str(value).encode())
    if res.status_code == 200:
        click.echo('Inserted successfully! \n')
    else:
        click.echo('Error, 404! \n')


@main.command(name='delete', help='Delete key')
@click.option('--node', '-n', required=False, default=-1, type=int,
              help='Give num of node to send request according to its position to Chord, eg. press "1" to send to 1st node')
@click.option('--key', '-k', required=True, type=str, help='Delete Key')
def delete(node, key):
    if node == -1:
        url = "http://{}/db/{}".format(random_addr(), key)
    else:
        url = "http://{}/db/{}".format(hashed_ips[node - 1][1], key)
    res = requests.delete(url)
    if res.status_code == 200:
        print()
        click.echo('{} \n'.format(res.text))
    else:
        click.echo('Error, 404! \n')


@main.command(name='query', help='Returns Value of current Key')
@click.option('--node', '-n', required=False, default=-1, type=int,
              help='Give num of node to send request according to its position to Chord, eg. press "1" to send to 1st node')
@click.option('--key', '-k', required=True, type=str, help='Give Key to return its value')
def query(node, key):
    if node == -1:
        url = "http://{}/db/q/{}".format(random_addr(), key)
    else:
        url = "http://{}/db/q/{}".format(hashed_ips[node - 1][1], key)
    # print("url of query ", url)
    res = requests.get(url)
    # click.echo(res.text)
    if res.status_code == 200:
        if key == '*':
            click.echo(res.text)
        else:
            click.echo(res.text)
            print()
    else:
        click.echo(res.text)
        click.echo('Error, 404! \n')


@main.command(name='depart', help='Give node which will depart from chord')
@click.option('--node', '-n', required=True, type=int, help='Give num of node which will depart from Chord')
def depart(node):
    try:
        url = "http://{}/dht/".format(hashed_ips[node - 1][1]) + "/depart"
        res = requests.get(url)
        if res.status_code == 200:
            print()
            click.echo('Node with ip:port {} departed from chord successfully \n'.format(hashed_ips[node - 1][1]))
            set_addresses()
        else:
            click.echo('Error, 404! \n')

        hashed_ips.remove(hashed_ips[node - 1])
    except:
        click.echo("Node not found")


@main.command(name='overlay', help='Give chords topology')
@click.option('--node', '-n', required=False, default=-1, type=int, help='Give num of node to send request')
def overlay(node):
    if node == -1:
        url = "http://{}/overlay".format(random_addr())
    else:
        url = "http://{}/overlay".format(hashed_ips[node - 1][1])
    print()
    res = requests.post(url)
    click.echo(res.text.split("~")[0])


@main.command(name='help', help='Commands instructions')
def help():
    print()
    click.echo('insert <key> <value> : give a key-value pair to insert to chord \n')
    click.echo('delete <key> : give a key to be deleted from chord \n')
    click.echo('depart <port> : give a port of a node which will depart from chord \n')
    click.echo('overlay : print dht chords topology \n')


if __name__ == '__main__':
    set_addresses()
    nodes2()
    main()
