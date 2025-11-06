import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_wikipedia(url: str) -> tuple[str, str]:
    """
    Scrapes a Wikipedia article, cleans its content, and returns the title and clean text.
    
    Args:
        url (str): The URL of the Wikipedia article.
        
    Returns:
        tuple[str, str]: A tuple containing (article_title, cleaned_text).
    
    Raises:
        Exception: If the page cannot be fetched or content is not found.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Get the title
        title_tag = soup.find('h1', id='firstHeading')
        if not title_tag:
            raise ValueError("Could not find article title (h1#firstHeading).")
        title = title_tag.get_text()

        # 2. Get the main content
        content_div = soup.find('div', id='mw-content-text')
        if not content_div:
            raise ValueError("Could not find article content (div#mw-content-text).")

        # 3. Clean the content
        # Remove unwanted elements like references, tables, and edit links
        for tag in content_div.find_all(['sup', 'table', 'span.mw-editsection', 'div.reflist', 'div.navbox']):
            tag.decompose()
        
        # Get all paragraph texts
        paragraphs = content_div.find_all('p', recursive=False) # Get only top-level paragraphs
        
        # Concatenate paragraph text, ensuring we don't get empty strings
        cleaned_text = "\n\n".join(
            p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
        )

        if not cleaned_text:
            logger.warning(f"No paragraph text found for {url}. Falling back to full content text.")
            # Fallback if no <p> tags are direct children (less clean)
            cleaned_text = content_div.get_text(separator='\n', strip=True)

        logger.info(f"Successfully scraped title: {title}")
        return title, cleaned_text

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Error while scraping {url}: {e}")
        raise Exception(f"Failed to fetch URL: {e}")
    except Exception as e:
        logger.error(f"Error scraping content from {url}: {e}")
        raise

if __name__ == '__main__':
    # Example usage for testing
    test_url = "https://en.wikipedia.org/wiki/Alan_Turing"
    try:
        article_title, text_content = scrape_wikipedia(test_url)
        print(f"--- TITLE ---")
        print(article_title)
        print(f"\n--- CLEANED TEXT (Sample) ---")
        print(text_content[:1000] + "...")
    except Exception as e:
        print(f"Scraping failed: {e}")