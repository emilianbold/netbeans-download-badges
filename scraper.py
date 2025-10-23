"""Scraper module for fetching download counts from NetBeans Plugin Portal"""
import requests
from bs4 import BeautifulSoup

class ScraperError(Exception):
    """Custom exception for scraper errors"""
    pass

def fetch_download_count(plugin_id):
    """
    Fetch download count for NetBeans plugin from plugins.netbeans.apache.org

    Args:
        plugin_id: The NetBeans plugin ID

    Returns:
        Download count as integer

    Raises:
        ScraperError: If scraping fails
    """
    url = f"https://plugins.netbeans.apache.org/catalogue/?id={plugin_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <i> element with class "fa-download"
        download_icon = soup.find('i', class_='fa-download')

        if not download_icon:
            raise ScraperError("Could not find download icon on page")

        # Get the parent <p> element
        p_element = download_icon.parent

        # Extract the text and parse the number after the download icon
        text = p_element.get_text()

        # Try to get the text content after the download icon
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

        raise ScraperError(f"Could not extract download count from: {text}")

    except requests.RequestException as e:
        raise ScraperError(f"Error fetching URL: {e}")
    except Exception as e:
        raise ScraperError(f"Error parsing page: {e}")
