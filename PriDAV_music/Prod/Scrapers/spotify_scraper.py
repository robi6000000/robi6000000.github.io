import requests
import pandas as pd
import time
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Spotify API authentication
auth_url = "https://accounts.spotify.com/api/token"
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
    'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET')
}

print("Getting access token...")
auth_response = requests.post(auth_url, data=auth_data)
print(f"Auth response status: {auth_response.status_code}")

token_data = auth_response.json()
access_token = token_data.get('access_token')

if not access_token:
    raise ValueError("Failed to get access token")

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Function to fetch all tracks from a Spotify playlist in batches of 100
# Takes a playlist ID and returns a list of track dictionaries
def get_playlist_tracks(playlist_id: str) -> List[Dict]:
    tracks = []
    offset = 0
    limit = 100
    
    while True:
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        params = {
            'offset': offset,
            'limit': limit,
            'fields': 'items(track(id,name,artists,album,duration_ms,explicit,popularity,restrictions,disc_number,track_number,available_markets)),total,next'
        }
        
        print(f"\nFetching playlist tracks: offset={offset}, limit={limit}")
        response = requests.get(url, headers=headers, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 1))
            time.sleep(retry_after + 1)
            continue
            
        if response.status_code != 200:
            print(f"Error getting playlist tracks: {response.text}")
            break
            
        data = response.json()
        items = data.get('items', [])
        total = data.get('total', 0)
        print(f"Got {len(items)} items from response (Total in playlist: {total})")
        
        if not items:
            print("No more items found")
            break
            
        valid_tracks = []
        for item in items:
            track = item.get('track')
            if track and track.get('id'):
                valid_tracks.append(item)
        
        tracks.extend(valid_tracks)
        print(f"Total tracks collected so far: {len(tracks)}")
        
        if len(items) < limit or offset + limit >= total:
            print("Reached end of playlist")
            break
            
        offset += limit

    print(f"Finished collecting {len(tracks)} tracks")
    return tracks

# Main function to collect track data from specified playlists
# Saves the collected data to a CSV file
def get_track_data() -> pd.DataFrame:
    playlists = ['49G54i94nAqUUsa57pHG4f']
        
    all_tracks = []
    processed_ids = set()
    
    for playlist_id in playlists:
        print(f"\nProcessing playlist: {playlist_id}")
        playlist_tracks = get_playlist_tracks(playlist_id)
        print(f"Found {len(playlist_tracks)} tracks")
        
        for item in playlist_tracks:
            track = item.get('track')
            if not track or not track.get('id') or track['id'] in processed_ids:
                continue
            
            track_data = {
                # Track Info
                'id': track['id'],
                'name': track['name'],
                'track_number': track['track_number'],
                'disc_number': track['disc_number'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'explicit': track['explicit'],
                
                # Track Artists
                'artists': ', '.join(artist['name'] for artist in track['artists']),
                'artist_ids': ', '.join(artist['id'] for artist in track['artists']),
                
                # Album Info
                'album': track['album']['name'],
                'album_total_tracks': track['album']['total_tracks'],
                'album_artists': ', '.join(artist['name'] for artist in track['album']['artists']),
                'album_artist_ids': ', '.join(artist['id'] for artist in track['album']['artists']),
                'album_release_date': track['album']['release_date'],
                
                # Availability
                'restrictions': track.get('restrictions'),
                'available_markets': track.get('available_markets')
            }
            
            all_tracks.append(track_data)
            processed_ids.add(track['id'])
    
    print(f"\nProcessing complete. Total unique tracks processed: {len(all_tracks)}")
    
    df = pd.DataFrame(all_tracks)
    output_file = os.path.join(os.path.dirname(__file__), 'spotify_tracks.csv')
    df.to_csv(output_file, index=False)
    print(f"Collected {len(df)} tracks and saved to {output_file}")
    
    return df

if __name__ == "__main__":
    get_track_data()