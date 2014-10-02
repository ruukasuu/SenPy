#! /usr/bin/python3

from flask import Flask, render_template, request, jsonify
import sys, psycopg2
import libsenpy as lib
conf = lib.conf

connection_string = "host='%s' dbname='%s' user='%s' password='%s'" % (conf.host, conf.db, conf.username, conf.password)
try:
	database_connection = psycopg2.connect(connection_string)
	print("Connected to database")
except:
	print("Error connecting to database")
	sys.exit()

app = Flask(__name__)

def main():
	app.run(debug=True)

@app.route("/")
def index():
	return lib.generate_index()

@app.route("/ayy")
def test():
	return render_template("message.html", style="/static/akari.css", name="ayy")

@app.route("/<board_name>/")
def board(board_name):
	return lib.generate_board(board_name.lower())

@app.route("/<board_name>/submit/", methods=["POST"])
def board_submit(board_name):
	return lib.submit_post(database_connection, board_name, "", request.form, request.files["file"])

@app.route("/<board_name>/catalog/")
def catalog(board_name):
	return lib.generate_catalog(board_name.lower())

@app.route("/<board_name>/<thread_id>/")
def thread(board_name, thread_id):
	return lib.generate_thread(board_name.lower(), thread_id)

@app.route("/<board_name>/<thread_id>/submit/", methods=["POST"])
def thread_submit(board_name, thread_id):
	return lib.submit_post(database_connection, board_name, thread_id, request.form, request.files["file"])

if __name__ == "__main__":
	main()
