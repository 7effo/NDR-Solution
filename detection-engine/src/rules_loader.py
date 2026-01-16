"""
Rules Loader
Loads detection rules from YAML files
"""
import yaml
import glob
import os
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger()

class RuleLoader:
    def __init__(self, rules_path: str):
        self.rules_path = rules_path
        
    def load_rules(self) -> List[Dict[str, Any]]:
        """Load all valid YAML rules"""
        rules = []
        pattern = os.path.join(self.rules_path, "*.yaml")
        files = glob.glob(pattern)
        
        for f in files:
            try:
                with open(f, 'r') as stream:
                    rule = yaml.safe_load(stream)
                    if self.validate_rule(rule):
                        rule['file_path'] = f
                        rules.append(rule)
                    else:
                        logger.warn("Skipping invalid rule", file=f)
            except Exception as e:
                logger.error("Failed to load rule", file=f, error=str(e))
                
        logger.info("Loaded rules", count=len(rules))
        return rules

    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name', 'severity', 'index', 'query_dsl', 'condition']
        return all(field in rule for field in required_fields)
