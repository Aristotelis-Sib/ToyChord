# ToyChord

NTUA Distributed Systems Course 2020-2021 


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
