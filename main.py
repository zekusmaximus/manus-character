#!/usr/bin/env python3
"""
Main Script for Character AI Framework

This script demonstrates the functionality of the Character AI Framework by loading a sample
character profile and starting a conversation with the character.
"""

import os
import sys
import json

# Add the current directory to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the required modules
from character_profile import CharacterProfile
from llm_interface import LLMInterface
from conversation_manager import ConversationManager

def load_character_profile(filepath):
    """
    Load a character profile from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file.
        
    Returns:
        CharacterProfile: A CharacterProfile instance.
    """
    try:
        return CharacterProfile.load_from_json(filepath)
    except Exception as e:
        print(f"Error loading character profile: {e}")
        sys.exit(1)

def setup_llm_interface():
    """
    Set up the LLM interface based on user input or environment variables.
    
    Returns:
        LLMInterface: An LLMInterface instance.
    """
    # Check for API key in environment variables
    api_key = os.environ.get("LLM_API_KEY")
    model = os.environ.get("LLM_MODEL")
    provider = os.environ.get("LLM_PROVIDER", "openai")
    
    # If no API key in environment, ask user if they want to provide one
    if not api_key:
        print("\nNo LLM API key found in environment variables.")
        use_api = input("Would you like to provide an API key? (y/n): ").lower()
        
        if use_api == 'y':
            api_key = input("Enter your API key: ")
            provider = input("Enter provider (openai, anthropic, gemini) [default: openai]: ") or "openai"
            model = input(f"Enter model name for {provider} [leave blank for default]: ")
        else:
            print("Using dummy LLM implementation for testing.")
    
    return LLMInterface(api_key=api_key, model=model, provider=provider)

def main():
    """
    Main function to run the Character AI Framework demonstration.
    """
    print("=" * 80)
    print("Character AI Framework - Minimal Prototype")
    print("=" * 80)
    
    # Get the path to the sample character profile
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_profile_path = os.path.join(script_dir, "sample_character.json")
    
    # Check if the sample character profile exists
    if not os.path.exists(sample_profile_path):
        print(f"Error: Sample character profile not found at {sample_profile_path}")
        sys.exit(1)
    
    print(f"Loading character profile from {sample_profile_path}")
    character_profile = load_character_profile(sample_profile_path)
    
    print(f"\nCharacter loaded: {character_profile.name}")
    print("\nSetting up LLM interface...")
    llm_interface = setup_llm_interface()
    
    print("\nInitializing conversation manager...")
    conversation_manager = ConversationManager(character_profile, llm_interface)
    
    print("\nStarting conversation...")
    print("-" * 80)
    conversation_manager.start_conversation()

if __name__ == "__main__":
    main()
