"""
Enhanced BDD Test Generator - Dynamic Gherkin templates with Background support
"""
import os
import re
import uuid
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Template
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EnhancedBDDGenerator:
    """Enhanced BDD generator with dynamic Gherkin template support"""
    
    # Enhanced Feature file template with Background support
    FEATURE_TEMPLATE = """Feature: {{ feature_name }}
  {{ feature_description }}
{% if tags %}
  {{ tags }}
{% endif %}
{% if background %}

  Background:
{% for step in background %}
    {{ step }}
{% endfor %}
{% endif %}
{% for scenario in scenarios %}

  Scenario: {{ scenario.name }}
{% if scenario.tags %}
    {{ scenario.tags }}
{% endif %}
{% for step in scenario.steps %}
    {{ step }}
{% endfor %}
{% endfor %}
"""
    
    def __init__(self):
        """Initialize Enhanced BDD Generator"""
        Config.ensure_directories()
        self.feature_template = Template(self.FEATURE_TEMPLATE)
        logger.info("EnhancedBDDGenerator initialized")
    
    def parse_structured_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse structured specification (JSON format)
        
        Expected format:
        {
            "feature": "Feature name",
            "description": "Feature description",
            "tags": ["@tag1", "@tag2"],  # optional
            "background": [  # optional
                "Given common setup step",
                "And another setup step"
            ],
            "scenarios": [
                {
                    "name": "Scenario name",
                    "tags": ["@smoke"],  # optional
                    "steps": [
                        "Given I am on Google",
                        "When I search for 'rain news'",
                        "And I click the first result",
                        "Then I should see the article"
                    ]
                }
            ]
        }
        """
        logger.info("Parsing structured specification")
        
        return {
            'feature_name': spec.get('feature', 'Generated Feature'),
            'feature_description': spec.get('description', 'Auto-generated test'),
            'tags': ' '.join(spec.get('tags', [])) if spec.get('tags') else None,
            'background': spec.get('background'),
            'scenarios': [
                {
                    'name': scenario.get('name', f'Scenario {i+1}'),
                    'tags': ' '.join(scenario.get('tags', [])) if scenario.get('tags') else None,
                    'steps': scenario.get('steps', [])
                }
                for i, scenario in enumerate(spec.get('scenarios', []))
            ]
        }
    
    def parse_natural_language(self, specification: str) -> Dict[str, Any]:
        """
        Parse natural language specification
        Supports: Feature, Background, Scenario, Given, When, Then, And, But
        
        Example:
        Feature: Google Search
        Background:
          Given I open a browser
        Scenario: Search for news
          Given I am on Google
          When I search for rain news
          Then I should see results
        """
        logger.info("Parsing natural language specification")
        
        lines = [line.strip() for line in specification.split('\n') if line.strip()]
        
        feature_name = "Generated Feature"
        feature_description = ""
        background_steps = []
        scenarios = []
        current_scenario = None
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Feature line
            if line_lower.startswith('feature:'):
                feature_name = line[8:].strip()
                current_section = 'feature'
            
            # Background section
            elif line_lower.startswith('background:'):
                current_section = 'background'
                current_scenario = None
            
            # Scenario line
            elif line_lower.startswith('scenario:'):
                if current_scenario:
                    scenarios.append(current_scenario)
                current_scenario = {
                    'name': line[9:].strip(),
                    'steps': []
                }
                current_section = 'scenario'
            
            # Step lines (Given, When, Then, And, But)
            elif any(line_lower.startswith(keyword) for keyword in ['given ', 'when ', 'then ', 'and ', 'but ']):
                if current_section == 'background':
                    background_steps.append(line)
                elif current_section == 'scenario' and current_scenario:
                    current_scenario['steps'].append(line)
            
            # Description (after Feature, before Background/Scenario)
            elif current_section == 'feature' and not line_lower.startswith(('background:', 'scenario:')):
                feature_description = line
        
        # Add last scenario
        if current_scenario:
            scenarios.append(current_scenario)
        
        # If no scenarios found, try simple comma-separated format
        if not scenarios:
            return self._parse_simple_format(specification)
        
        return {
            'feature_name': feature_name,
            'feature_description': feature_description or f"Auto-generated test for {feature_name}",
            'tags': None,
            'background': background_steps if background_steps else None,
            'scenarios': scenarios
        }
    
    def _parse_simple_format(self, specification: str) -> Dict[str, Any]:
        """Parse simple comma-separated format (backward compatibility)"""
        lines = [line.strip() for line in specification.split(',') if line.strip()]
        
        steps = []
        for line in lines:
            line = line.strip()
            if not any(line.lower().startswith(kw) for kw in ['given', 'when', 'then', 'and', 'but']):
                if 'search' in line.lower() or 'click' in line.lower():
                    line = f"When {line}"
                elif 'should' in line.lower() or 'see' in line.lower():
                    line = f"Then {line}"
                else:
                    line = f"Given {line}"
            steps.append(line)
        
        feature_name = self._generate_feature_name(steps)
        
        return {
            'feature_name': feature_name,
            'feature_description': f"Auto-generated test for {feature_name}",
            'tags': None,
            'background': None,
            'scenarios': [{
                'name': f"Execute {feature_name}",
                'steps': steps
            }]
        }
    
    def _generate_feature_name(self, steps: List[str]) -> str:
        """Generate feature name from steps"""
        if not steps:
            return "Generated Test"
        
        first_step = steps[0].lower()
        words = re.findall(r'\b\w+\b', first_step)
        common_words = {'given', 'when', 'then', 'and', 'but', 'i', 'am', 'on', 'the', 'a', 'an'}
        key_words = [w for w in words if w not in common_words][:3]
        
        return ' '.join(key_words).title() or "Generated Test"
    
    def generate_feature_file(self, specification: Any, test_id: Optional[str] = None) -> Dict[str, str]:
        """
        Generate Gherkin feature file from specification
        
        Args:
            specification: Can be:
                - String (natural language or simple format)
                - Dict (structured JSON format)
            test_id: Optional test ID
            
        Returns:
            Dictionary with test_id and file paths
        """
        try:
            test_id = test_id or str(uuid.uuid4())[:8]
            logger.info(f"Generating feature file for test: {test_id}")
            
            # Parse specification based on type
            if isinstance(specification, dict):
                parsed = self.parse_structured_spec(specification)
            elif isinstance(specification, str):
                # Try to detect YAML format
                if specification.strip().startswith('feature:') or specification.strip().startswith('Feature:'):
                    # Could be YAML or natural language
                    try:
                        # Try parsing as YAML first
                        yaml_data = yaml.safe_load(specification)
                        if isinstance(yaml_data, dict):
                            logger.info("Detected YAML format")
                            parsed = self.parse_structured_spec(yaml_data)
                        else:
                            # Not valid YAML dict, try natural language
                            parsed = self.parse_natural_language(specification)
                    except yaml.YAMLError:
                        # Not valid YAML, try natural language
                        parsed = self.parse_natural_language(specification)
                elif 'Feature:' in specification or 'Scenario:' in specification:
                    # Natural language Gherkin format
                    parsed = self.parse_natural_language(specification)
                else:
                    # Simple comma-separated format
                    parsed = self._parse_simple_format(specification)
            else:
                raise ValueError("Specification must be string or dict")
            
            # Generate feature file content
            feature_content = self.feature_template.render(**parsed)
            
            # Save feature file
            feature_filename = f"generated_{test_id}.feature"
            feature_path = os.path.join(Config.BDD_GENERATED_DIR, feature_filename)
            
            with open(feature_path, 'w') as f:
                f.write(feature_content)
            
            logger.info(f"Feature file generated: {feature_path}")
            
            return {
                'test_id': test_id,
                'feature_file': feature_path,
                'feature_name': parsed['feature_name'],
                'feature_content': feature_content,
                'scenarios_count': len(parsed['scenarios']),
                'has_background': bool(parsed.get('background'))
            }
            
        except Exception as e:
            logger.error(f"Error generating feature file: {str(e)}")
            raise


# Convenience function (backward compatible)
def generate_bdd_test(specification: Any) -> Dict[str, str]:
    """
    Generate BDD test from specification
    
    Args:
        specification: String or Dict specification
        
    Returns:
        Generated test information
    """
    generator = EnhancedBDDGenerator()
    return generator.generate_feature_file(specification)
