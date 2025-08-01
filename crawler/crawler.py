import asyncio
import json
import logging
from typing import List, Optional, Dict, Any

import httpx
from pydantic import BaseModel, Field, ValidationError, field_validator
from selectolax.parser import HTMLParser, Node

# --- Configuration ---
BASE_URL = "https://www.62imoveis.com.br"
MAX_CONCURRENT_REQUESTS = 5  
REQUEST_DELAY = 0.5 
REQUEST_TIMEOUT = 20 
MAX_RETRIES = 3  
DEBUG_MODE = False 

# URL Builder Class
class ImovelURLBuilder:
    """
    A class to build URLs for the 62imoveis.com.br website.
    """
    
    BASE_URL = "https://www.62imoveis.com.br"
    
    LISTING_TYPES = {
        "ALUGUEL": "aluguel",
        "IMOVEL NOVO": "lancamento",
        "TEMPORADA": "temporada",
        "VENDA": "venda"
    }
    
    def __init__(
        self,
        type_listing: str = "aluguel",
        state: str = "go",
        city: str = "todos",
        bedrooms: int = None,
        keyword: str = None,
        min_price: int = None,
        max_price: int = None,
        property_type: str = None
    ):
        """
        Initialize the URL builder with search parameters.
        """
        # Convert listing type if it matches one of the dropdown options
        self.type_listing = self.LISTING_TYPES.get(type_listing.upper(), type_listing.lower())
        self.state = state.lower()
        self.city = city.lower() if city else "todos"
        self.bedrooms = bedrooms
        self.keyword = keyword
        self.min_price = min_price
        self.max_price = max_price
        self.property_type = property_type
    
    def build_url(self) -> str:
        """
        Build and return the complete URL for the search query.
        """
        # Build the base path
        path_parts = [
            self.type_listing,
            self.state,
            self.city,
        ]
        
        # Add property type if specified, otherwise use "imoveis"
        if self.property_type:
            path_parts.append(self.property_type.lower())
        else:
            path_parts.append("imoveis")
            
        # Add bedrooms if specified
        if self.bedrooms:
            if self.bedrooms >= 5:
                path_parts.append("5+-quartos")
            else:
                path_parts.append(f"{self.bedrooms}-quartos")
        
        # Join the path parts
        path = "/".join(path_parts)
        url = f"{self.BASE_URL}/{path}"
        
        # Add query parameters if specified
        query_params = []
        
        if self.keyword:
            query_params.append(f"palavrachave={self.keyword}")
        
        if self.min_price:
            query_params.append(f"valorinicial={self.min_price}")
        
        if self.max_price:
            query_params.append(f"valorfinal={self.max_price}")
        
        # Add query parameters to URL if there are any
        if query_params:
            url += "?" + "&".join(query_params)
        
        return url

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scraper.log", mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# --- Pydantic Models ---
class ListingUnit(BaseModel):
    """Represents a specific unit/plant within a listing."""
    description: Optional[str] = None
    image_url: Optional[str] = None

    @field_validator('image_url', mode='before')
    @classmethod
    def validate_unit_url(cls, value):
        if isinstance(value, str):
            if not value.startswith(('http://', 'https://')):
                return None
            try:
                return value
            except ValidationError:
                logger.warning(f"Invalid unit image URL skipped: {value}")
                return None
        return value


class Listing(BaseModel):
    """Represents a single real estate listing."""
    # --- Fields from Listing Page ---
    url: Optional[str] = Field(None, description="Full URL to the listing details page")
    image_url: Optional[str] = Field(None, description="URL of the main listing image from list view")
    address_line1: Optional[str] = Field(None, description="Main address line (e.g., street)")
    address_line2: Optional[str] = Field(None, description="Secondary address line (e.g., neighborhood, city)")
    title: Optional[str] = Field(None, description="A short title or catchphrase for the listing")
    property_type_area: Optional[str] = Field(None, description="Description of property type and area range")
    price: Optional[str] = Field(None, description="Listing price (raw text)")
    price_per_m2: Optional[str] = Field(None, description="Price per square meter, if available")
    area: Optional[str] = Field(None, description="Area of the property")
    bedrooms: Optional[str] = Field(None, description="Number of bedrooms")
    suites: Optional[str] = Field(None, description="Number of suites")
    parking_spaces: Optional[str] = Field(None, description="Number of parking spaces ('Vagas')")
    plants: Optional[str] = Field(None, description="Number of floor plans available ('Plantas')")
    description_short: Optional[str] = Field(None, alias="description", description="Short description text from list view")
    advertiser_name: Optional[str] = Field(None, description="Name of the advertiser/agency")
    advertiser_creci: Optional[str] = Field(None, description="Advertiser's CRECI number")
    listing_id: Optional[str] = Field(None, description="Internal ID from the favorite button")

    # --- Fields from Detail Page (Enrichment) ---
    gallery_images: List[str] = Field(default_factory=list, description="List of image URLs from the detail page gallery")
    property_code: Optional[str] = Field(None, description="The 'Código' found in the details section")
    last_updated: Optional[str] = Field(None, description="The 'Última Atualização' date")
    full_description: Optional[str] = Field(None, description="Longer text from the 'Descrição' section")
    construction_phase: Optional[str] = Field(None, description="'Fase' from the 'Unidades do Empreendimento' section")
    units: List[ListingUnit] = Field(default_factory=list, description="Details about different available units/plants")
    characteristics: List[str] = Field(default_factory=list, description="List of features from the 'Características' section")
    whatsapp_share_link: Optional[str] = Field(None, description="The link for sharing via WhatsApp")
    days_published: Optional[str] = Field(None, description="Days the listing has been published")

    @field_validator('url', 'image_url', 'whatsapp_share_link', mode='before')
    @classmethod
    def validate_url_field(cls, value): 
        if isinstance(value, str):
            if not value.startswith(('http://', 'https://')):
                if value.startswith('/'):
                    base = BASE_URL.rstrip('/')
                    val = value.lstrip('/')
                    return f"{base}/{val}"
                logger.warning(f"Potentially invalid URL format: {value}")
                return None
            try:
                return value
            except ValidationError:
                logger.warning(f"Invalid URL skipped: {value}")
                return None
        return value

    @field_validator('gallery_images', mode='before')
    @classmethod
    def validate_gallery_urls(cls, value):
        if isinstance(value, list):
            validated_urls = []
            for url_str in value:
                if isinstance(url_str, str):
                    if not url_str.startswith(('http://', 'https://')):
                        logger.warning(f"Invalid gallery URL (missing http/s): {url_str}")
                        continue
                    try:
                        validated_urls.append(url_str)
                    except ValidationError:
                        logger.warning(f"Invalid gallery URL: {url_str}")
            return validated_urls
        elif value is None:
            return []
        return value

    @field_validator('price', 'price_per_m2', mode='before')
    @classmethod
    def clean_monetary_values(cls, value):
        if isinstance(value, str):
            cleaned = value.replace('R$', '').replace('Valor m²', '').replace('A partir de', '').replace('A partir', '').strip()
            if cleaned.endswith('+'):
                cleaned = cleaned[:-1]
            cleaned = cleaned.replace('.', '')
            cleaned = cleaned.replace(',', '.')
            return cleaned.strip() if cleaned else None
        return value

    class Config:
        populate_by_name = True


# --- Helper Functions ---
def safe_get_text(node: Optional[Node], strip: bool = True, separator: str = ' ') -> Optional[str]:
    """Safely extract text from an HTML node."""
    if node:
        text = node.text(strip=False, separator=separator)
        cleaned_text = ' '.join(text.split()).strip()
        return cleaned_text if cleaned_text else None
    return None

def safe_get_attribute(node: Optional[Node], attribute: str) -> Optional[str]:
    """Safely extract an attribute from an HTML node."""
    if node:
        return node.attributes.get(attribute)
    return None

# --- Browser Headers ---
def get_browser_headers() -> Dict[str, str]:
    """Return headers that mimic a real browser."""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Referer': BASE_URL + '/'
    }

# --- Scraping Functions ---
async def fetch_with_retry(client: httpx.AsyncClient, url: str, max_retries: int = MAX_RETRIES) -> Optional[str]:
    """Fetch a URL with retry logic."""
    for attempt in range(max_retries + 1):
        try:
            response = await client.get(url, timeout=REQUEST_TIMEOUT, follow_redirects=True)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e}")
            if attempt == max_retries:
                return None
            await asyncio.sleep(REQUEST_DELAY * (2 ** attempt))  # Exponential backoff
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            if attempt == max_retries:
                return None
            await asyncio.sleep(REQUEST_DELAY * (2 ** attempt))
        except asyncio.TimeoutError:
            logger.error(f"Timeout for {url}")
            if attempt == max_retries:
                return None
            await asyncio.sleep(REQUEST_DELAY * (2 ** attempt))
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            if attempt == max_retries:
                return None
            await asyncio.sleep(REQUEST_DELAY * (2 ** attempt))
    
    return None

async def scrape_listings_page(client: httpx.AsyncClient, url: str) -> List[Listing]:
    """Scrape a page of listings."""
    listings = []
    logger.info(f"Fetching listings page: {url}")
    
    html_content = await fetch_with_retry(client, url)
    if not html_content:
        logger.error(f"Failed to fetch listings page: {url}")
        return []
    
    # Parse HTML
    try:
        tree = HTMLParser(html_content)
        container = tree.css_first("#resultadoDaBuscaDeImoveis")
        
        if not container:
            logger.error("Could not find the main listings container.")
            return []
        
        listing_cards = container.css("a.new-card")
        logger.info(f"Found {len(listing_cards)} listing cards.")
        
        for card in listing_cards:
            try:
                listing_url_raw = safe_get_attribute(card, 'href')
                
                # Get image URL
                img_source = card.css_first('div.new-pic picture source[media="(min-width:781px)"]')
                if not img_source:
                    img_source = card.css_first('div.new-pic picture source')
                image_url_raw = safe_get_attribute(img_source, 'srcset')
                
                # Address
                address_node = card.css_first("h2.new-title.phrase")
                address_line1, address_line2 = None, None
                if address_node:
                    address_span = address_node.css_first("span")
                    address_line2_raw = safe_get_text(address_span)
                    full_address_text = safe_get_text(address_node)
                    if address_line2_raw and full_address_text:
                        address_line1 = full_address_text.replace(address_line2_raw, '').strip()
                        address_line2 = address_line2_raw
                    elif full_address_text:
                        address_line1 = full_address_text
                    address_line1 = address_line1.replace(',', '').strip() if address_line1 else None
                
                # Title
                title = safe_get_text(card.css_first("h3.new-simple.phrase"))
                if not title:
                    title = safe_get_text(card.css_first("h3.new-subtitle.phrase"))
                
                property_type_area = safe_get_text(card.css_first("h3.new-desc.phrase"))
                
                # Price
                price_node = card.css_first("div.new-price h4 span")
                if not price_node:
                    price_node = card.css_first("div.new-price h4")
                price = safe_get_text(price_node)
                
                price_nodes = card.css("div.new-price h4")
                price_per_m2 = None
                if len(price_nodes) > 1:
                    raw_ppm2 = safe_get_text(price_nodes[1])
                    if raw_ppm2:
                        price_per_m2 = raw_ppm2
                
                # Property details
                area, bedrooms, suites, parking, plants = None, None, None, None, None
                details_ul = card.css_first("ul.new-details-ul")
                if details_ul:
                    for li in details_ul.css("li"):
                        text = safe_get_text(li)
                        if not text:
                            continue
                        text_lower = text.lower()
                        if "m²" in text:
                            area = text
                        elif "quarto" in text_lower:
                            bedrooms = text
                        elif "suíte" in text_lower:
                            suites = text
                        elif "vaga" in text_lower:
                            parking = text
                        elif "planta" in text_lower:
                            plants = text
                
                description_short = safe_get_text(card.css_first("div.new-text.phrase"))
                
                # Advertiser info
                advertiser_img = card.css_first("div.new-anunciante img")
                advertiser_name = safe_get_attribute(advertiser_img, 'alt')
                advertiser_creci = safe_get_text(card.css_first("div.new-anunciante div.creci p"))
                
                # Listing ID
                fav_span = card.css_first("span.favorito-resultado-busca")
                listing_id = safe_get_attribute(fav_span, 'data-id')
                
                # Create listing object
                listing_data = Listing(
                    url=listing_url_raw,
                    image_url=image_url_raw,
                    address_line1=address_line1,
                    address_line2=address_line2,
                    title=title,
                    property_type_area=property_type_area,
                    price=price,
                    price_per_m2=price_per_m2,
                    area=area,
                    bedrooms=bedrooms,
                    suites=suites,
                    parking_spaces=parking,
                    plants=plants,
                    description_short=description_short,
                    advertiser_name=advertiser_name,
                    advertiser_creci=advertiser_creci,
                    listing_id=listing_id,
                )
                listings.append(listing_data)
                
            except ValidationError as e:
                logger.warning(f"Validation error creating listing: {e}")
            except Exception as e:
                logger.warning(f"Error processing listing card: {e}")
    
    except Exception as e:
        logger.error(f"Error parsing listings page: {e}", exc_info=True)
    
    logger.info(f"Extracted {len(listings)} listings from page.")
    return listings

async def enrich_listing(client: httpx.AsyncClient, listing: Listing, semaphore: asyncio.Semaphore) -> Listing:
    """Enrich a listing with details from its detail page."""
    if not listing.url:
        logger.warning(f"Skipping enrichment for listing ID {listing.listing_id}: No URL found.")
        return listing
    
    url_str = str(listing.url)
    
    # Use semaphore to limit concurrent requests
    async with semaphore:
        logger.info(f"Enriching listing ID: {listing.listing_id}")
        
        # Add delay between requests
        await asyncio.sleep(REQUEST_DELAY)
        
        html_content = await fetch_with_retry(client, url_str)
        if not html_content:
            logger.error(f"Failed to fetch detail page for listing {listing.listing_id}")
            return listing
        
        try:
            tree = HTMLParser(html_content)
            main_content = tree.css_first(".col-md-9 > .pr-md-2.aumentar-tela")
            
            if not main_content:
                main_content = tree.css_first(".col-md-9")
                if not main_content:
                    logger.warning(f"Could not find content area for listing {listing.listing_id}")
                    return listing
            
            # Gallery Images
            gallery_imgs = main_content.css('#image-carousel .swiper-slide:not(.swiper-slide-duplicate) img')
            gallery_urls_raw = [safe_get_attribute(img, 'src') or safe_get_attribute(img, 'data-flickity-lazyload') 
                              for img in gallery_imgs if img is not None]
            gallery_urls_filtered = [url for url in gallery_urls_raw if url and url.startswith(('http://', 'https://'))]
            
            try:
                listing.gallery_images = gallery_urls_filtered
            except ValidationError:
                logger.warning(f"Error validating gallery images for listing {listing.listing_id}")
            
            # Details Section
            for details_container in main_content.css('.col-md-12.bg-white.shadow.mt-2.pb-2'):
                h5 = details_container.css_first('h5')
                if h5 and "Detalhes" in safe_get_text(h5, strip=True):
                    rows = details_container.css('.row .col-lg-6')
                    for row_div in rows:
                        h6 = row_div.css_first('h6')
                        if h6:
                            h6_text = safe_get_text(h6)
                            if h6_text:
                                small_text = safe_get_text(h6.css_first('small.text-muted'))
                                if small_text:
                                    if "código:" in h6_text.lower():
                                        listing.property_code = small_text
                                    elif "última atualização:" in h6_text.lower():
                                        listing.last_updated = small_text
            
            # Full Description
            desc_node = main_content.css_first('p.texto-descricao')
            if desc_node:
                listing.full_description = safe_get_text(desc_node)
                
            # Characteristics
            characteristics_container = main_content.css_first('#listaDeDetalhesDoImovel ul.checkboxes')
            if characteristics_container:
                char_items = characteristics_container.css('li')
                listing.characteristics = [safe_get_text(item) for item in char_items if safe_get_text(item)]
                
            logger.info(f"Successfully enriched listing ID: {listing.listing_id}")
            
        except Exception as e:
            logger.error(f"Error enriching listing {listing.listing_id}: {e}", exc_info=True)
        
    return listing

# --- Main Execution Functions ---
async def main(search_params: Dict[str, Any] = None):
    """
    Main asynchronous function.
    
    Args:
        search_params: Dictionary with search parameters for building the URL
    """
    all_listings = []
    
    # Build target URL using the ImovelURLBuilder
    if not search_params:
        search_params = {}
    
    url_builder = ImovelURLBuilder(**search_params)
    target_url = url_builder.build_url()
    logger.info(f"Using target URL: {target_url}")
    
    # Create HTTPX client with browser-like headers
    async with httpx.AsyncClient(headers=get_browser_headers(), follow_redirects=True) as client:
        try:
            # Get initial listings
            initial_listings = await scrape_listings_page(client, target_url)
            
            if not initial_listings:
                logger.error("No listings found on the main page. Exiting.")
                return
            
            # Limit listings for debugging if needed
            if DEBUG_MODE:
                working_listings = initial_listings[:5]
                logger.info(f"DEBUG MODE: Processing only 5 listings")
            else:
                working_listings = initial_listings
                
            logger.info(f"Starting enrichment for {len(working_listings)} listings...")
            
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
            
            # Create tasks for all listings
            tasks = [enrich_listing(client, listing, semaphore) for listing in working_listings]
            
            # Process all listings with asyncio.gather
            enriched_listings = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and process results
            for i, result in enumerate(enriched_listings):
                if isinstance(result, Exception):
                    logger.error(f"Error processing listing {i}: {result}")
                else:
                    all_listings.append(result)
            
            logger.info(f"Finished enrichment. Total successful listings: {len(all_listings)}")
            
            # Save to JSON file
            if all_listings:
                output_data = [listing.model_dump(mode='json', by_alias=True, exclude_none=True) for listing in all_listings]
                json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
                
                # Create a filename based on search params
                filename_parts = []
                for key, value in search_params.items():
                    if value is not None:
                        filename_parts.append(f"{key}_{value}")
                
                filename_suffix = "_".join(filename_parts)[:50] if filename_parts else "default"
                output_filename = f"listings_62imoveis_{filename_suffix}.json"
                
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(json_output)
                logger.info(f"Successfully saved data to {output_filename}")
                print(f"Successfully saved {len(all_listings)} listings to {output_filename}")
            else:
                logger.warning("No successful listings to save.")
                
        except Exception as e:
            logger.error(f"Error in main execution: {e}", exc_info=True)

if __name__ == "__main__":
    # Example usage with search parameters
    search_params = {
        "type_listing": "aluguel",
        "state": "go",
        "city": "goiania",
        #"bedrooms": 4,
        #"keyword": "jardim",
        #"min_price": 2000,
        #"max_price": 5000
    }
    
    try:
        asyncio.run(main(search_params))
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)