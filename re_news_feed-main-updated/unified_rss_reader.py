import feedparser
import json
import pandas as pd
from typing import Dict, List, Optional
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class BaseFeedReader:
    """Base class for all RSS feed readers with common functionality"""
    
    # Class variables to be overridden by child classes
    SITE_NAME = "Generic News Site"
    JSON_LOC = 'prompts/rss_links.json'
    
    __global_rss_links: Dict[str, str] = {}
    
    def __init__(self, section_name: str):
        """Initialize the RSS feed reader for a specific section"""
        self._section = section_name
        self._feed_url = self.__global_rss_links.get(section_name)
        
        if not self._feed_url:
            available = ", ".join(self.__global_rss_links.keys())
            raise ValueError(f"No feed found for '{section_name}'. Available sections: {available}")
            
        self._feed = feedparser.parse(self._feed_url)
        
        # Check for feed parsing errors
        if self._feed.get('bozo', 0) == 1:
            error = self._feed.bozo_exception
            raise ValueError(f"Failed to parse RSS feed for {section_name}. Error: {error}")
        
        logger.info(f"Successfully initialized {self.SITE_NAME} reader for section: {section_name}")
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """Child classes must implement their own link ID extraction logic"""
        raise NotImplementedError("Child classes must implement their own link ID extraction")
    
    def get_feed_entries(self) -> pd.DataFrame:
        """Parse and return feed entries as a DataFrame"""
        if not hasattr(self._feed, 'entries') or not self._feed.entries:
            logger.warning(f"No entries found in feed for {self._section}")
            return pd.DataFrame(columns=['site_name', 'sub_site_name', 'links', 'title', 'link_id', 'link_date'])
            
        article_data = {
            'title': [],
            'links': [],
            'link_id': [],
            'link_date': []
        }
        
        for entry in self._feed.entries:
            article_data['title'].append(entry.get('title', ''))
            article_data['links'].append(entry.get('link', ''))
            
            # Use child class's implementation for link ID extraction
            link = entry.get('link', '')
            article_data['link_id'].append(self._extract_link_id(link) if link else None)
            article_data['link_date'].append(entry.get('published', None))
            
        df = pd.DataFrame(article_data)
        df.insert(0, 'site_name', self.SITE_NAME)
        df.insert(1, 'sub_site_name', self._section)
        
        logger.info(f"Found {len(df)} articles for {self._section}")
        return df
    
    @classmethod
    def load_links(cls) -> None:
        """Load RSS links from JSON file"""
        try:
            with open(cls.JSON_LOC, 'r') as fp:
                data = fp.read().strip()
            
            if not data or data in ('{}', '[]'):
                cls.__global_rss_links = {}
                logger.warning(f"Empty file at {cls.JSON_LOC}, no RSS links loaded.")
            else:
                cls.__global_rss_links = json.loads(data)
                logger.info(f"Successfully loaded {len(cls.__global_rss_links)} RSS links from {cls.JSON_LOC}")
                
        except FileNotFoundError:
            logger.error(f"File {cls.JSON_LOC} not found. Please create this file with valid RSS links.")
            cls.__global_rss_links = {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {cls.JSON_LOC}: {e}")
            cls.__global_rss_links = {}
    
    @classmethod
    def show_all_rss_links(cls) -> Dict[str, str]:
        """Return all loaded RSS links"""
        return cls.__global_rss_links
    
    @classmethod
    def get_available_feeds(cls) -> List[str]:
        """Return list of available feed names"""
        return list(cls.__global_rss_links.keys())
    
    @classmethod
    def save_links(cls) -> None:
        """Save current RSS links to JSON file"""
        with open(cls.JSON_LOC, 'w') as fp:
            json.dump(cls.__global_rss_links, fp, indent=4)
        logger.info(f"Saved {len(cls.__global_rss_links)} RSS links to {cls.JSON_LOC}")

    @classmethod
    def set_json_location(cls, new_path: str) -> None:
        """Set new location for the JSON file with RSS links"""
        cls.JSON_LOC = new_path
        logger.info(f"JSON location updated to {new_path}")

class EconomicTimesReader(BaseFeedReader):
    """Reader for Economic Times RSS feeds"""
    
    SITE_NAME = "Economic Times"
    JSON_LOC = 'prompts/et_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """ET links format: .../articleshow/121432353.cms or .../articleshow/103270989.cms
        Extract the numeric ID between /articleshow/ and .cms"""
        try:
            # Split on 'articleshow/' and then take the part before '.cms'
            return link.split('articleshow/')[1].split('.')[0]
        except (IndexError, AttributeError):
            return None

class HindustanTimesReader(BaseFeedReader):
    """Reader for Hindustan Times RSS feeds"""
    
    SITE_NAME = "Hindustan Times"
    JSON_LOC = 'prompts/tht_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """HT links format: https://www.hindustantimes.com/...-101748322371668.html
        Extract the full numeric ID (101748322371668 in this example)"""
        try:
            # Split on '-' and take last part, then remove '.html'
            return link.split('-')[-1].split('.')[0]
        except (IndexError, AttributeError):
            return None
        
class LivemintReader(BaseFeedReader):
    """Reader for Livemint RSS feeds"""
    
    SITE_NAME = "Livemint"
    JSON_LOC = 'prompts/livemint_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """Livemint links format: ...-11748332381948.html
        Extract the long numeric ID before .html"""
        try:
            # Split on '-' and take last part, then remove '.html'
            return link.split('-')[-1].split('.')[0]
        except (IndexError, AttributeError):
            return None

class TimesOfIndiaReader(BaseFeedReader):
    """Reader for Times of India RSS feeds"""
    
    SITE_NAME = "Times of India"
    JSON_LOC = 'prompts/toi_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """TOI links format: .../articleshow/118633662.cms
        Extract the numeric ID between /articleshow/ and .cms"""
        try:
            # Same logic as Economic Times
            return link.split('articleshow/')[1].split('.')[0]
        except (IndexError, AttributeError):
            return None

class TheHinduReader(BaseFeedReader):
    """Reader for The Hindu RSS feeds"""
    
    SITE_NAME = "The Hindu"
    JSON_LOC = 'prompts/th_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """The Hindu links format: .../article69620861.ece
        Extract the numeric ID between /article and .ece"""
        try:
            # Split on 'article' and then take the part before '.ece'
            return link.split('article')[-1].split('.')[0]
        except (IndexError, AttributeError):
            return None
        
class LokmatReader(BaseFeedReader):
    """Reader for Lokmat RSS feeds"""
    
    SITE_NAME = "Lokmat"
    JSON_LOC = 'prompts/lokmat_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """Lokmat links format: .../a-a653/ or .../a-a719/
        Extract the a-xxxx part before the last slash"""
        try:
            # Get the last part of URL before final slash
            last_part = link.rstrip('/').split('/')[-1]
            return last_part if last_part.startswith('a-') else None
        except (IndexError, AttributeError):
            return None
        
class AmarUjalaReader(BaseFeedReader):
    """Reader for Amar Ujala RSS feeds"""
    
    SITE_NAME = "Amar Ujala"
    JSON_LOC = 'prompts/amarujala_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """Amar Ujala links format: .../lalu-yadav-family-2025-05-27
        Extract the last 6 hyphen-separated parts"""
        try:
            # Get the last part of URL (after last slash, before any query params)
            last_part = link.split('/')[-1].split('?')[0]
            # Take the last 6 hyphen-separated components
            parts = last_part.split('-')
            return '-'.join(parts[-6:]) if len(parts) >= 6 else last_part
        except (IndexError, AttributeError):
            return None
        
class NDTVReader(BaseFeedReader):
    """Reader for NDTV RSS feeds"""
    
    SITE_NAME = "NDTV"
    JSON_LOC = 'prompts/ndtv_rss_links.json'
    
    def _extract_link_id(self, link: str) -> Optional[str]:
        """
        Extracts ID from NDTV URLs like:
        https://www.ndtv.com/...-8409222
        https://www.ndtv.com/...-8586492
        
        Returns the numeric ID at the end of the URL
        """
        try:
            # Split URL by hyphens and take the last part
            return link.split('-')[-1]
        except (IndexError, AttributeError):
            return None
        
# Example usage:
def main():
    # Initialize readers for different sources
    readers = {
        'ET': EconomicTimesReader('Economy'),
        'HT': HindustanTimesReader('Delhi'),
        'Livemint': LivemintReader('Markets'),
        'TOI': TimesOfIndiaReader('Mumbai'),
        'The Hindu': TheHinduReader('National'),
        'Lokmat': LokmatReader('Real estate'),
        'Amar Ujala': AmarUjalaReader('Delhi'),
        'NDTV': NDTVReader('India')
    }
    
    # Get and display feeds
    for name, reader in readers.items():
        try:
            df = reader.get_feed_entries()
            print(f"\n{name} News Headlines:")
            print(df[['title', 'link_date']].head(3))  # Show first 3 headlines
        except Exception as e:
            print(f"Error with {name} reader: {str(e)}")

if __name__ == "__main__":
    # Load links for all readers
    EconomicTimesReader.load_links()
    HindustanTimesReader.load_links()
    LivemintReader.load_links()
    TimesOfIndiaReader.load_links()
    TheHinduReader.load_links()
    LokmatReader.load_links()
    AmarUjalaReader.load_links()
    NDTVReader.load_links()
    
    main()