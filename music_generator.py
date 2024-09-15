import requests
import time

SUNO_API_URL = "https://studio-api.suno.ai/api/external/generate"
SUNO_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

def generate_music(description, tempo, tags=""):
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Include tempo in the description and tags
    full_description = f"{description} with a {tempo} bpm tempo"
    full_tags = f"{tags}, {tempo} bpm" if tags else f"{tempo} bpm"
    
    data = {
        "gpt_description_prompt": full_description,
        "tags": full_tags,
        "mv": "chirp-v3-5"
    }
    
    response = requests.post(SUNO_API_URL, headers=headers, json=data)
    response.raise_for_status()
    
    generation_id = response.json()["id"]
    return generation_id

def check_generation_status(generation_id):
    status_url = f"https://studio-api.suno.ai/api/external/clips/?ids={generation_id}"
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}"
    }
    
    while True:
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        
        clip_info = response.json()[0]
        status = clip_info["status"]
        
        if status == "complete":
            return clip_info["audio_url"]
        elif status == "error":
            raise Exception("Generation failed")
        
        time.sleep(10)  # Wait 10 seconds before checking again

# Example usage
description = "A upbeat pop song about summer"
tempo = 120
tags = "pop, electronic"

try:
    generation_id = generate_music(description, tempo, tags)
    print(f"Generation started. ID: {generation_id}")
    
    audio_url = check_generation_status(generation_id)
    print(f"Music generated successfully. Audio URL: {audio_url}")
except Exception as e:
    print(f"An error occurred: {str(e)}")