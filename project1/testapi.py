import requests
def main():
    key = "nTn90wDOHmwT53AyuhZNg"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": "1416505016"})
    avg_rating = res.json()['books'][0]['average_rating']
    no_of_ratings = res.json()['books'][0]['work_ratings_count']

if __name__ == '__main__':
    main()
