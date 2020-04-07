import csv
import os

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    #f = open("books.csv")
    #reader = csv.reader(f)
    i = 0
    isbn_list= db.execute("SELECT isbn FROM books").fetchall()
    isbn_string_list = ""
    for item in isbn_list:
        isbn_string_list += item[0] + ","
    isbn_string_list = isbn_string_list[:-1]
    key = "nTn90wDOHmwT53AyuhZNg"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn_string_list})
    res = res.json()
    for books in res:
        try:
            work_ratings_count = str(books[0]['work_ratings_count'])
            average_rating = str(books[0]['average_rating'])
        except Exception as e:
            print(e)
            work_ratings_count = "0"
            average_rating = "no data"
        isbn_temp = books[0]['isbn']
        db.execute("UPDATE books SET average_rating = \'"+average_rating+"\' WHERE isbn = \'"+isbn_temp+"\'")
        db.execute("UPDATE books SET work_ratings_count = "+work_ratings_count+" WHERE isbn = \'" + isbn_temp + "\'")
        i += 1
        print("rating: "+average_rating+" number: "+work_ratings_count+"  "+str(i)+" out of : 5000 added")
        #print(f"Added book {title} with isbn {isbn} written by {author} in {year} to database")
    db.commit()

if __name__ == "__main__":
    main()
