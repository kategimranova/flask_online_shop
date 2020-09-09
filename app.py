from flask import Flask, render_template, request, session, redirect, url_for
from database import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "THISISASECRET!"

@app.route("/", methods=["POST", "GET"])
def home():
    if "adminid" in session:
        session.pop('adminid')
        session.pop('loginadm')
    if "userid" in session:
        return render_template("home.html", signedin=True, id=session['userid'], name=session['name'])
    return render_template("home.html", signedin=False)

@app.route("/admin", methods=["POST", "GET"])
def home_admin():
    if "userid" in session:
        session.pop('userid')
        session.pop('name')
    if "adminid" in session:
        return render_template("home_admin.html", signedin=True, id=session['adminid'], name=session['loginadm'])
    return render_template("home_admin.html", signedin=False)

@app.route("/loginadmin", methods=["POST", "GET"])
def loginadm():
    if request.method == "POST":
        data = request.form
        userdat = login_adm(data)
        if userdat:
            session["adminid"] = userdat[0]
            session["loginadm"] = userdat[1]
            return redirect(url_for('home_admin'))
        return render_template("loginadmin.html", err=True)
    return render_template("loginadmin.html", err=False)

@app.route("/logoutadmin", methods=["POST", "GET"])
def logoutadm():
    session.pop('adminid')
    session.pop('loginadm')
    return redirect(url_for('home_admin'))

@app.route("/addproducts", methods=["POST", "GET"])
def addproducts():
    if "adminid" not in session:
        return redirect(url_for("home_admin"))
    view_all()
    if request.method == "POST":
        data = request.form
        add_prod(session["adminid"], data)
        return redirect(url_for("home_admin"))
    return render_template("addproduct.html")

@app.route("/product/delete/<id>", methods=["POST", "GET"])
def deleteproduct(id):
    if "adminid" not in session:
        return redirect(url_for("home_admin"))
    del_prod(id)
    return redirect(url_for("searchprod_admin"))

@app.route("/admin/products", methods=["POST", "GET"])
def searchprod_admin():
    if 'adminid' not in session:
        return redirect(url_for('home'))
    if request.method=="POST":
        data = request.form
        srchBy = data["search method"]
        category = None if srchBy=='by keyword' else data["category"]
        keyword = data["keyword"]
        results = search_products(srchBy, category, keyword)
        return render_template('searchprod_admin.html', after_srch=True, results=results, category=category)
    return render_template('searchprod_admin.html', after_srch=False)

@app.route("/register/", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        data = request.form
        ok = add_user(data)
        if ok:
            return render_template("success_register.html")
        return render_template("register.html", ok=False)
    return render_template("register.html", ok=True)

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.form
        userdat = auth(data)
        print(userdat)
        if userdat:
            session["userid"] = userdat[0]
            session["name"] = userdat[1]
            return redirect(url_for('home'))
        return render_template("login.html", err=True)
    return render_template("login.html", err=False)

@app.route("/logout/")
def logout():
    session.pop('userid')
    session.pop('name')
    return redirect(url_for('home'))

@app.route("/viewprofile/<id>", methods=["GET"])
def view_profile(id):
    if "userid" not in session:
        return redirect(url_for('home'))
    userid = session["userid"]
    myprofile = (int(userid)==int(id))
    print(myprofile)
    data = profile(id)
    id_exists = True
    if data == False:
        id_exists = False
    profile_type = "Customer"
    return render_template("view_profile.html", type=profile_type, name=data[1],email=data[2],phone=data[3],city=data[4],country=data[5],
                           zip=data[6], myprofile = myprofile, id_exists=id_exists)

@app.route("/myprofile")
def my_profile():
    if "userid" not in session:
        return redirect(url_for('home'))
    uid = str(int(session["userid"]))
    redirect("/view_profile/{}".format(uid))

@app.route("/changepassword")
def change_password():
    if "userid" not in session:
        return redirect(url_for('home'))
    check = True
    equal = True
    if request.method=="POST":
        userid = session["userid"]
        old_psswd = request.form["old_psswd"]
        new_psswd = request.form["new_psswd"]
        cnfrm_psswd = request.form["cnfrm_psswd"]
        check = check_psswd(old_psswd, userid)
        if check:
            equal = (new_psswd == cnfrm_psswd)
            if equal:
                set_psswd(new_psswd, userid)
                return redirect(url_for('home'))
    return render_template("change_password.html", check=check, equal=equal)

@app.route("/editprofile/", methods=["POST", "GET"])
def edit():
    if "userid" not in session:
        return redirect(url_for('home'))
    if request.method=="POST":
        print("post")
        data = request.form
        update_user(data, session['userid'])
        return redirect(url_for('view_profile', id=session['userid']))

    if request.method=="GET":
        print("get")
        userid = session["userid"]
        userinfo = profile(userid)
        return render_template("edit_profile.html",
                                name=userinfo[1],
                                email=userinfo[2],
                                phone=userinfo[3],
                                city=userinfo[4],
                                country=userinfo[5],
                                zip=userinfo[6],
                                check = userinfo[8])

@app.route("/buy/", methods=["POST", "GET"])
def buy():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if request.method=="POST":
        data = request.form
        srchBy = data["search method"]
        category = None if srchBy=='by keyword' else data["category"]
        keyword = data["keyword"]
        results = search_products(srchBy, category, keyword)
        return render_template('search_prod.html', after_srch=True, results=results, category=category)
    return render_template('search_prod.html', after_srch=False)

@app.route("/product/<id>", methods=["POST", "GET"])
def product_info(id):
    if ('userid' not in session):
        return redirect(url_for('home'))
    #elif ("adminid" not in session):
        #return redirect(url_for('home_admin'))
    if request.method == "GET":
        data = product_info_db(id)
        return render_template("product_info.html", category = data[3], name = data[1], price = data[4], description = data[5], pid = id)

@app.route("/product/addtocart/<pid>/", methods=["GET", "POST"])
def addtocart(pid):
    if "userid" not in session:
        return redirect(url_for('home'))
    if request.method == "POST":
        print("postt")
    data = request.form
    print(data)
    add_to_cart(pid, session['userid'],1)
    return redirect(url_for("viewcart"))

@app.route("/cart", methods=["POST", "GET"])
def viewcart():
    if "userid" not in session:
        return redirect(url_for('home'))
    l = view_cart(session["userid"])
    nullcart = True
    if len(l)!=0:
        nullcart = False
    return render_template("cart.html", nullcart=nullcart, table = l)


if __name__ == "__main__":
    app.run(debug=True, port=1322)






