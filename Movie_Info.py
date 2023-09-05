import requests
from bs4 import BeautifulSoup
import sqlite3
from twilio.rest import Client

# Function to scrape the website for new releases
def scrape_website():

    # URL of the website to scrape (modify this to your target website)
    url = "https://example.com/movies"
    
    # Send an HTTP GET request to the website
    response = requests.get(url)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract relevant information
    new_releases = []
    
    # Example: Extract movie titles and release dates
    for movie_element in soup.find_all('div', class_='movie'):
        title = movie_element.find('h2').text
        release_date = movie_element.find('span', class_='release-date').text
        imdb_id = movie_element.find('a', class_='imdb-link')['href'].split('/')[-1]
        
        new_releases.append({
            'title': title,
            'release_date': release_date,
            'imdb_id': imdb_id
        })
    
    # Now, new_releases contains the scraped movie and TV show data

# OMDb API key (replace with your actual API key)
api_key = 'YOUR_IMDB_API_KEY'

# Function to fetch movie information from IMDb API
def fetch_movie_info(imdb_id):
    url = f"http://www.imdbapi.com/?i={imdb_id}&apikey={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    # Extract relevant information
    title = data['Title']
    rating = data['imdbRating']
    plot = data['Plot']
    
    return {
        'title': title,
        'rating': rating,
        'plot': plot
    }

# Twilio Account SID and Auth Token (replace with your actual credentials)
account_sid = 'YOUR_ACCOUNT_SID'
auth_token = 'YOUR_AUTH_TOKEN'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Function to send Twilio notifications
def send_notification(message):
    # Replace 'from_' and 'to' with your Twilio phone numbers
    message = client.messages.create(
        body=message,
        from_='YOUR_TWILIO_PHONE_NUMBER',
        to='RECIPIENT_PHONE_NUMBER'
    )

    print(f"Notification sent with SID: {message.sid}")

# Main program
if __name__ == "__main__":
    # Set up database connection
    conn = sqlite3.connect('movie_database.db')
    cursor = conn.cursor()

    # Check for new releases
    new_releases = scrape_website()

    for release in new_releases:
        # Check if the release is already in the database
        # If not, fetch IMDb info and send a notification
        if not check_if_in_database(release):
            imdb_info = fetch_movie_info(release['imdb_id'])
            insert_into_database(release, imdb_info)
            send_notification(f"New release: {release['title']}")

    # Close database connection
    conn.close()
