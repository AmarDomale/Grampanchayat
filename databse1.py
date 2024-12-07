import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create village table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS village (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        population INTEGER,
        male_population INTEGER,
        female_population INTEGER,
        sarpanch TEXT,
        gramsevak TEXT
    )
''')

# Create members table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL
    )
''')

# Insert initial data into village table
cursor.execute('''
    INSERT INTO village (population, male_population, female_population, sarpanch, gramsevak)
    VALUES (?, ?, ?, ?, ?)
''', (1000, 500, 500, 'Sarpanch Name', 'Gramsevak Name'))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
