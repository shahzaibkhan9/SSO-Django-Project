import sqlite3

# Establish a connection to the SQLite database
conn = sqlite3.connect('db.sqlite3')

# Create a cursor object
cursor = conn.cursor()

# Define the data you want to insert as a list of tuples
data_to_insert = [
    ("GitHub", "https://github.com/login", "static/app_icons/github.png"),
    ("Google", "https://accounts.google.com/signin", "static/app_icons/google.png"),
    ("Facebook", "https://www.facebook.com/login/", "static/app_icons/facebook.png"),
    ("Azure", "https://portal.azure.com/", "static/app_icons/azure.png"),
    ("Amazon", "https://console.aws.amazon.com/", "static/app_icons/amazon.png"),
    ("Twitter", "https://twitter.com/login", "static/app_icons/twitter.png")
]

# Use a single INSERT INTO query with placeholders and the executemany() method
insert_query = "INSERT INTO main_app_app (name, app_url, icon) VALUES (?, ?, ?)"
cursor.executemany(insert_query, data_to_insert)

# Commit the changes
conn.commit()

# Close the connection
conn.close()
