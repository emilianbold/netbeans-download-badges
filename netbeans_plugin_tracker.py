#!/usr/bin/env python3
"""
Script to track download counts for NetBeans plugin
Saves timestamp and download count to CSV file
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# Configuration
PLUGIN_URL = "https://plugins.netbeans.apache.org/catalogue/?id=118"
CSV_FILE = "plugin_downloads.csv"

def fetch_download_count(url):
    """
    Fetch the page and extract the download count
    Returns the download count as an integer
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <i> element with class "fa-download" or "fas fa-download"
        download_icon = soup.find('i', class_='fa-download')

        if not download_icon:
            raise ValueError("Could not find download icon on page")

        # Get the parent <p> element
        p_element = download_icon.parent

        # Extract the text and parse the number after the download icon
        text = p_element.get_text()

        # Split by the download icon and get the number after it
        parts = text.split('download')
        if len(parts) < 2:
            # Try alternative approach - get all text and find number after icon
            # Get the text content after the download icon
            download_text = download_icon.next_sibling
            if download_text:
                # Extract just the number
                count = ''.join(filter(str.isdigit, str(download_text)))
                if count:
                    return int(count)

        # Alternative: find all numbers in the paragraph and take the last one
        numbers = []
        for part in text.split():
            cleaned = part.strip()
            if cleaned.isdigit():
                numbers.append(int(cleaned))

        if numbers:
            # The download count should be the last number in the paragraph
            return numbers[-1]

        raise ValueError(f"Could not extract download count from: {text}")

    except requests.RequestException as e:
        raise Exception(f"Error fetching URL: {e}")
    except Exception as e:
        raise Exception(f"Error parsing page: {e}")

def save_to_csv(timestamp, download_count, csv_file):
    """
    Save timestamp and download count to CSV file
    Creates file with headers if it doesn't exist
    """
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write header if file is new
        if not file_exists:
            writer.writerow(['timestamp', 'download_count'])

        # Write data
        writer.writerow([timestamp, download_count])

def main():
    """Main function"""
    try:
        print(f"Fetching download count from {PLUGIN_URL}...")
        download_count = fetch_download_count(PLUGIN_URL)

        timestamp = datetime.now().isoformat()

        print(f"Download count: {download_count}")
        print(f"Timestamp: {timestamp}")

        save_to_csv(timestamp, download_count, CSV_FILE)
        print(f"Data saved to {CSV_FILE}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
