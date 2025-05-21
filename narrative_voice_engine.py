"""
NarrativeVoiceEngine Module

This module defines the NarrativeVoiceEngine class which constructs prompts for an external LLM
that encourage responses in a character's narrative voice.
"""

class NarrativeVoiceEngine:
    """
    A class to construct prompts for an external LLM that encourage responses in a character's narrative voice.
    
    Methods:
        construct_llm_prompt: Creates a detailed prompt for an LLM to respond as the character.
    """
    
    @staticmethod
    def _format_voice_samples(samples):
        """
        Format narrative voice samples for inclusion in the prompt.
        
        Args:
            samples (list): List of narrative voice samples.
            
        Returns:
            str: Formatted samples string.
        """
        if not samples:
            return "No specific voice samples available."
        
        formatted = "Examples of how this character speaks:\n"
        for i, sample in enumerate(samples, 1):
            formatted += f"{i}. \"{sample}\"\n"
        return formatted
    
    @staticmethod
    def _format_key_phrases(phrases):
        """
        Format key phrases and verbal tics for inclusion in the prompt.
        
        Args:
            phrases (list): List of key phrases and verbal tics.
            
        Returns:
            str: Formatted phrases string.
        """
        if not phrases:
            return "No specific key phrases or verbal tics."
        
        formatted = "Common phrases and verbal tics:\n"
        for phrase in phrases:
            formatted += f"- \"{phrase}\"\n"
        return formatted
    
    @staticmethod
    def _format_linguistic_quirks(quirks):
        """
        Format linguistic quirks for inclusion in the prompt.
        
        Args:
            quirks (dict): Dictionary of linguistic quirks.
            
        Returns:
            str: Formatted quirks string.
        """
        if not quirks:
            return "No specific linguistic quirks."
        
        formatted = "Linguistic style and quirks:\n"
        for key, value in quirks.items():
            formatted += f"- {key}: {value}\n"
        return formatted
    
    @staticmethod
    def _format_response_tendencies(tendencies):
        """
        Format response tendencies for inclusion in the prompt.
        
        Args:
            tendencies (dict): Dictionary of response tendencies.
            
        Returns:
            str: Formatted tendencies string.
        """
        if not tendencies:
            return "No specific response tendencies."
        
        formatted = "Typical response patterns:\n"
        for key, value in tendencies.items():
            formatted += f"- {key}: {value}\n"
        return formatted
    
    @staticmethod
    def _format_conversation_history(history, max_entries=5):
        """
        Format conversation history for inclusion in the prompt.
        
        Args:
            history (list): List of conversation entries.
            max_entries (int): Maximum number of recent entries to include.
            
        Returns:
            str: Formatted history string.
        """
        if not history:
            return "No conversation history yet."
        
        # Take only the most recent entries
        recent_history = history[-max_entries:] if len(history) > max_entries else history
        
        formatted = "Recent conversation:\n"
        for entry in recent_history:
            formatted += f"User: {entry['user']}\n"
            formatted += f"Character: {entry['character']}\n"
        return formatted
    
    @classmethod
    def construct_llm_prompt(cls, user_input, character_profile, conversation_history=None, decision_guidance=None):
        """
        Construct a detailed prompt for an LLM to respond as the character.
        
        Args:
            user_input (str): The user's current input.
            character_profile (CharacterProfile): The character profile.
            conversation_history (list, optional): A list of previous conversation entries.
            decision_guidance (str or dict, optional): Guidance from the DecisionEngine.
            
        Returns:
            str: A detailed prompt for the LLM.
        """
        if conversation_history is None:
            conversation_history = []
        
        # Basic instruction
        prompt = f"You are roleplaying as {character_profile.name}. "
        prompt += "Respond to the user's message in character, maintaining a consistent voice and personality.\n\n"
        
        # Character voice details
        prompt += "CHARACTER VOICE DETAILS:\n"
        prompt += cls._format_voice_samples(character_profile.narrative_voice_samples)
        prompt += "\n"
        prompt += cls._format_key_phrases(character_profile.key_phrases_tics)
        prompt += "\n"
        prompt += cls._format_linguistic_quirks(character_profile.linguistic_quirks)
        prompt += "\n"
        prompt += cls._format_response_tendencies(character_profile.response_tendencies)
        prompt += "\n"
        
        # Decision guidance (if provided)
        if decision_guidance:
            prompt += "DECISION GUIDANCE:\n"
            if isinstance(decision_guidance, dict):
                for key, value in decision_guidance.items():
                    prompt += f"- {key}: {value}\n"
            else:
                prompt += f"{decision_guidance}\n"
            prompt += "\n"
        
        # Conversation history
        prompt += "CONVERSATION CONTEXT:\n"
        prompt += cls._format_conversation_history(conversation_history)
        prompt += "\n"
        
        # Current user input
        prompt += f"USER'S CURRENT MESSAGE: \"{user_input}\"\n\n"
        
        # Final instruction
        prompt += "INSTRUCTIONS:\n"
        prompt += "1. Respond as the character, maintaining their unique voice and personality.\n"
        prompt += "2. Keep the response concise and conversational.\n"
        prompt += "3. Do not break character or reference that you are an AI.\n"
        prompt += "4. Do not include any meta-text, instructions, or explanations outside of the character's response.\n\n"
        
        prompt += "CHARACTER'S RESPONSE:"
        
        return prompt
