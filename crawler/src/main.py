import asyncio
import json
import logging
from typing import List, Optional, Dict, Any

from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser, Node

from pydantic import BaseModel, Field, ValidationError, field_validator

import logger
from url_builder import ImovelURLBuilder
from crawler import crawler


async def main(search_params: Dict[str, Any] = None):
    """
    Main asynchronous function.
    
    Args:
        search_params: Dictionary with search parameters for building the URL
    """
    page = 1
    all_listings = []
    
    while True:
        # Build target URL using the ImovelURLBuilder
        if not search_params:
            search_params = {}
        
        url_builder = ImovelURLBuilder(**search_params)
        target_url = url_builder.build_url() + f"?pagina={page}"
        logger.info(f"Using target URL: {target_url}")
        
        # Create HTTPX client with browser-like headers
        async with AsyncSession(impersonate="chrome") as client:
            try:
                # Get initial listings
                initial_listings = await scrape_listings_page(client, target_url)
                
                if not initial_listings:
                    logger.error("No listings found on the main page. Exiting.")
                    break
                    
                logger.info(f"Starting enrichment for {len(working_listings)} listings...")
                
                # Create semaphore to limit concurrent requests
                semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
                
                # Create tasks for all listings
                tasks = [enrich_listing(client, listing, semaphore) for listing in working_listings]
                
                # Process all listings with asyncio.gather
                enriched_listings = await asyncio.gather(*tasks, return_exceptions=True)
                page = page + 1
                # Filter out exceptions and process results
                for i, result in enumerate(enriched_listings):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing listing {i}: {result}")
                    else:
                        all_listings.append(result)
                
                logger.info(f"Finished enrichment. Total successful listings: {len(all_listings)}")
                
                # Save to JSON file
                #TODO adicionar o mongoDB aqui
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
        "type_listing": "venda",
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