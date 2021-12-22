import sqlite3
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

@app.route("/posts", method=['GET'])
def get_all():
	db = sqlite3.connect("db.sqlite3")
	cursor = db.execute("select id, name, body from blog")
	posts = cursor.fetchall()
	posts = [{"id": id_, "name": name, "body": body} for id_, name, body
		in posts]
	db.close()
	return jsonify(posts)

@app.route("/", methods=['POST', 'GET'])
def index():
	db = sqlite3.connect("db.sqlite3")
	cursor = db.execute("select name, body from blog order by id desc")
	posts = cursor.fetchall()
	if request.method == 'POST':
		name = request.form.get('name', '')
		body = request.form.get('body', '')
		if name and body:
			db = sqlite3.connect("db.sqlite3")
			cursor = db.cursor()
			cursor.execute(
				"insert into blog (name, body) values (?, ?)",
				(name, body)
  			)
			cursor.close()
			db.commit()
			db.close()
			return redirect('/')
	db.close()
	return render_template("index.html", posts=posts)
if __name__ == '__main__':
	app.run()
