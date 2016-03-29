#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
 
import re
import time 
import json 
import md5
import pdb
import random 
import psycopg2
import traceback

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
#DATABASEURI = "sqlite:///test.db"
DATABASEURI = "postgresql://hc2819:KRBJZL@w4111db.eastus.cloudapp.azure.com/hc2819"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args

  #cursor = g.conn.execute("select rid from restaurants;")
  #cursor = g.conn.execute("select rm.namemenu, rt.name,m.caloryamount, m.proteinamount, m.sodiumamount, rm.price from restaurants rt, restaurantsmenu rm, menunutrients m where rm.rid = rt.rid and rm.mid = m.mid and m.rid = rm.rid; ")
#  print len(cursor)
  #for item in cursor:
    #print item['rid']
  #cursor.close()
  names = []
  
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}:
  #
  #context = dict(foodname = foodname, restautrant = restaurantname, sodium = sodium, calorie = calorie, protein = protein, price = price )


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
@app.route('/')
def approot():
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
#@app.route('/another')
#def another():
#  return render_template("anotherfile.html")

#@app.route('/basicsearch', methods=['POST'])
#def basicsearch():
#  name = request.form['name']
#  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
#  return redirect('/')

# Example of adding new data to the database

@app.route('/order_page')
def order_page():
  return render_template("order.html")

@app.route('/back', methods=['POST','GET'])
def back():
  return render_template("index.html")

@app.route('/search', methods=['POST','GET'])
def search():
  for item in request.form:
    print item
    print request.form[item]
  restaurant = request.form['restaurant']
  category = request.form['category']
  calorie_upper = request.form['calorie_upper']
  calorie_lower = request.form['calorie_lower']
  sodium_upper = request.form['sodium_upper']
  sodium_lower = request.form['sodium_lower']
  protein_upper = request.form['protein_upper']
  protein_lower = request.form['protein_lower']
  keyword = request.form['keyword']

  q = 'select rm.namemenu, rt.name,m.caloryamount, m.proteinamount, m.sodiumamount, rm.price from restaurants rt, restaurantsmenu rm, menunutrients m where rm.rid = rt.rid and rm.mid = m.mid and m.rid = rm.rid and rt.name = %s and rm.namemenu = %s and rm.category = %s and  m.caloryamount < %s and m.caloryamount > %s and m.sodiumamount < %s and m.sodiumamount > %s and m.proteinamount < %s and m.proteinamount > %s;'
  #q = "select rm.namemenu, rt.name,m.caloryamount, m.proteinamount, m.sodiumamount, rm.price from restaurants rt, restaurantsmenu rm, menunutrients m where rm.rid = rt.rid and rm.mid = m.mid and m.rid = rm.rid; "
  print q  
  try:
    cursor = g.conn.execute(q, (restaurant, keyword, category, calorie_upper, calorie_lower,sodium_upper, sodium_lower, protein_upper, protein_lower,))
  #cursor = g.conn.execute(q)
  #cursor = g.conn.execute("select rm.namemenu, rt.name,m.caloryamount, m.proteinamount, m.sodiumamount, rm.price from restaurants rt, restaurantsmenu rm, menunutrients m where rm.rid = rt.rid and rm.mid = m.mid and m.rid = rm.rid; ")

    foodname = []
    restaurantname = []
    sodium = []
    calorie = []
    protein = []
    price = []
    error = []
  #
  # example of a database query
  #
  
    for result in cursor:
      print result['namemenu']
      foodname.append(result['namemenu'])# can also be accessed using result[0]
      print result['name']
      restaurantname.append(result['name'])
      print result['sodiumamount']
      sodium.append(result['sodiumamount'])
      print result['caloryamount']
      calorie.append(result['caloryamount'])
      print result['proteinamount']
      protein.append(result['proteinamount'])
      print result['price']
      price.append(result['price'])
    cursor.close()

  #context = dict(foodname = foodname, restautrant = restaurantname, sodium = sodium, calorie = calorie, protein = protein, price = price )
    #g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
    return render_template("index.html", foodname = foodname, restautrant = restaurantname, sodium = sodium, calorie = calorie, protein = protein, price = price)
  except Exception as e:
    q = "Not found"
    print q
    error.append(q)
    return render_template("index.html", error = error)


@app.route('/order', methods=['POST','GET'])
def order():
  restaurant = request.form['restaurant']
  print restaurant
  foodname = request.form['foodname']
  print foodname
  quantity = request.form['quantity']
  print quantity
  name = request.form['name']
  print name
  deliverytime = request.form['deliverytime']
  print deliverytime
  address = request.form['address']
  print address
  mid = []
  rid = []
  amount = []
  uid = []
  oid = []
  price = 0
  calorie = 0
  sodium = 0
  protein = 0
  foodname_list = []
  restaurant_list = []
  name_list = []
  address_list = []
  totalprice_list = []
  foodname_list.append(foodname)
  restaurant_list.append(restaurant)
  name_list.append(name)
  address_list.append(address) 
  amount.append(quantity)
  q = 'select rm.mid, rt.rid, rm.price, m.caloryamount, m.sodiumamount, m.proteinamount from restaurants rt, restaurantsmenu rm, menunutrients m where rt.rid = rm.rid and m.mid = rm.mid and rm.namemenu = %s and rt.name = %s;' 
  cursor1 = g.conn.execute(q, (foodname, restaurant, ) )
  print q
  for  result in cursor1:
    mid.append(result['mid'])
    print result['mid']
    rid.append(result['rid'])
    print result['rid']
    price = price + int(result['price'])
    print result['price']
    calorie = calorie + int(result['caloryamount'])
    print result['caloryamount']
    sodium = sodium + int(result['sodiumamount'])   
    print result['sodiumamount']
    protein = protein + int(result['proteinamount'])
    print result['proteinamount']
  cursor1.close()
  q2 = 'select uid from usersearch;'
  print q2
  cursor2 = g.conn.execute(q2)
  for result in cursor2:
    uid.append(result['uid'])
    print result['uid']
  length_uid = len(uid) 
  cursor2.close()
  uid_new = length_uid + 21
  q3 = 'select oid from userorder;'
  cursor3 = g.conn.execute(q3)
  for result in cursor3:
    oid.append(result['oid'])  
    print result['oid']
  cursor3.close()
  length_oid = len(oid)   
  oid_new = length_oid + 100

  q4 = 'insert into usersearch (uid, name) Values(%s, %s)'
  print q4
  g.conn.execute(q4, (uid_new, name,))
  totalprice = price * int(amount[0])
  print totalprice
  totalprice_list.append(totalprice)
  q5 = 'insert into userorder (uid, oid, deliveraddress, totalprice) Values(%s, %s, %s, %s)'
  print q5
  print address
  print totalprice
  g.conn.execute(q5, (uid_new, oid_new, address, totalprice,))
  print "success"
  print foodname_list
  print name_list
  print address_list
  print amount
  print restaurant_list
  print totalprice_list

  return render_template("final.html", foodname = foodname_list, name = name_list, deliveraddress = address_list, quantity = amount, restaurant = restaurant_list, totalprice = totalprice_list)
#     return redictrict('another')



@app.route('/login', methods=['GET','POST'])
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":

  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
