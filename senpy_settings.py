# SenPy settings

# Website info
title = "SenPy" # The name of the imageboard
subtitle = "気付いて！" # Optional subtitle

# Visual settings
style = "/static/akari.css" # CSS theme to use

# Database info
host = "localhost" # Host of database (usually localhost)
db = "senpy" # Database to connect to
username = "postgres" # Username to connect to database as
password = "changeme" # Database password

# File info
file_directory = "/home/nepp/simg" # Directory to store uploaded files in
max_size = 20 * (1024**2) # Max filesize
allowed_extensions = set(["jpg", "jpeg", "png", "gif"]) # File extensions to allow user to upload

# Seed used to generate tripcodes and secure tripcodes
trip_salt = "random" # Should be changed once and only once, before launching
