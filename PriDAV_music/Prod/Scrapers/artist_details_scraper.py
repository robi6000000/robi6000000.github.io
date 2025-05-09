import requests
import pandas as pd
import time
from typing import List, Dict
import os
from dotenv import load_dotenv
from tqdm import tqdm # Tracks progress within loops with a progress bar

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

# Function to fetch track info in batches of 50
# Takes a list of track IDs and returns a list of track details
def get_track_details(track_ids: List[str]) -> List[Dict]:
    track_details = []
    
    for i in tqdm(range(0, len(track_ids), 50), desc="Fetching track details"):
        batch = track_ids[i:i + 50]
        url = 'https://api.spotify.com/v1/tracks'
        params = {'ids': ','.join(batch)}
        
        while True:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                print(f"\nRate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after + 1)
                continue
                
            if response.status_code == 200:
                tracks = response.json().get('tracks', [])
                track_details.extend([t for t in tracks if t])
                break
            else:
                print(f"\nError {response.status_code}: {response.text}")
                time.sleep(1)
                break
    
    return track_details

# Function to fetch artist info in batches of 50
# Takes a list of artist IDs and returns a dictionary with artist details
def get_artist_details(artist_ids: List[str]) -> Dict[str, Dict]:
    artist_details = {}
    
    for i in tqdm(range(0, len(artist_ids), 50), desc="Fetching artist details"):
        batch = artist_ids[i:i + 50]
        url = 'https://api.spotify.com/v1/artists'
        params = {'ids': ','.join(batch)}
        
        while True:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                print(f"\nRate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after + 1)
                continue
                
            if response.status_code == 200:
                artists = response.json().get('artists', [])
                for artist in artists:
                    if artist and 'id' in artist:
                        artist_details[artist['id']] = {
                            'name': artist.get('name', ''),
                            'popularity': artist.get('popularity', 0),
                            'genres': ','.join(artist.get('genres', [])),
                            'followers': artist.get('followers', {}).get('total', 0)
                        }
                break
            else:
                print(f"\nError {response.status_code}: {response.text}")
                time.sleep(1)
                break
    
    return artist_details

# Main function to enrich track data with additional artist information
# Reads track IDs from CSV, fetches additional data, and saves it to a new CSV file
def enrich_track_data():
    input_file = os.path.join(os.path.dirname(__file__), 'Data', 'spotify_tracks_kaggle_weekly.csv')
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} tracks from {input_file}")
    
    track_ids = df['track_id'].unique().tolist()
    print(f"Found {len(track_ids)} unique tracks")
    
    track_details = get_track_details(track_ids)
    print(f"Retrieved details for {len(track_details)} tracks")
    
    all_artist_ids = set()
    for track in track_details:
        if track and track.get('artists'):
            all_artist_ids.update(artist['id'] for artist in track['artists'])
    
    print(f"Found {len(all_artist_ids)} unique artists")
    
    artist_details = get_artist_details(list(all_artist_ids))
    print(f"Retrieved details for {len(artist_details)} artists")
    
    enriched_tracks = []
    for track in track_details:
        if not track:
            continue
            
        track_artists = track.get('artists', [])
        
        track_data = {
            'track_id': track['id'],
            'track_name': track['name'],
            'artist_count': len(track_artists),
            'artist_ids': ','.join(artist['id'] for artist in track_artists),
            'artist_names': ','.join(artist['name'] for artist in track_artists),
            'artist_popularities': ','.join(str(artist_details[artist['id']]['popularity']) 
                                          for artist in track_artists if artist['id'] in artist_details),
            'artist_genres': '|'.join(artist_details[artist['id']]['genres'] 
                                    for artist in track_artists if artist['id'] in artist_details),
            'artist_followers': ','.join(str(artist_details[artist['id']]['followers']) 
                                       for artist in track_artists if artist['id'] in artist_details)
        }
        enriched_tracks.append(track_data)
    
    enriched_df = pd.DataFrame(enriched_tracks)
    
    output_file = os.path.join(os.path.dirname(__file__), 'Data', 'spotify_tracks_artist_details.csv')
    enriched_df.to_csv(output_file, index=False)
    print(f"\nSaved enriched data with {len(enriched_df)} tracks to {output_file}")
    
    return enriched_df

if __name__ == "__main__":
    enrich_track_data()
