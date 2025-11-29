"""
WhoisXML API client for domain lookups
"""
import requests
from config import Config


class WhoisClient:
    """Client for interacting with WhoisXML API"""
    
    def __init__(self):
        self.api_key = Config.WHOISXML_API_KEY
        self.api_url = Config.WHOISXML_API_URL
        
    def search_domain(self, domain):
        """
        Search for domain information using WhoisXML API
        
        Args:
            domain (str): Domain name to search
            
        Returns:
            dict: Domain information or error message
        """
        # Check if API key is configured
        if not Config.validate_api_key():
            return {
                'success': False,
                'error': 'API key not configured',
                'message': 'Domain information not found. Please configure your WhoisXML API key.'
            }
        
        try:
            # Prepare API request
            params = {
                'apiKey': self.api_key,
                'domainName': domain,
                'outputFormat': 'JSON'
            }
            
            # Make API request
            response = requests.get(
                self.api_url,
                params=params,
                timeout=10
            )
            
            # Check response status
            if response.status_code == 200:
                data = response.json()
                
                # Check if domain data exists
                if 'WhoisRecord' in data:
                    return {
                        'success': True,
                        'data': self._parse_whois_data(data['WhoisRecord'])
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No data found',
                        'message': f'Domain information not found for {domain}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'message': 'Unable to retrieve domain information. Please try again later.'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'message': 'Request timed out. Please try again.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Network error occurred. Please check your connection.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'An unexpected error occurred. Please try again.'
            }
    
    def _parse_whois_data(self, whois_record):
        """
        Parse WhoisXML API response into readable format
        
        Args:
            whois_record (dict): Raw WHOIS record from API
            
        Returns:
            dict: Parsed domain information
        """
        parsed_data = {
            'domain_name': whois_record.get('domainName', 'N/A'),
            'registrar': whois_record.get('registrarName', 'N/A'),
            'created_date': whois_record.get('createdDate', 'N/A'),
            'updated_date': whois_record.get('updatedDate', 'N/A'),
            'expires_date': whois_record.get('expiresDate', 'N/A'),
            'status': whois_record.get('status', 'N/A'),
        }
        
        # Extract registrant information if available
        if 'registrant' in whois_record:
            registrant = whois_record['registrant']
            parsed_data['registrant'] = {
                'name': registrant.get('name', 'N/A'),
                'organization': registrant.get('organization', 'N/A'),
                'country': registrant.get('country', 'N/A'),
                'email': registrant.get('email', 'N/A')
            }
        
        # Extract name servers if available
        if 'nameServers' in whois_record:
            name_servers = whois_record['nameServers']
            if isinstance(name_servers, dict):
                parsed_data['name_servers'] = name_servers.get('hostNames', [])
            elif isinstance(name_servers, list):
                parsed_data['name_servers'] = name_servers
        
        return parsed_data
