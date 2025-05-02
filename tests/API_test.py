import requests

def fetch_book_info(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'isbn:{isbn}',
        'key': 'AIzaSyCvcWCBabVuFWg8UDaSQ3XRXy-XNavZC-k'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()
        if results['totalItems'] == 0:
            return "No results found."
        book = results['items'][0]['volumeInfo']
        title = book.get('title', 'No title available')
        authors = book.get('authors', ['No authors listed'])
        return f"Title: {title}, Author: {', '.join(authors)}"
    else:
        return "Failed to fetch data from Google Books API"

# Example ISBN for testing
isbn = '1472288157' 
book_details = fetch_book_info(isbn)
print(book_details)
