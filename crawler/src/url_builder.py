import config

# URL Builder Class
class ImovelURLBuilder:
    """
    A class to build URLs for the 62imoveis.com.br website.
    """
    
    BASE_URL = config.BASE_URL
    
    LISTING_TYPES = {
        "ALUGUEL": "aluguel",
        "IMOVEL NOVO": "lancamento",
        "TEMPORADA": "temporada",
        "VENDA": "venda"
    }
    
    def __init__(
        self,
        type_listing: str = "venda",
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