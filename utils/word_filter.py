import re
import unicodedata
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from better_profanity import Profanity

logger = logging.getLogger('discord')

@dataclass
class FilterMatch:
    pattern: str
    category: str
    severity: int
    index: int
    matched_text: str

class EnhancedWordFilter:
    def __init__(self, db):
        self.db = db
        self.profanity = Profanity()
        self.cache = {}
        self.pattern_cache = {}
        self.regex_patterns = {}
        
    async def load_patterns(self, guild_id: int):
        """Load or refresh patterns for a guild"""
        patterns = await self.db.get_filter_patterns(guild_id)
        
        self.pattern_cache[guild_id] = {
            'regex': [],
            'simple': set(),
            'categories': {}
        }
        
        for pattern in patterns:
            if pattern['is_regex']:
                try:
                    compiled = re.compile(pattern['regex_pattern'], re.IGNORECASE)
                    self.pattern_cache[guild_id]['regex'].append({
                        'pattern': compiled,
                        'category': pattern['category'],
                        'severity': pattern['severity']
                    })
                except re.error:
                    logger.error(f"Invalid regex pattern: {pattern['regex_pattern']}")
            else:
                self.pattern_cache[guild_id]['simple'].add(pattern['pattern'].lower())
                self.pattern_cache[guild_id]['categories'][pattern['pattern'].lower()] = {
                    'category': pattern['category'],
                    'severity': pattern['severity']
                }

    def normalize_text(self, text: str) -> str:
        """Advanced text normalization"""
        # Remove accents and convert to lowercase
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode()
        
        # Replace common leetspeak
        leetspeak = {
            '4': 'a', '@': 'a', '8': 'b', '3': 'e', '1': 'i', '0': 'o',
            '5': 's', '7': 't', '2': 'z', '9': 'g', '6': 'g'
        }
        for k, v in leetspeak.items():
            text = text.replace(k, v)
            
        # Remove repeating characters
        text = re.sub(r'(.)\1+', r'\1', text)
        
        # Remove non-alphanumeric characters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        return text.lower()

    async def check_message(self, guild_id: int, content: str) -> List[FilterMatch]:
        """Check message for filter violations"""
        if guild_id not in self.pattern_cache:
            await self.load_patterns(guild_id)
            
        matches = []
        normalized = self.normalize_text(content)
        words = normalized.split()
        
        # Check regex patterns
        for regex_data in self.pattern_cache[guild_id]['regex']:
            for match in regex_data['pattern'].finditer(normalized):
                matches.append(FilterMatch(
                    pattern=match.group(),
                    category=regex_data['category'],
                    severity=regex_data['severity'],
                    index=match.start(),
                    matched_text=content[match.start():match.end()]
                ))
        
        # Check simple patterns
        for i, word in enumerate(words):
            if word in self.pattern_cache[guild_id]['simple']:
                cat_data = self.pattern_cache[guild_id]['categories'][word]
                matches.append(FilterMatch(
                    pattern=word,
                    category=cat_data['category'],
                    severity=cat_data['severity'],
                    index=normalized.find(word),
                    matched_text=word
                ))
        
        return matches 