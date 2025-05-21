"""
DecisionEngine Module

This module defines the DecisionEngine class which applies a character's decision rules
to influence responses or actions in a simplified manner.
"""

class DecisionEngine:
    """
    A class to apply a character's decision rules to influence responses or actions.
    
    Methods:
        evaluate_situation: Analyzes user input against character decision rules.
    """
    
    @staticmethod
    def _check_for_keywords(user_input, keywords):
        """
        Check if any keywords are present in the user input.
        
        Args:
            user_input (str): The user's input.
            keywords (list): List of keywords to check for.
            
        Returns:
            bool: True if any keyword is found, False otherwise.
        """
        user_input_lower = user_input.lower()
        return any(keyword.lower() in user_input_lower for keyword in keywords)
    
    @staticmethod
    def _match_decision_pattern(user_input, pattern):
        """
        Check if the user input matches a decision pattern.
        
        Args:
            user_input (str): The user's input.
            pattern (dict): A decision pattern with 'if_situation' and 'then_response_style'.
            
        Returns:
            str or None: The response style if matched, None otherwise.
        """
        situation = pattern.get('if_situation', '')
        response_style = pattern.get('then_response_style', '')
        
        # Simple keyword matching for situations
        if 'asked a direct personal question' in situation and '?' in user_input:
            return response_style
        elif 'criticized' in situation and any(word in user_input.lower() for word in ['wrong', 'bad', 'terrible', 'awful', 'mistake']):
            return response_style
        elif 'complimented' in situation and any(word in user_input.lower() for word in ['good', 'great', 'excellent', 'amazing', 'wonderful']):
            return response_style
        elif 'threatened' in situation and any(word in user_input.lower() for word in ['threat', 'danger', 'warning', 'careful', 'watch out']):
            return response_style
        
        return None
    
    @classmethod
    def evaluate_situation(cls, user_input, character_profile):
        """
        Analyze the user input against the character's decision rules.
        
        Args:
            user_input (str): The user's current input.
            character_profile (CharacterProfile): The character profile.
            
        Returns:
            dict: Decision guidance for the NarrativeVoiceEngine.
        """
        decision_rules = character_profile.decision_rules
        guidance = {}
        
        # Check values hierarchy if present
        values_hierarchy = decision_rules.get('values_hierarchy', [])
        if values_hierarchy:
            # Check if user input triggers any values
            triggered_values = []
            for value in values_hierarchy:
                if cls._check_for_keywords(user_input, [value]):
                    triggered_values.append(value)
            
            if triggered_values:
                # Sort triggered values by their position in the hierarchy
                triggered_values.sort(key=lambda x: values_hierarchy.index(x))
                guidance['prioritized_values'] = triggered_values
        
        # Check moral framework if present
        moral_framework = decision_rules.get('moral_framework_notes', '')
        if moral_framework:
            guidance['moral_framework'] = moral_framework
        
        # Check decision patterns if present
        decision_patterns = decision_rules.get('decision_patterns', [])
        for pattern in decision_patterns:
            response_style = cls._match_decision_pattern(user_input, pattern)
            if response_style:
                guidance['suggested_response_style'] = response_style
                break
        
        # If no specific guidance was generated, provide a default
        if not guidance:
            guidance['default_approach'] = "Respond naturally based on character voice."
        
        return guidance
