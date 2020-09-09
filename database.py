import sqlite3

def russianname(name):
    if name=="Sportwear":
        return "Одежда для спорта"
    elif name=="Velosport":
        return "Велоспорт"
    elif name=="Winter":
        return "Зимний спорт"
    elif name=="Swimming":
        return "Плавание"
    elif name=="Trainer":
        return "Тренажеры"


def add_user(data):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    email = data["email"]
    a = cur.execute("SELECT * FROM user_ WHERE email=?", (email,))
    if len(list(a))!=0:
        return False
    data_tuple = (data["name"],data["email"], data["phone"], data["city"], data["country"], data["zip"], data["password"], data["check"])
    cur.execute("INSERT INTO user_ (name, email, phone, city, country, zipcode, password, public_access) VALUES (?,?,?,?,?,?,?,?)",(*data_tuple,))
    bb = cur.execute("SELECT * FROM user_")
    rows = bb.fetchall()
    for row in rows:
        print(row)
    conn.commit()
    conn.close()
    return True

def auth(data):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    bb = cur.execute("SELECT * FROM user_")
    rows = bb.fetchall()
    for row in rows:
        print(row)
    email = data["email"]
    password = data["password"]
    a = cur.execute("SELECT userID, name FROM user_ WHERE email=? AND password=?", (email, password))
    rows = a.fetchall()
    for row in rows:
        print(row)
    conn.close()
    if len(rows)==0:
        print(False)
        return False
    print(rows[0])
    return rows[0]

def login_adm(data):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    login = data["loginadm"]
    password = data["password"]
    a = cur.execute("SELECT adminID, login FROM admin WHERE login=? AND password=?", (login, password))
    rows = a.fetchall()
    if len(rows) == 0:
        return False
    return rows[0]

def remove_from_cart(custID, prodID):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE userID=? AND prodID=?", (custID, prodID))
    conn.commit()

def update_cart(userID, qty):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    for prodID in qty:
        cur.execute("DELETE FROM cart WHERE prodID=? AND userID=?", (prodID, userID))
        cur.execute("INSERT INTO cart VALUES (?,?,?)", (userID, prodID, qty[prodID]))
    conn.commit()
    conn.close()

def profile(id):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM user_ WHERE userID=?", (id,))
    rows = a.fetchall()
    for row in rows:
        print(row)
    if len(rows)==0:
        return False
    print(rows[0])
    return rows[0]

def update_user(data, id):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("UPDATE user_ SET phone=?, city=?, country=?, zipcode=? where userID=?",
                (data["phone"],
                 data["city"],
                 data["country"],
                 data["zip"],
                 int(id)))
    conn.commit()
    conn.close()

def search_products(srchBy, category, keyword):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    keyword = ['%'+i+'%' for i in keyword.split()]
    if len(keyword)==0: keyword.append('%%')
    if srchBy=="by category":
        a = cur.execute("""SELECT prodID, name, category, price
                        FROM product WHERE category=? AND quantity!=0 """,(russianname(category),))
        res = [i for i in a]
    elif srchBy=="by keyword":
        res = []
        for word in keyword:
            a = cur.execute("""SELECT prodID, name, category, price
                            FROM product
                            WHERE (name LIKE ? OR description LIKE ? OR category LIKE ?) AND quantity!=0 """,
                            (word, word, word))
            res += list(a)
        res = list(set(res))
    conn.close()
    return res

def product_info_db(id):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM product WHERE prodID=?", (id,))
    rows = a.fetchall()
    for row in rows:
        print(row)
    return rows[0]

def check_psswd(psswd, userid):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    a = cur.execute("SELECT password FROM user_ WHERE userID=?", (userid,))
    real_psswd = list(a)[0][0]
    conn.close()
    return psswd==real_psswd

def set_psswd(psswd, userid):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("UPDATE customer SET password=? WHERE custID=?", (psswd, userid))
    conn.commit()
    conn.close()

def view_cart(userid):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM cart WHERE userID=?", (userid,))
    rows = a.fetchall()
    l = []
    for row in rows:
        print(row)
    for row in rows:
        prodid = row[1]
        quant = row[2]
        b = cur.execute("SELECT * FROM product WHERE prodID=?", (prodid,))
        br = b.fetchall()
        l.append(br[0] + tuple(str(quant)))
    print(l)
    conn.commit()
    conn.close()
    return l

def add_to_cart(prodID, userID, number=1):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM cart WHERE userID=? AND prodID=?", (userID, prodID))
    rows = a.fetchall()
    if len(rows) == 0:
        cur.execute("""INSERT INTO cart VALUES (?,?,1) """, (userID, prodID))
        conn.commit()
    else:
        a = cur.execute("SELECT quantity FROM cart WHERE userID=? AND prodID=?", (userID,prodID))
        rows = a.fetchall()
        q = rows[0]
        quantity = q[0]
        cur.execute("UPDATE cart SET quantity=? WHERE userID=? AND prodID=?", (quantity + number, userID, prodID))
        conn.commit()
    conn.close()

def view_all():
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM product")
    rows = a.fetchall()
    for row in rows:
        print(row)


def add_prod(adminID, data):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM product")
    rows = a.fetchall()
    for row in rows:
        print(row)
    tupl = (data["name"],
           100,
           data["category"],
           data["price"],
           data["description"],
           adminID)
    cur.execute("INSERT INTO product (name, quantity, category, price, description, adminID) VALUES (?,?,?,?,?,?)", tupl)
    conn.commit()
    conn.close()

def del_prod(prodID):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM CART where prodID=?", (prodID,))
    conn.commit()
    cur.execute("DELETE FROM product WHERE prodID=?", (prodID,))
    conn.commit()
    conn.close()






















