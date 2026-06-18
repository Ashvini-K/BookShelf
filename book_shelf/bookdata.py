import csv
import sqlite3

# Step 1: Connect to SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect("bookshelf/bookshelfs.db")
cursor = conn.cursor()


# Step 3: Open and read the CSV file
#with open("bookshelf/books.csv", newline='', encoding='utf-8') as csvfile:
with open("bookshelf/books.csv", newline='', encoding='windows-1252') as csvfile:

   reader = csv.reader(csvfile, delimiter=';')
    
    # Skip the header row if your CSV has one
   next(reader)
    
   # cursor.execute("SELECT * FROM book;")
   # print(cursor.fetchall())


    # Step 4: Insert only the first 200 rows
   for i, row in enumerate(reader):
        if i >= 200:
            break
        cleaned_row = [field.strip('"') for field in row[:8]]
        
        cursor.execute("INSERT INTO book (isbn, title, author, year, publisher, image, image2, image3) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", cleaned_row)
        #cursor.execute("INSERT OR IGNORE INTO book (isbn, title, author, year, image,image2,image3) VALUES (?, ?, ?, ?, ?)",cleaned_row)


# Step 5: Commit changes and close connection
conn.commit()
conn.close()

print("Inserted 200 rows into the database.")
