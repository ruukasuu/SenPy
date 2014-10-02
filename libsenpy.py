import hashlib, base64, flask, sys, time, os
import senpy_settings as conf
from werkzeug import secure_filename

# Dict to base page rendering info upon
render_args = {
	"style":conf.style,
	"title":conf.title,
}

# Some functions
def unix_timestamp():
	return int(time.time())

def randbytes(count, b64):
	r = open("/dev/urandom", "rb")
	out = r.read(count)
	if b64:
		out = base64.b64encode(out)[:count]
	return out

def allowed_file(filename):
	return "." in filename and filename.rsplit('.', 1)[1] in conf.allowed_extensions

def inet_aton(a):
	a_bytes = a.split(".")
	n_bytes = b""
	for byte in a_bytes:
		n_bytes += bytes([int(byte)])
	return n_bytes

def inet_ntoa(n):
	a_bytes_list = [str(x) for x in list(n)]
	a = ".".join(a_bytes_list)
	return a

def generate_trip(seed):
	hash_input = bytes(conf.trip_salt + seed, "utf-8")
	hashed_eleven_bytes = hashlib.sha256(hash_input).digest()[:11]
	output_trip_untrimmed = base64.b64encode(hashed_eleven_bytes)
	output_trip_trimmed = output_trip_untrimmed[:-2]
	formatted_output = "!" + output_trip_trimmed.decode("utf-8")
	return formatted_output

def generate_secure_trip(seed, ip):
	hash_input = inet_aton(ip) + bytes(conf.trip_salt + seed, "utf-8")
	hashed_eleven_bytes = hashlib.sha256(hash_input).digest()[:11]
	output_trip_untrimmed = base64.b64encode(hashed_eleven_bytes)
	output_trip_trimmed = output_trip_untrimmed[:-2]
	formatted_output = "!!" + output_trip_trimmed.decode("utf-8")
	return formatted_output

# Functions for generating pages from templates
def generate_index():
	template_args = render_args.copy()
	try:
		conf.subtitle
	except:
		conf.subtitle = False
	if conf.subtitle:
		template_args["name"] = "%s - %s" % (conf.title, conf.subtitle)
	else:
		template_args["name"] = "%s" % (conf.title)
	template_args["form"] = False
	return flask.render_template("index.html", **template_args)

def generate_board(board_name):
	template_args = render_args.copy()
	template_args["name"] = "/%s/ - %s" % (board_name, conf.title)
	template_args["form"] = True
	return flask.render_template("index.html", **template_args)

def generate_catalog(board_name):
	template_args = render_args.copy()
	template_args["name"] = "/%s/ catalog - %s" % (board_name, conf.title)
	template_args["form"] = False
	return flask.render_template("index.html", **template_args)

def generate_thread(board_name, thread_id):
	template_args = render_args.copy()
	template_args["name"] = "%s - %s" % (board_name, conf.title)
	template_args["form"] = True
	return flask.render_template("index.html", **template_args)

def generate_message(message, url_to, redirect):
	return flask.render_template("message.html", message, url_to, redirect)

# Function for inserting and responding to a post submission
def submit_post(conn, board, thread, form, file):
	post_data = {
		"timestamp" : unix_timestamp(),
		"board" : board,
		"thread" : thread,
		"in_filename" : None,
		"extension" : None,
		"name" : None,
		"trip" : None,
		"subject" : None,
		"email" : None,
		"comment" : None,
		"cap" : None
	}

	form = dict(form)

	# filename
	if file and file.filename and allowed_file(file.filename):
		post_data["in_filename"] = secure_filename(file.filename)
		post_data["extension"] = post_data["in_filename"].rsplit('.', 1)[1]
	elif file and file.filename and not allowed_file(file.filename):
		return "error"
	else:
		post_data["in_filename"] = ""
		post_data["out_filename"] = ""
		post_data["extension"] = ""

	# name
	prename = form.get("name", [""])[0]
	name_trip_list = prename.split("#", 1)
	if len(name_trip_list) == 0:
		post_data["name"] = ""
		post_data["trip"] = ""
	elif len(name_trip_list) == 1:
		post_data["name"] = name_trip_list[0]
		post_data["trip"] = ""
	else:
		post_data["name"] = name_trip_list[0]
		pretrip = name_trip_list[1]
		if pretrip.startswith("#"):
			post_data["trip"] = generate_secure_trip(pretrip, "127.0.0.1")
		else:
			post_data["trip"] = generate_trip(pretrip)

	# subject
	post_data["subject"] = form.get("subject", [""])[0]

	# email
	post_data["email"] = form.get("email", [""])[0]

	# comment
	post_data["comment"] = form.get("comment", [""])[0]

	# capcode id
	post_data["cap"] = 0

	# decide whether to approve post and optionally do so
	if post_data["in_filename"] or post_data["comment"]:
		cursor = conn.cursor()
		cursor.execute("""INSERT INTO posts (board, parent, timestamp, extension, name, trip, subject, email, comment, cap) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;""", (post_data["board"], post_data["thread"], post_data["timestamp"], post_data["extension"], post_data["name"], post_data["trip"], post_data["subject"], post_data["email"], post_data["comment"], post_data["cap"]))
		last_id = int(cursor.fetchone()[0])
		if post_data["extension"]:
			out_filename = str(last_id) + "." + post_data["extension"]
			file.save(os.path.join(conf.file_directory, out_filename))
		conn.commit()
		return "post successful"
	else:
		return "posting requires a file or comment"
