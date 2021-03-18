import click
import dht_client
import dht_master
import time
from cmn_endpoints import bp
import requests
import time
import os 
import signal

@click.command()
@click.option('-h', '--host', default='192.168.1.1', help='Hostname to bind to')
@click.option('-p', '--port', type=str, required=True, help='Port to bind to')
@click.option('-m', '--master', default=False, type=bool, help="Start Master Server (default False)")
@click.option('-k', '--kreplicas', default=1, type=int, help="Number of replicas (default=3)")
@click.option('-c', '--consistency', default=True, type=bool, help="Consistency: True:Linearization,False:Eventual Consistency (default=True)")
def main(host, port, master, kreplicas, consistency):
    dht_node=None
    if master:
        dht_node=dht_master
    else:
        dht_node=dht_client

    dht_node.app.config["SERVER_NAME"] = "{0}:{1}".format(host, port)
    dht_node.app.config['HOST'] = host
    dht_node.app.config['k'] = kreplicas
    dht_node.app.config['consistency'] = consistency
    dht_node.app.register_blueprint(bp)
    if master:
        dht_node.app.run(host=host, port=port)
    else:
        try:
            parent_id=os.fork()
            if parent_id>0:
                dht_node.app.run(host=host, port=port)
            else:
                requests.get("http://{}/pingclient?addr={}".format("192.168.1.1:5000","{0}:{1}".format(host, port)))
                os.kill(os.getpid(),signal.SIGKILL)
        except:
            print("Master node not found")

if __name__ == '__main__':
    main()

