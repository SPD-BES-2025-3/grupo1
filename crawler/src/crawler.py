import asyncio
import json
import logging
from typing import List, Optional, Dict, Any

from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser, Node

from listing_validator import Listing


class crawler(client : AsyncSession, url, ):
    self



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

    # --- Scraping Functions ---
    async def fetch_with_retry(client: AsyncSession, url: str, max_retries: int = MAX_RETRIES) -> Optional[str]:
        """Fetch a URL with retry logic."""
        for attempt in range(max_retries + 1):
            try:
                response = await client.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}")
                if attempt == max_retries:
                    return None
                await asyncio.sleep(REQUEST_DELAY * (2 ** attempt))
        
        return None

    async def scrape_listings_page(client: AsyncSession, url: str) -> List[Listing]:
        """Scrape a page of listings."""
        listings = []
        logger.info(f"Fetching listings page: {url}")
        
        html_content = await fetch_with_retry(client, url)

        with open('output.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

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

    async def enrich_listing(client: AsyncSession, listing: Listing, semaphore: asyncio.Semaphore) -> Listing:
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