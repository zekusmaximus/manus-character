"""
LLMInterface Module

This module defines the LLMInterface class which handles communication with external LLM APIs.
It provides a generic interface that can work with multiple LLM providers and includes
a dummy implementation for testing without an API key.
"""

class LLMInterface:
    """
    A class to handle communication with external LLM APIs.
    
    Attributes:
        api_key (str): API key for the LLM provider.
        model (str): Model name to use.
        provider (str): LLM provider name.
        use_dummy (bool): Whether to use the dummy implementation.
    """
    
    def __init__(self, api_key=None, model=None, provider="openai"):
        """
        Initialize an LLMInterface with the given API key and model.
        
        Args:
            api_key (str, optional): API key for the LLM provider.
            model (str, optional): Model name to use.
            provider (str, optional): LLM provider name. Defaults to "openai".
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider.lower()
        self.use_dummy = api_key is None
        
        if not self.use_dummy:
            print(f"Using {self.provider} with model {self.model}")
        else:
            print("No API key provided. Using dummy implementation.")
    
    def get_llm_response(self, prompt):
        """
        Get a response from the LLM API.
        
        Args:
            prompt (str): The prompt to send to the LLM.
            
        Returns:
            str: The LLM's text response.
        """
        if self.use_dummy:
            return self._get_dummy_response(prompt)
        
        # Determine which provider to use
        if self.provider == "openai":
            return self._get_openai_response(prompt)
        elif self.provider == "anthropic":
            return self._get_anthropic_response(prompt)
        elif self.provider == "gemini":
            return self._get_gemini_response(prompt)
        else:
            print(f"Unknown provider: {self.provider}. Using dummy implementation.")
            return self._get_dummy_response(prompt)
    
    def _get_dummy_response(self, prompt):
        """
        Get a dummy response for testing without an API key.
        
        Args:
            prompt (str): The prompt that would be sent to the LLM.
            
        Returns:
            str: A canned response for testing.
        """
        # Extract character name from prompt if possible
        import re
        name_match = re.search(r"You are roleplaying as ([^.]+)", prompt)
        character_name = name_match.group(1) if name_match else "the character"
        
        # Extract user message from prompt if possible
        user_msg_match = re.search(r"USER'S CURRENT MESSAGE: \"([^\"]+)\"", prompt)
        user_message = user_msg_match.group(1) if user_msg_match else "your message"
        
        # Generate a simple response based on the user's message
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            return f"Hello there! {character_name} at your service."
        elif "how are you" in user_message.lower():
            return f"I'm doing just fine, thank you for asking. How about yourself?"
        elif "?" in user_message:
            return f"That's an interesting question. Let me think about that for a moment..."
        else:
            return f"I hear what you're saying about '{user_message}'. Interesting perspective."
    
    def _get_openai_response(self, prompt):
        """
        Get a response from the OpenAI API.
        
        Args:
            prompt (str): The prompt to send to the OpenAI API.
            
        Returns:
            str: The OpenAI API's text response.
        """
        try:
            # Import the OpenAI library
            import openai
            
            # Set the API key
            openai.api_key = self.api_key
            
            # Determine the model to use
            model = self.model or "gpt-3.5-turbo"
            
            # Make the API call
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            # Extract and return the response text
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._get_dummy_response(prompt)
    
    def _get_anthropic_response(self, prompt):
        """
        Get a response from the Anthropic API.
        
        Args:
            prompt (str): The prompt to send to the Anthropic API.
            
        Returns:
            str: The Anthropic API's text response.
        """
        try:
            # Import the Anthropic library
            import anthropic
            
            # Create a client
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Determine the model to use
            model = self.model or "claude-2"
            
            # Make the API call
            response = client.completions.create(
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                model=model,
                max_tokens_to_sample=150,
                temperature=0.7
            )
            
            # Extract and return the response text
            return response.completion.strip()
        
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return self._get_dummy_response(prompt)
    
    def _get_gemini_response(self, prompt):
        """
        Get a response from the Google Gemini API.
        
        Args:
            prompt (str): The prompt to send to the Gemini API.
            
        Returns:
            str: The Gemini API's text response.
        """
        try:
            # Import the Google Generative AI library
            import google.generativeai as genai
            
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Determine the model to use
            model = self.model or "gemini-pro"
            
            # Get the model
            model = genai.GenerativeModel(model)
            
            # Generate a response
            response = model.generate_content(prompt)
            
            # Extract and return the response text
            return response.text.strip()
        
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self._get_dummy_response(prompt)
