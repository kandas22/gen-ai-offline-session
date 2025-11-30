import re
import base64
from bs4 import BeautifulSoup

class EmailParser:
    PATTERNS = {
        'netflix': {
            'sender': 'netflix.com',
            'subject': ['payment', 'receipt', 'invoice'],
            'cost_pattern': r'(\$|£|€)\s*(\d+\.\d{2})',
            'date_pattern': r'\d{1,2}\s+[A-Za-z]+\s+\d{4}'
        },
        'spotify': {
            'sender': 'spotify.com',
            'subject': ['receipt', 'payment'],
            'cost_pattern': r'Total\s+(\$|£|€)(\d+\.\d{2})',
            'date_pattern': r'\d{4}-\d{2}-\d{2}'
        },
        # Add more patterns here
    }

    def parse_email(self, message):
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        
        body = self._get_body(payload)
        
        service = self._detect_service(sender, subject)
        if not service:
            return None
            
        data = self._extract_data(body, service)
        data['service'] = service
        data['date'] = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        return data

    def _get_body(self, payload):
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        return base64.urlsafe_b64decode(data).decode()
                elif part['mimeType'] == 'text/html':
                    # Prefer plain text but handle HTML if needed
                    pass
        elif 'body' in payload:
            data = payload['body'].get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode()
        return ""

    def _detect_service(self, sender, subject):
        for service, patterns in self.PATTERNS.items():
            if patterns['sender'] in sender.lower():
                for subj_pattern in patterns['subject']:
                    if subj_pattern in subject.lower():
                        return service
        return None

    def _extract_data(self, body, service):
        patterns = self.PATTERNS.get(service)
        if not patterns:
            return {}
            
        cost_match = re.search(patterns['cost_pattern'], body)
        cost = cost_match.group(2) if cost_match else None
        currency = cost_match.group(1) if cost_match else None
        
        return {
            'cost': float(cost) if cost else 0.0,
            'currency': currency
        }
