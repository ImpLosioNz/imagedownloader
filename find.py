import os
import time
import random
import argparse
import requests
import re
from urllib.parse import quote_plus, urlencode

def read_filenames_from_txt(file_path):
    """Read filenames from a text file, one filename per line."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def get_user_agent():
    """Return a random user agent string."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15"
    ]
    return random.choice(user_agents)

def download_image(url, output_path):
    """Download an image from the URL and save it to the output path."""
    try:
        # Add delay to avoid being detected as a bot
        time.sleep(random.uniform(0.5, 2.0))
        
        response = requests.get(
            url, 
            stream=True, 
            headers={
                'User-Agent': get_user_agent(),
                'Referer': 'https://www.google.com/'
            },
            timeout=10
        )
        response.raise_for_status()
        
        # Check if the content type is an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"Warning: URL does not point to an image. Content-Type: {content_type}")
            # Try to download anyway
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Very basic validation - check if file exists and has size > 0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True
        else:
            print(f"Downloaded file {output_path} is empty or invalid")
            if os.path.exists(output_path):
                os.remove(output_path)
            return False
            
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def search_bing_images(search_term, max_images=1):
    """Search Bing Images for a term and return image URLs."""
    print(f"Searching Bing Images for: {search_term}")
    
    # Construct Bing Images search URL
    base_url = "https://www.bing.com/images/search"
    params = {
        "q": search_term,
        "form": "HDRSC2",
        "first": 1
    }
    search_url = f"{base_url}?{urlencode(params)}"
    
    try:
        # Send request to Bing Images
        headers = {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Extract image URLs using regex
        content = response.text
        # Look for image URLs in the page content
        img_pattern = r'murl&quot;:&quot;(https?://[^&]+)&quot;'
        matches = re.findall(img_pattern, content)
        
        # Deduplicate and clean URLs
        image_urls = []
        for url in matches:
            url = url.replace('\\', '')
            if url not in image_urls:
                image_urls.append(url)
                
        print(f"Found {len(image_urls)} image URLs")
        return image_urls[:max_images]
        
    except Exception as e:
        print(f"Error searching Bing Images: {e}")
        return []

def search_google_images(search_term, max_images=1):
    """Search Google Images for a term and return image URLs."""
    print(f"Searching Google Images for: {search_term}")
    
    try:
        # Construct Google Images search URL
        search_url = f"https://www.google.com/search?q={quote_plus(search_term)}&tbm=isch"
        
        response = requests.get(
            search_url, 
            headers={
                'User-Agent': get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        response.raise_for_status()
        
        # Try to extract image URLs using various patterns
        content = response.text
        
        # Pattern for higher quality images
        pattern1 = r'imgurl=([^&]+)&'
        matches1 = re.findall(pattern1, content)
        
        # Pattern for thumbnail images
        pattern2 = r'src="(https://encrypted-tbn0.gstatic.com/images[^"]+)"'
        matches2 = re.findall(pattern2, content)
        
        # Combine and deduplicate
        image_urls = []
        
        # First try the higher quality images
        for url in matches1:
            decoded_url = url.replace('%3A', ':').replace('%2F', '/')
            if decoded_url not in image_urls:
                image_urls.append(decoded_url)
                if len(image_urls) >= max_images:
                    break
        
        # If we don't have enough, add thumbnails
        if len(image_urls) < max_images:
            for url in matches2:
                if url not in image_urls:
                    image_urls.append(url)
                    if len(image_urls) >= max_images:
                        break
        
        print(f"Found {len(image_urls)} image URLs from Google")
        return image_urls[:max_images]
        
    except Exception as e:
        print(f"Error searching Google Images: {e}")
        return []

def search_and_download_image(filename, output_dir):
    """Search for a single image and download it using the exact filename from the text file."""
    # Define the search term as the filename (without extension if present)
    search_term = os.path.splitext(filename)[0]
    print(f"\nProcessing: {filename}")
    print(f"Using search term: {search_term}")
    
    # Get file extension if present, otherwise default to .jpg
    _, file_ext = os.path.splitext(filename)
    if not file_ext:
        file_ext = '.jpg'
    
    # Define the output path with the exact filename
    output_path = os.path.join(output_dir, filename)
    
    # Try to find an image URL
    image_url = None
    
    # Try Bing first
    bing_urls = search_bing_images(search_term, 1)
    if bing_urls:
        image_url = bing_urls[0]
        print(f"Using image from Bing")
    
    # If Bing failed, try Google
    if not image_url:
        google_urls = search_google_images(search_term, 1)
        if google_urls:
            image_url = google_urls[0]
            print(f"Using image from Google")
    
    # If we found an image URL, download it
    if image_url:
        print(f"Downloading image to: {output_path}")
        success = download_image(image_url, output_path)
        if success:
            print(f"Successfully downloaded image for: {filename}")
            return 1
        else:
            print(f"Failed to download image for: {filename}")
            return 0
    else:
        print(f"Could not find any images for: {filename}")
        return 0

def main():
    parser = argparse.ArgumentParser(description='Download images with exact filenames from a text file')
    parser.add_argument('input_file', help='Text file containing filenames, one per line')
    parser.add_argument('--output-dir', default='downloads', help='Directory to save downloaded images')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Read filenames from text file
    filenames = read_filenames_from_txt(args.input_file)
    
    if not filenames:
        print(f"No filenames found in {args.input_file}")
        return
    
    print(f"Found {len(filenames)} filenames in {args.input_file}")
    
    # Process each filename
    total_downloads = 0
    for filename in filenames:
        downloaded = search_and_download_image(filename, args.output_dir)
        total_downloads += downloaded
        
        # Add delay between searches to avoid getting blocked
        if filename != filenames[-1]:  # If not the last filename
            delay = random.uniform(2.0, 5.0)
            print(f"Waiting {delay:.2f} seconds before next search...")
            time.sleep(delay)
    
    print(f"\nDownload complete! Downloaded {total_downloads}/{len(filenames)} images.")

if __name__ == "__main__":
    main()