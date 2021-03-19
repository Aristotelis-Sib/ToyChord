# ToyChord

NTUA Distributed Systems Course 2020-2021 

Referenced [ShaeBrown chord-flask](https://github.com/ShaeBrown/chord-flask.git) repo for some initial ideas

## Run 
```pip3 install -r requirements.txt```
 
Must start a bootstrap node (done with argument -m True)

```
python3 startserver -m True
```

For startserver arguments

```python3 startserver --help```

Start as many other nodes (only 1 boostrap) with different ports,or host:ports addresses. 
Nodes join automaticaly to boostrap node ,must change first hardcoded host:port address of bootstrap node  (*master_addr* variable) in dht_client.py.

For CLI commands run:

```python3 cli_dht.py --help``` 

And choose action desired (address of bootstrap node must be changed manualy)

For Frontend commands first run: 

```python3 front_public2local.py```

Change port to desired (or if working in VM's give public ip )

In "client" machine run:

```python3 front.py``` 

Change host:port to desired (default localhost:5000)

## About files
**Back-End**  <br>
*dht_node.py* --> Implementation of basic DHT node <br>
*dht_master.py*--> Boostrap node only endpoints,functions and operations <br>
*dht_client.py*--> Client node only endpoints,functions and operations <br>
*cmn_endpoints*--> Common endpoints and operations for both client and boostrap <br>
*myglobal.py*--> "Hacky" solution for passing global variables between cmn_endpoints.py and dht_client.py or dht_master.py <br>
*startserver.py*--> Helper function for starting a new node <br>
*cli_dht.py*--> CLI implementation for actions on our Chord <br>
*front_public2local.py*--> Front-end intermediate "server" for accepting requests from client and forwarding to the Chord
<br>
For the scripts bellow (and for above but have been explained ) caution must be taken about the boostrap address to run properly
*exper_1.py*,*exper_2.py*,*exper_3.py*--> Implementation of 3 experiments asked in exercise <br>
*compare.py* --> Helper function for comparing true results of experiments with our results <br>
*insert_data.py*,*show_data.py* --> Scripts for inserting and showing some dummy data
<br>

**Frontend** <br>
*/templates*--> HTML files <br>
*forms.py* --> Forms for insert,delete etc. actions <br>
*front.py* --> Fron-end "server" for starting a client side browser frontend <br>






