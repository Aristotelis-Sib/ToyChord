from flask import Flask, render_template, url_for, flash, redirect
import forms
import requests
import time
import random
from hashlib import sha1
from wtforms.validators import ValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
public_addr="83.212.76.15:5000"
global max_node
global activenodes

def get_nodes(form,field):
    url = "http://{}/nodes".format(public_addr)
    res = requests.get(url)
    print(res.text)
    max_node=len(res.text.split("|")[:-1])
    if type(field.data)==int:
        if field.data>max_node:
            raise ValidationError("No such node in Chord, {} in total".format(max_node))

def nodes():
    global activenodes
    global max_node
    url = "http://{}/nodes".format(public_addr)
    try:
        res = requests.get(url)
        max_node=len(res.text.split("|")[:-1])
        node0=["Node 0 -->Random Node"]
        activenodes=node0+res.text.split("|")
    except:
        activenodes=["Problem with Master Node"]
    return activenodes

@app.route("/")
@app.route("/home", methods=['GET','POST'])
def home():
    form=forms.Insert()

    if form.validate_on_submit():
        print(form.action.data)
        return redirect('/home')
    
    return render_template('home.html',form=form)

@app.route("/insert", methods=['GET','POST'])
def insert():
    form=forms.Insert()
    if form.validate_on_submit():
        key=form.key.data
        val=form.value.data
        node=form.nodes.data
        url = "http://{}/insert?key={}&node={}".format(public_addr, key,node)
        res = requests.post(url, data = str(val).encode())
        if res.status_code == 200:
            flash('Key value pair Inserted successfully! \n')
        else:
            flash('Error, 404! \n')
        
        return redirect('/insert')    
    
    return render_template('insert.html',form=form,nodes=activenodes)

@app.route("/delete", methods=['GET','POST'])
def delete():
    form=forms.Delete()

    if form.validate_on_submit():
        key=form.key.data
        node=form.nodes.data

        url = "http://{}/delete?key={}&node={}".format(public_addr, key,node)
        res = requests.post(url)
        if res.status_code == 200:
            flash('{}'.format(res.text))
        else:
            flash('Error, 404! \n')
        
        return redirect('/delete')   
    
    return render_template('delete.html',form=form,nodes=activenodes)

@app.route("/query", methods=['GET','POST'])
def query():
    form=forms.Query()

    if form.validate_on_submit():
        key=form.key.data
        node=form.nodes.data

        url = "http://{}/query?key={}&node={}".format(public_addr, key,node)
        res = requests.post(url)
        if res.status_code == 200:
            if key=="*":
                tmp=res.text.split("\n")
                tmp2= [i.split("|") for i in tmp[:-1]]
                list1=[i[0].split(":")[2]+":"+i[0].split(":")[3] for i in tmp2]
                list2=[i[1].split(":")[1][1:-1] for i in tmp2]
                return render_template('query_res.html',data=zip(list1,list2))
            else:
                flash('Query result: {}\n'.format(res.text))
        else:
            flash('Error, 404! \n')
        
        return redirect('/query')   
    return render_template('query.html',form=form,nodes=activenodes)


@app.route("/depart", methods=['GET','POST'])
def depart():
    form=forms.Depart()

    if form.validate_on_submit():
        node=form.nodes.data

        url = "http://{}/depart?node={}".format(public_addr,node)
        tmp=nodes()[node].split(">")[1]
        res = requests.get(url)
        if res.status_code == 200:
            flash('Node {} departed successfully'.format(tmp))
            nodes()
        else:
            flash('Master node cannot depart! \n')
        
        return redirect('/depart')
    


    return render_template('depart.html',form=form,nodes=activenodes[1:])

@app.route("/overlay", methods=['GET','POST'])
def overlay():
    return render_template('overlay.html',nodes=nodes()[1:])

@app.route("/help", methods=['GET','POST'])
def help():
    return render_template('help.html')

@app.route("/reset", methods=['GET','POST'])
def reset():
    form=forms.Reset()
    if form.validate_on_submit():
        k=form.k.data
        lin=form.Linearization.data
        if lin=='Linearization':
            lin="true"
        else:
            lin="false"

        url = "http://{}/reset?k={}&const={}".format(public_addr,k,lin)
        res = requests.get(url)

        return redirect('/reset')
    try:
        url = "http://{}/about".format(public_addr)
        res = requests.get(url)  
        tmp=res.text.split(":")
        nodes()
        text="Chord with replication k={},consistency {} and {} nodes".format(tmp[0],tmp[1],max_node)
    except:
        text="Problem with master node"

    return render_template('reset.html',form=form,about=text)



if __name__ == '__main__':
    nodes()
    app.run(debug=True,port=5000)