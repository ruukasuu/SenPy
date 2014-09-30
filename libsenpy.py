import hashlib, base64, flask, sys
import senpy_settings as conf

render_args = {
	"style":conf.style,
	"title":conf.title,
}

def timestamp():
	return int(time.time())

def randbytes(count, b64):
	r = open("/dev/urandom", "rb")
	out = r.read(count)
	if b64:
		out = base64.b64encode(out)[:count]
	return out

def generate_id():
	return randbytes(32, True)

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

def trip(seed):
	hash_input = bytes(conf.trip_salt + seed, "utf-8")
	hashed_eleven_bytes = hashlib.sha256(hash_input).digest()[:11]
	output_trip_untrimmed = base64.b64encode(hashed_eleven_bytes)
	output_trip_trimmed = output_trip_untrimmed[:-2]
	formatted_output = "!" + output_trip_trimmed.decode("utf-8")
	return formatted_output

def secure_trip(seed, ip):
	hash_input = inet_aton(ip) + bytes(conf.trip_salt + seed, "utf-8")
	hashed_eleven_bytes = hashlib.sha256(hash_input).digest()[:11]
	output_trip_untrimmed = base64.b64encode(hashed_eleven_bytes)
	output_trip_trimmed = output_trip_untrimmed[:-2]
	formatted_output = "!!" + output_trip_trimmed.decode("utf-8")
	return formatted_output

def post(conn, board, parent, timestamp, extension, name, trip, cap):
	cursor = conn.cursor()
	cursor.execute("""INSERT INTO posts VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", (generate_id().decode("ascii"), board, parent, timestamp, extension, name, trip, cap))
	conn.commit()

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
	template_args["form"] = True
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
