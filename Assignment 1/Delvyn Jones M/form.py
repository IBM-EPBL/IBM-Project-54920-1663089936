
from flask import Flask,redirect,url_for,render_template,request
app=Flask(__name__)
@app.route('/success/<name>,<email>,<phone>')
def success(name,email,phone):
    return "Welcome %s \n"%name+" Your email is %s"%email+" \n Your Phone number is %s" %phone
@app.route('/login',methods=["POST","GET"])
def login():
    if request.method=="POST":
        user=request.form["nm"]
        emai=request.form["em"]
        phon=request.form["pm"]
        return redirect(url_for('success', name=user,email=emai,phone=phon))
if __name__=='__main__':
    app.run(debug=True)