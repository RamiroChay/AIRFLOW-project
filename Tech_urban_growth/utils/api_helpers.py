import requests
import logging

def fetch_api_json(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"API call failed with status {response.status_code} for URL: {url}")
            return None
    except Exception as e:
        logging.error(f"Error fetching API data from {url}: {e}")
        return None
    
country_codes = "ARG;ATG;BHS;BRB;BLZ;BOL;BRA;CAN;CHL;COL;CRI;CUB;DMA;DOM;ECU;SLV;GRD;GTM;GUY;HTI;HND;JAM;MEX;NIC;PAN;PRY;PER;KNA;LCA;VCT;SUR;TTO;URY;USA;VEN"

capital_coords = {
    "ARG": {"city": "Buenos Aires", "lat": -34.6037, "lon": -58.3816},
    "ATG": {"city": "St. John's", "lat": 17.1274, "lon": -61.8468},
    "BHS": {"city": "Nassau", "lat": 25.0443, "lon": -77.3504},
    "BRB": {"city": "Bridgetown", "lat": 13.0975, "lon": -59.6167},
    "BLZ": {"city": "Belmopan", "lat": 17.2510, "lon": -88.7590},
    "BOL": {"city": "Sucre", "lat": -19.0196, "lon": -65.2619},
    "BRA": {"city": "Brasilia", "lat": -15.8267, "lon": -47.9218},
    "CAN": {"city": "Ottawa", "lat": 45.4215, "lon": -75.6999},
    "CHL": {"city": "Santiago", "lat": -33.4489, "lon": -70.6693},
    "COL": {"city": "Bogotá", "lat": 4.7110, "lon": -74.0721},
    "CRI": {"city": "San José", "lat": 9.9281, "lon": -84.0907},
    "CUB": {"city": "Havana", "lat": 23.1136, "lon": -82.3666},
    "DMA": {"city": "Roseau", "lat": 15.3092, "lon": -61.3794},
    "DOM": {"city": "Santo Domingo", "lat": 18.4861, "lon": -69.9312},
    "ECU": {"city": "Quito", "lat": -0.1807, "lon": -78.4678},
    "SLV": {"city": "San Salvador", "lat": 13.6929, "lon": -89.2182},
    "GRD": {"city": "St. George's", "lat": 12.0561, "lon": -61.7488},
    "GTM": {"city": "Guatemala City", "lat": 14.6349, "lon": -90.5069},
    "GUY": {"city": "Georgetown", "lat": 6.8013, "lon": -58.1551},
    "HTI": {"city": "Port-au-Prince", "lat": 18.5944, "lon": -72.3074},
    "HND": {"city": "Tegucigalpa", "lat": 14.0723, "lon": -87.1921},
    "JAM": {"city": "Kingston", "lat": 17.9712, "lon": -76.7936},
    "MEX": {"city": "Ciudad de México", "lat": 19.4326, "lon": -99.1332},
    "NIC": {"city": "Managua", "lat": 12.1140, "lon": -86.2362},
    "PAN": {"city": "Panama City", "lat": 8.9824, "lon": -79.5199},
    "PRY": {"city": "Asunción", "lat": -25.2637, "lon": -57.5759},
    "PER": {"city": "Lima", "lat": -12.0464, "lon": -77.0428},
    "KNA": {"city": "Basseterre", "lat": 17.3026, "lon": -62.7177},
    "LCA": {"city": "Castries", "lat": 14.0101, "lon": -60.9875},
    "VCT": {"city": "Kingstown", "lat": 13.1600, "lon": -61.2248},
    "SUR": {"city": "Paramaribo", "lat": 5.8520, "lon": -55.2038},
    "TTO": {"city": "Port of Spain", "lat": 10.6549, "lon": -61.5019},
    "URY": {"city": "Montevideo", "lat": -34.9011, "lon": -56.1645},
    "USA": {"city": "Washington", "lat": 38.9072, "lon": -77.0369},
    "VEN": {"city": "Caracas", "lat": 10.4806, "lon": -66.9036}
}