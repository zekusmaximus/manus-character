"""
ConversationManager Module

This module defines the ConversationManager class which manages the conversation flow
between the user and the AI character.
"""

class ConversationManager:
    """
    A class to manage the conversation flow between the user and the AI character.
    
    Attributes:
        character_profile (CharacterProfile): The character profile.
        narrative_voice_engine (NarrativeVoiceEngine): The narrative voice engine.
        decision_engine (DecisionEngine): The decision engine.
        llm_interface (LLMInterface): The LLM interface.
        conversation_history (list): The conversation history.
    """
    
    def __init__(self, character_profile, llm_interface):
        """
        Initialize a ConversationManager with the given character profile and LLM interface.
        
        Args:
            character_profile (CharacterProfile): The character profile.
            llm_interface (LLMInterface): The LLM interface.
        """
        from narrative_voice_engine import NarrativeVoiceEngine
        from decision_engine import DecisionEngine
        
        self.character_profile = character_profile
        self.narrative_voice_engine = NarrativeVoiceEngine()
        self.decision_engine = DecisionEngine()
        self.llm_interface = llm_interface
        self.conversation_history = []
    
    def process_user_input(self, user_input):
        """
        Process user input and generate a character response.
        
        Args:
            user_input (str): The user's input.
            
        Returns:
            str: The character's response.
        """
        # Get decision guidance from the decision engine
        decision_guidance = self.decision_engine.evaluate_situation(
            user_input, self.character_profile
        )
        
        # Construct the LLM prompt using the narrative voice engine
        prompt = self.narrative_voice_engine.construct_llm_prompt(
            user_input, 
            self.character_profile, 
            self.conversation_history,
            decision_guidance
        )
        
        # Get the character's response from the LLM
        character_response = self.llm_interface.get_llm_response(prompt)
        
        # Update the conversation history
        self.conversation_history.append({
            'user': user_input,
            'character': character_response
        })
        
        return character_response
    
    def start_conversation(self):
        """
        Start the conversation loop.
        """
        print(f"You are now talking to {self.character_profile.name}. Type 'quit' to exit.")
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check if the user wants to quit
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\n{self.character_profile.name}: Goodbye!")
                break
            
            # Process the user input and get the character's response
            character_response = self.process_user_input(user_input)
            
            # Print the character's response
            print(f"\n{self.character_profile.name}: {character_response}")
