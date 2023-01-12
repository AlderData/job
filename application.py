#Job application - display and filter lists of startup compnaies I have analyzed

### External Libraries
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
#import pyTigerGraph as tg
import pandas as pd
import numpy as np
from datetime import datetime

#Files
global startingDB
startingDB = 'static/arizona.csv'
global outputpath
outputpath = 'static/'

#read files into DataFrame
df = pd.read_csv(startingDB)
global users
users = pd.DataFrame([{'email':'chad@me.com', 'password':'temp'}])
print("user dataframe:", users)

#export dataframe into csv file
#df.to_csv(outputpath+date+"_MIN.csv", index = False)


## Application
app = Flask(__name__)

#configure Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/", methods=["GET","POST"])
def index():
    if not session.get("user"):
        return redirect("/login")
    return redirect("/explore")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        haoma = request.form.get("password")
        print("app48: user email list:", users['email'].unique())
        print("app49: user password list:", users['password'].unique())

        if email not in users["email"].unique():
            return render_template("error.html", message="Email not registered")
        elif email in users["email"].unique():
            print("email registered")
            temp = users[users['email'] == email]
            #temp2 = temp.loc[0,'password']
            temp2 = temp['password'].values[0]
            if haoma != temp2:
                return render_template("error.html", message="password incorrect")
        session["user"] = email
        timestamp = datetime.now(tz=None)
        timestamp = timestamp.strftime("%Y-%m-%d, %H:%M:%S")
        #ADD Login Analytic to graph
        #gq.addLogin(email, timestamp, connNWH)
        print(f"now: {timestamp}")
        return redirect("/")
    return render_template("login.html")


@app.route("/logout", methods=["GET","POST"])
def logout():
    if request.method == "POST":
        session["user"] = None
    if not session.get("user"):
        return redirect("/login")
    return render_template("logout.html")


@app.route("/explore", methods=["GET", "POST"])
def explore():
    if request.method == "GET":
        ajobs = df['jobAbstract'].unique()
        #print("app82 ajobs:", ajobs)
        apersonas = df['personaAbstract'].unique()
        #print("app82 apersonas:", apersonas)
        ilevels=df['interest'].unique()
        #print("app86 interest levels:", ilevels)
        #print("app.py87>DF main:", df)
        #events = df[['startup'],['persona'],['job'],['taskDetail'],['jobHow'],['interest'],['market'],['marketDetail']]
        eventsDF = pd.DataFrame().assign(State=df['state'], Startup=df['startup'], NextStep=df['nextStep'], Persona=df['personaAbstract'], Job=df['jobAbstract'], JobDetail=df['taskDetail'],How=df['jobHow'], Interest=df['interest'], MarketRank=df['market'],MarketDetail=df['marketDetail'])
        print("app.py89 DF events:", eventsDF)
        events = eventsDF.to_dict('records')
        return render_template("explore.html", ilevels=ilevels, ajobs=ajobs, apersonas=apersonas, events=events)
    if request.method == "POST":
        filter_dict = request.form.to_dict(flat=False)
        print("filter values:", filter_dict)
        ajobs = df['jobAbstract'].unique()
        apersonas = df['personaAbstract'].unique()
        ilevels=df['interest'].unique()
        eventsDF = pd.DataFrame().assign(Startup=df['startup'], NextStep=df['nextStep'], Persona=df['personaAbstract'], Job=df['jobAbstract'], JobDetail=df['taskDetail'],How=df['jobHow'], Interest=df['interest'], MarketRank=df['market'],MarketDetail=df['marketDetail'])
        print("APP89 DF events:", eventsDF)

        #filter the events using the dictionary ---------------------------
        formV = {k: str(v[0]) for k,v in iter(filter_dict.items())}
        print("new filter:", formV)
        filter_list = []
        if 'Interest' in formV:
            print("There is an Interest Filter")
            interestPiece = f"Interest == {formV['Interest']}"
            filter_list.append(interestPiece)
        else:
            interestPiece = ""
        if 'Persona' in formV:
            print("There is a Persona Filter")
            personaPiece = f"Persona == '{formV['Persona']}'"
            filter_list.append(personaPiece)
        else:
            personaPiece = ""
        if 'Job' in formV:
            print("There is a Job Filter")
            jobPiece = f"Job == '{formV['Job']}'"
            filter_list.append(jobPiece)
        else:
            jobPiece = ""
        filter = ' & '.join([str(elem) for elem in filter_list])
        print("APP119 Filter:", filter)
        eventsFILTER = eventsDF.query(filter)
        print("APP104 DF events Filtered:", eventsFILTER)

        events = eventsFILTER.to_dict('records')
        return render_template("explore.html", ilevels=ilevels, ajobs=ajobs, apersonas=apersonas, events=events, filters=formV)
