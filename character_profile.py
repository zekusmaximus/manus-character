"""
CharacterProfile Module

This module defines the CharacterProfile class which stores attributes of a fictional character
for use in a conversational AI agent.
"""

class CharacterProfile:
    """
    A class to define and store a fictional character's attributes for use in a conversational AI.
    
    Attributes:
        name (str): Character's name.
        narrative_voice_samples (list): Examples of the character's dialogue or narration.
        key_phrases_tics (list): Common phrases, verbal tics, or unique expressions.
        linguistic_quirks (dict): Vocabulary preferences and sentence structure patterns.
        response_tendencies (dict): Notes on how the character typically reacts to situations.
        decision_rules (dict): A simplified set of rules for the decision engine.
    """
    
    def __init__(self, name="", narrative_voice_samples=None, key_phrases_tics=None, 
                 linguistic_quirks=None, response_tendencies=None, decision_rules=None):
        """
        Initialize a CharacterProfile with the given attributes.
        
        Args:
            name (str): Character's name.
            narrative_voice_samples (list): Examples of the character's dialogue or narration.
            key_phrases_tics (list): Common phrases, verbal tics, or unique expressions.
            linguistic_quirks (dict): Vocabulary preferences and sentence structure patterns.
            response_tendencies (dict): Notes on how the character typically reacts to situations.
            decision_rules (dict): A simplified set of rules for the decision engine.
        """
        self.name = name
        self.narrative_voice_samples = narrative_voice_samples or []
        self.key_phrases_tics = key_phrases_tics or []
        self.linguistic_quirks = linguistic_quirks or {}
        self.response_tendencies = response_tendencies or {}
        self.decision_rules = decision_rules or {}
    
    def to_dict(self):
        """
        Convert the character profile to a dictionary for serialization.
        
        Returns:
            dict: A dictionary representation of the character profile.
        """
        return {
            'name': self.name,
            'narrative_voice_samples': self.narrative_voice_samples,
            'key_phrases_tics': self.key_phrases_tics,
            'linguistic_quirks': self.linguistic_quirks,
            'response_tendencies': self.response_tendencies,
            'decision_rules': self.decision_rules
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a CharacterProfile instance from a dictionary.
        
        Args:
            data (dict): A dictionary containing character profile data.
            
        Returns:
            CharacterProfile: A new CharacterProfile instance.
        """
        return cls(
            name=data.get('name', ''),
            narrative_voice_samples=data.get('narrative_voice_samples', []),
            key_phrases_tics=data.get('key_phrases_tics', []),
            linguistic_quirks=data.get('linguistic_quirks', {}),
            response_tendencies=data.get('response_tendencies', {}),
            decision_rules=data.get('decision_rules', {})
        )
    
    def save_to_json(self, filepath):
        """
        Save the character profile to a JSON file.
        
        Args:
            filepath (str): Path to the JSON file.
        """
        import json
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
    
    @classmethod
    def load_from_json(cls, filepath):
        """
        Load a character profile from a JSON file.
        
        Args:
            filepath (str): Path to the JSON file.
            
        Returns:
            CharacterProfile: A new CharacterProfile instance.
        """
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
