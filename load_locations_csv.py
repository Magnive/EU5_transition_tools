import csv
from typing import List, Dict, Optional


class Location:
    """Represents a location/province from the CSV file."""
    
    def __init__(self, row_dict: Dict[str, str]):
        """Initialize a Location from a CSV row dictionary."""
        self.continent = row_dict.get('continent', '')
        self.superregion = row_dict.get('superregion', '')
        self.region = row_dict.get('region', '')
        self.area = row_dict.get('area', '')
        self.province = row_dict.get('province', '')
        self.location_type = row_dict.get('location_type', '')
        self.location_name = row_dict.get('location_name', '')
        self.hexcode = row_dict.get('hexcode', '')
        self.topography = row_dict.get('topography', '')
        self.vegetation = row_dict.get('vegetation', '')
        self.climate = row_dict.get('climate', '')
        self.religion = row_dict.get('religion', '')
        self.culture = row_dict.get('culture', '')
        self.raw_material = row_dict.get('raw_material', '')
        
        # Parse natural_harbor_suitability as float if present
        harbor_value = row_dict.get('natural_harbor_suitability', '')
        self.natural_harbor_suitability = float(harbor_value) if harbor_value else None
        
        self.owner = row_dict.get('owner', '')
        
        # Parse cores as a list (comma-separated values)
        cores_str = row_dict.get('cores', '')
        self.cores = [c.strip() for c in cores_str.split(',')] if cores_str else []
        
        # Parse old_province_number as int if present
        old_prov = row_dict.get('old_province_number', '')
        self.old_province_number = int(old_prov) if old_prov else None
    
    def __repr__(self):
        return f"Location(name={self.location_name}, province={self.province}, owner={self.owner})"
    
    def to_dict(self) -> Dict:
        """Convert the Location back to a dictionary."""
        return {
            'continent': self.continent,
            'superregion': self.superregion,
            'region': self.region,
            'area': self.area,
            'province': self.province,
            'location_type': self.location_type,
            'location_name': self.location_name,
            'hexcode': self.hexcode,
            'topography': self.topography,
            'vegetation': self.vegetation,
            'climate': self.climate,
            'religion': self.religion,
            'culture': self.culture,
            'raw_material': self.raw_material,
            'natural_harbor_suitability': self.natural_harbor_suitability,
            'owner': self.owner,
            'cores': self.cores,
            'old_province_number': self.old_province_number
        }


def load_locations_csv(filepath: str, encoding: str = 'utf-8') -> List[Location]:
    """
    Load location data from a CSV file and return a list of Location objects.
    
    Args:
        filepath: Path to the CSV file
        encoding: Character encoding of the file (default: 'utf-8')
        
    Returns:
        List of Location objects
    """
    locations = []
    
    with open(filepath, 'r', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            location = Location(row)
            locations.append(location)
    
    return locations


def load_locations_as_dicts(filepath: str, encoding: str = 'utf-8') -> List[Dict]:
    """
    Load location data from a CSV file and return a list of dictionaries.
    
    Args:
        filepath: Path to the CSV file
        encoding: Character encoding of the file (default: 'utf-8')
        
    Returns:
        List of dictionaries with location data
    """
    locations = []
    
    with open(filepath, 'r', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Convert natural_harbor_suitability to float if present
            if row.get('natural_harbor_suitability'):
                try:
                    row['natural_harbor_suitability'] = float(row['natural_harbor_suitability'])
                except ValueError:
                    row['natural_harbor_suitability'] = None
            
            # Convert cores to list
            if row.get('cores'):
                row['cores'] = [c.strip() for c in row['cores'].split(',')]
            else:
                row['cores'] = []
            
            # Convert old_province_number to int if present
            if row.get('old_province_number'):
                try:
                    row['old_province_number'] = int(row['old_province_number'])
                except ValueError:
                    row['old_province_number'] = None
            
            locations.append(row)
    
    return locations


def filter_locations(locations: List[Location], **filters) -> List[Location]:
    """
    Filter locations based on specified criteria.
    
    Args:
        locations: List of Location objects
        **filters: Keyword arguments for filtering (e.g., owner='F23', region='bahar_region')
        
    Returns:
        Filtered list of Location objects
    
    Example:
        filter_locations(locations, owner='F23', religion='regent_court')
    """
    filtered = locations
    
    for key, value in filters.items():
        if key == 'cores':
            # Special handling for cores (check if value is in the list)
            filtered = [loc for loc in filtered if value in loc.cores]
        elif hasattr(Location, key):
            filtered = [loc for loc in filtered if getattr(loc, key) == value]
    
    return filtered


# Example usage
if __name__ == "__main__":
    # Load locations as objects
    locations = load_locations_csv("anbennar_eu5_transition_data_locations.csv")
    
    print(f"Loaded {len(locations)} locations")
    print(f"\nFirst location: {locations[0]}")
    print(f"  - Province: {locations[0].province}")
    print(f"  - Owner: {locations[0].owner}")
    print(f"  - Cores: {locations[0].cores}")
    print(f"  - Culture: {locations[0].culture}")
    
    # Example: Find all provinces owned by F23
    f23_provinces = filter_locations(locations, owner='F23')
    print(f"\nProvinces owned by F23: {len(f23_provinces)}")
    for prov in f23_provinces[:3]:  # Show first 3
        print(f"  - {prov.location_name} ({prov.province})")
    
    # Example: Load as dictionaries instead
    locations_dict = load_locations_as_dicts("anbennar_eu5_transition_data_locations.csv")
    print(f"\nFirst location as dict keys: {list(locations_dict[0].keys())}")
