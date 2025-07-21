from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError, field_validator

import config
import logger


class Listing(BaseModel):
    """Represents a single real estate listing."""
    url: Optional[str] = Field(None, description="Full URL to the listing details page")
    
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
    plants: Optional[str] = Field(None, description="Number of floor plans available ('Plantas')") #número de imóveis na planta
    description_short: Optional[str] = Field(None, alias="description", description="Short description text from list view")
    advertiser_name: Optional[str] = Field(None, description="Name of the advertiser/agency")
    advertiser_creci: Optional[str] = Field(None, description="Advertiser's CRECI number")
    listing_id: Optional[str] = Field(None, description="Internal ID from the favorite button")

    gallery_images: List[str] = Field(default_factory=list, description="List of image URLs from the detail page gallery")
    property_code: Optional[str] = Field(None, description="The 'Código' found in the details section")
    last_updated: Optional[str] = Field(None, description="The 'Última Atualização' date")
    full_description: Optional[str] = Field(None, description="Longer text from the 'Descrição' section")
    construction_phase: Optional[str] = Field(None, description="'Fase' from the 'Unidades do Empreendimento' section") #não tá funcionando

    characteristics: List[str] = Field(default_factory=list, description="List of features from the 'Características' section")
    days_published: Optional[str] = Field(None, description="Days the listing has been published") #não tá funcionando legal

    @field_validator('url', mode='before')
    @classmethod
    def validate_url_field(cls, value): 
        if isinstance(value, str):
            if not value.startswith(('http://', 'https://')):
                if value.startswith('/'):
                    base = config.BASE_URL.rstrip('/')
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