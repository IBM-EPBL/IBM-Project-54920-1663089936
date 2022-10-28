
import time
import random
import math
import datetime
from flask import Flask,render_template
app=Flask(__name__)
@app.route('/')

def homer():

    time.sleep(2.4)
    msg="This is printed after 2.4 seconds using \"time.sleep module\""
    tada =random.randrange(3, 9)
    msg1=" The above number is random number between 3 and 9 using \"random module\""
    tana=math.sqrt(25)
    msg2="The above number is square root of 25 using \"sqrt module\""
    msg3="I also used \"flask module\""
    taba= datetime.datetime.now()
    msg4=" This is today's date time using \"datetime module\""
    return render_template('modules.html',msg=msg,msg1=msg1,tada=tada,tana=tana,msg2=msg2,msg3=msg3,taba=taba,msg4=msg4)
if __name__=='__main__':
    app.run()