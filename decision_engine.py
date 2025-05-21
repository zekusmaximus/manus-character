"""
DecisionEngine Module

This module defines the DecisionEngine class, a sophisticated component responsible for
analyzing user input and conversation context against a character's profile. 
It leverages various techniques including keyword matching, regular expressions, 
sentiment analysis, conversation history analysis, and values-based scoring 
to produce rich guidance for generating character responses.
"""
import re # Added for regex support
from typing import List, Dict, Any
from collections import Counter # Added Counter for topic detection
from character_profile import CharacterProfile # Assuming CharacterProfile is in character_profile.py

class DecisionEngine:
    """
    Applies a character's decision rules to analyze user input and conversation context,
    producing guidance for response generation.

    The engine evaluates situations by:
    - Analyzing conversation history for topics, unanswered questions, and emotional tone.
    - Performing sentiment analysis on the current user input.
    - Matching user input against predefined decision patterns (keyword or regex-based).
    - Scoring matched patterns, considering alignment with the character's value hierarchy.
    - Checking for direct keyword triggers related to character values and moral framework.

    The primary public method is `evaluate_situation`, which orchestrates these steps
    and returns a structured `guidance` dictionary.

    Attributes:
        character_profile (CharacterProfile): The character's profile, containing
                                              decision rules, values, and other traits.
        conversation_history (List[Dict[str, str]]): A list of dictionaries, where
                                                     each dictionary represents a turn
                                                     in the conversation (e.g., 
                                                     {'user': 'input', 'character': 'response'}).
    """
    character_profile: CharacterProfile
    conversation_history: List[Dict[str, str]]

    def __init__(self, character_profile: CharacterProfile, conversation_history: List[Dict[str, str]]):
        """
        Initializes the DecisionEngine with a character's profile and conversation history.

        Args:
            character_profile (CharacterProfile): An instance of CharacterProfile containing
                                                  the character's attributes, decision rules,
                                                  value hierarchy, and moral framework.
            conversation_history (List[Dict[str, str]]): A list of dictionaries,
                                                          representing the ongoing conversation.
                                                          Each dictionary should have keys like
                                                          'user' and/or 'character' with their
                                                          respective utterances.
        """
        self.character_profile = character_profile
        self.conversation_history = conversation_history
    
    def _check_for_keywords(self, user_input: str, keywords: List[str]) -> bool:
        """
        Checks if any of the provided keywords are present in the user input.
        This is a utility method used, for example, to quickly check if user input
        directly mentions one of the character's core values.

        Args:
            user_input (str): The text input from the user.
            keywords (List[str]): A list of keywords to search for. The check is
                                  case-insensitive.
            
        Returns:
            bool: True if any keyword is found in the user input, False otherwise.
        """
        user_input_lower = user_input.lower()
        return any(keyword.lower() in user_input_lower for keyword in keywords)
    
    def _match_decision_pattern(self, user_input: str, pattern: Dict[str, Any]) -> float:
        """
        Matches the user input against a single decision pattern and returns a score.

        Patterns can be keyword-based or regex-based. The score indicates the strength
        of the match, typically on a scale of 0.0 to 10.0 (though values-based adjustments
        can increase this).

        Args:
            user_input (str): The user's text input.
            pattern (Dict[str, Any]): A dictionary representing the decision pattern.
                Expected keys include:
                - 'if_situation' (str): The core pattern string (a keyword phrase or a regex).
                - 'is_regex' (bool, optional): If True, 'if_situation' is treated as a regex.
                                              Defaults to False.
                - Other keys like 'then_response_style', 'category', 'aligns_with_values'
                  are used by `evaluate_situation` but not directly by this method's matching logic.

        Returns:
            float: A score representing the match strength. 0.0 indicates no match or a
                   very weak match. Higher scores (e.g., 5.0-9.0) indicate stronger matches.
                   A generic regex match not tied to predefined situations gets a default score (e.g. 5.0).
        """
        situation_pattern: str = pattern.get('if_situation', '')
        is_regex: bool = pattern.get('is_regex', False)
        user_input_lower = user_input.lower() # For keyword matching

        # patterns_config defines a set of built-in, quickly accessible situation patterns
        # with their specific keywords and scores. These can be matched via simple keyword
        # logic or, if 'if_situation' string from this config is used as a regex pattern
        # in the character profile, it will also use the score defined here.
        patterns_config = {
            'asked a direct personal question': {'score': 7.0, 'keywords': ['?'], 'match_all_keywords': True},
            'criticized': {'score': 8.0, 'keywords': ['wrong', 'bad', 'terrible', 'awful', 'mistake']},
            'complimented': {'score': 6.0, 'keywords': ['good', 'great', 'excellent', 'amazing', 'wonderful']},
            'threatened': {'score': 9.0, 'keywords': ['threat', 'danger', 'warning', 'careful', 'watch out']}
        }

        if is_regex:
            try:
                # If situation_pattern is one of the predefined ones, use its score.
                # Otherwise, a generic regex match could have a default score or score from pattern itself (future enhancement)
                if re.search(situation_pattern, user_input): # Match user_input, not user_input_lower for regex
                    # Check if this regex pattern corresponds to one of our scored situations
                    for key, config in patterns_config.items():
                        if situation_pattern == key: # Exact match to a predefined situation string
                            # If the regex is, for example, ".* a direct personal question.*" and it matches,
                            # and situation_pattern is "asked a direct personal question", it gets 7.0
                            # Further keyword checks for regex are implicit in the regex pattern itself.
                            # e.g. pattern for "asked a direct personal question" could be ".*\?"
                            return config['score']
                    return 5.0 # Default score for generic regex match not tied to predefined situations
            except re.error as e:
                # Log the error or print a warning for debugging purposes
                print(f"Warning: Regex error for pattern '{situation_pattern}': {e}")
                return 0.0 # Return 0.0 if regex is invalid to prevent further issues
        else:
            # Keyword-based matching (existing logic)
            if 'asked a direct personal question' in situation_pattern and '?' in user_input:
                return patterns_config['asked a direct personal question']['score']
            elif 'criticized' in situation_pattern and any(word in user_input_lower for word in patterns_config['criticized']['keywords']):
                return patterns_config['criticized']['score']
            elif 'complimented' in situation_pattern and any(word in user_input_lower for word in patterns_config['complimented']['keywords']):
                return patterns_config['complimented']['score']
            elif 'threatened' in situation_pattern and any(word in user_input_lower for word in patterns_config['threatened']['keywords']):
                return patterns_config['threatened']['score']
        
        return 0.0 # Return 0.0 if no match

    def _weigh_against_value_hierarchy(self, matched_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adjusts scores of matched patterns based on their alignment with the character's value hierarchy.

        Patterns that align with higher-priority values in the character's hierarchy receive
        a score bonus. The bonus is inversely proportional to the value's rank (higher rank = smaller index = larger bonus).

        Args:
            matched_patterns (List[Dict[str, Any]]): A list of pattern match dictionaries.
                Each dictionary should contain at least a 'score' and a 'pattern' sub-dictionary.
                The 'pattern' sub-dictionary is expected to have an 'aligns_with_values' key (List[str], optional).

        Returns:
            List[Dict[str, Any]]: The list of pattern matches, with scores potentially adjusted
                                  and a 'value_alignment' dictionary added to those that aligned.
                                  The list is re-sorted by the new scores in descending order.
                                  The 'value_alignment' dictionary contains:
                                  - 'value' (str): The specific value it aligned with.
                                  - 'original_score' (float): The score before value-based adjustment.
                                  - 'bonus' (float): The bonus applied.
                                  - 'final_score' (float): The score after bonus.
        """
        values_hierarchy: List[str] = self.character_profile.decision_rules.get('values_hierarchy', [])
        if not values_hierarchy: # No values to weigh against, return patterns as is
            return matched_patterns

        adjusted_patterns: List[Dict[str, Any]] = []
        for pattern_match in matched_patterns:
            # The 'pattern' key in pattern_match holds the original decision pattern configuration
            original_decision_pattern_config: Dict[str, Any] = pattern_match.get('pattern', {})
            aligns_with_values: List[str] = original_decision_pattern_config.get('aligns_with_values', [])
            
            best_alignment_bonus = 0.0
            best_alignment_value = None
            original_score = pattern_match['score']

            if aligns_with_values:
                for value_name in aligns_with_values:
                    if value_name in values_hierarchy:
                        try:
                            idx = values_hierarchy.index(value_name)
                            # Bonus is higher for values earlier in the hierarchy (lower index)
                            bonus = 2.0 / (idx + 1) 
                            if bonus > best_alignment_bonus: # Apply bonus for the highest-ranking aligned value
                                best_alignment_bonus = bonus
                                best_alignment_value = value_name
                        except ValueError:
                            # This should not happen if value_name was confirmed to be in values_hierarchy.
                            # Logging could be added here for robustness if external data integrity is a concern.
                            continue 
            
            adjusted_pattern_match = pattern_match.copy() # Create a copy to modify
            if best_alignment_value and best_alignment_bonus > 0:
                adjusted_pattern_match['score'] = original_score + best_alignment_bonus
                adjusted_pattern_match['value_alignment'] = {
                    'value': best_alignment_value,
                    'original_score': original_score,
                    'bonus': best_alignment_bonus,
                    'final_score': adjusted_pattern_match['score']
                }
            adjusted_patterns.append(adjusted_pattern_match)

        # Re-sort patterns by their new score in descending order
        adjusted_patterns.sort(key=lambda p: p['score'], reverse=True)
        return adjusted_patterns

    def _detect_sentiment_in_input(self, user_input: str) -> Dict[str, float]:
        """
        Performs basic sentiment analysis on the user's input string.

        It counts occurrences of predefined positive and negative keywords.
        A neutral score is assigned if no keywords are found.

        Args:
            user_input (str): The user's text input.

        Returns:
            Dict[str, float]: A dictionary containing sentiment scores:
                - 'positive_score' (float): Count of positive keywords.
                - 'negative_score' (float): Count of negative keywords.
                - 'neutral_score' (float): 1.0 if no positive/negative keywords found, else 0.0.
        """
        if not user_input: # Handles None or empty string
            return {'positive_score': 0.0, 'negative_score': 0.0, 'neutral_score': 1.0}

        user_input_lower = user_input.lower()
        # Keywords for sentiment detection
        positive_keywords = ['good', 'great', 'happy', 'love', 'excellent', 'amazing', 'wonderful', 'nice', 'super']
        negative_keywords = ['bad', 'terrible', 'sad', 'hate', 'wrong', 'awful', 'mistake', 'not good', 'annoying']

        positive_score = 0.0
        for keyword in positive_keywords:
            positive_score += user_input_lower.count(keyword) # Sum occurrences of each positive keyword

        negative_score = 0.0
        for keyword in negative_keywords:
            negative_score += user_input_lower.count(keyword) # Sum occurrences of each negative keyword
            
        neutral_score = 0.0
        if positive_score == 0 and negative_score == 0:
            neutral_score = 1.0 # Mark as neutral if no positive or negative keywords are detected

        return {'positive_score': positive_score, 'negative_score': negative_score, 'neutral_score': neutral_score}

    def _analyze_conversation_history(self) -> Dict[str, Any]:
        """
        Analyzes the recent conversation history to extract contextual information.

        This includes:
        - Identifying recurring topics (most common words from recent user inputs).
        - Listing pending (unanswered) questions from recent user inputs.
        - Detecting recent emotional tones based on keywords.

        Args:
            None (uses `self.conversation_history`).

        Returns:
            Dict[str, Any]: A dictionary containing the analysis:
                - 'recurring_topics' (List[str]): Top 3 most common words (len > 4) from the
                                                  last 5 user utterances.
                - 'pending_questions' (List[str]): User utterances from the last 3 turns
                                                   (excluding the most recent) that contain '?'.
                - 'recent_emotional_tones' (List[str]): Keywords like 'angry', 'happy', 'sad'
                                                        detected in the last 3 user utterances.
        """
        history_analysis: Dict[str, Any] = {
            'recurring_topics': [],
            'pending_questions': [],
            'recent_emotional_tones': []
        }
        
        # Extract user utterances from conversation history
        # Assumes history entries are dicts like {'user': 'text'} or {'character': 'text'}
        user_utterances: List[str] = [
            turn['user'] for turn in self.conversation_history if 'user' in turn
        ]

        if not user_utterances:
            return history_analysis # Return empty analysis if no user utterances

        # Topic Detection: Analyze last 5 user inputs for common words (longer than 4 chars)
        topic_words: List[str] = []
        for text in user_utterances[-5:]: 
            words = [word.lower() for word in text.split() if len(word) > 4]
            topic_words.extend(words)
        
        if topic_words:
            history_analysis['recurring_topics'] = [
                item[0] for item in Counter(topic_words).most_common(3) # Get top 3
            ]

        # Unanswered Questions: Check user inputs from 3 turns ago up to the one before last
        # (e.g., if current is turn 5, check user inputs from turn 2, 3, 4)
        # Slicing user_utterances[-4:-1] covers:
        #   -4: 4th from last (if history is long enough)
        #   -3: 3rd from last
        #   -2: 2nd from last (the one just before the current user_input being processed by evaluate_situation)
        for text in user_utterances[-4:-1]: 
            if '?' in text:
                history_analysis['pending_questions'].append(text)
        
        # Recent Emotional Tone: Check last 3 user inputs for emotional keywords
        emotional_keywords = {'angry', 'happy', 'sad'} # Example set of emotional keywords
        detected_tones: List[str] = []
        for text in user_utterances[-3:]: 
            text_lower = text.lower()
            for tone in emotional_keywords:
                if tone in text_lower:
                    detected_tones.append(tone)
        if detected_tones:
            history_analysis['recent_emotional_tones'] = list(set(detected_tones)) # Store unique tones
            
        return history_analysis

    def evaluate_situation(self, user_input: str) -> Dict[str, Any]:
        """
        Analyzes user input and conversation context against character rules to guide response generation.

        This is the main public method of the DecisionEngine. It orchestrates various analyses:
        1.  Contextual Analysis: Examines conversation history and current input sentiment.
        2.  Direct Character Aspects: Checks for alignment with character's values (keyword-based) and moral framework.
        3.  Pattern Matching: Matches input against predefined decision patterns (keyword/regex).
        4.  Value Weighting: Adjusts pattern scores based on alignment with character's value hierarchy.
        5.  Confidence Scoring: Determines a confidence level for the top decision.

        Args:
            user_input (str): The current text input from the user.

        Returns:
            Dict[str, Any]: A comprehensive 'guidance' dictionary containing various analytical outputs.
                Key fields include:
                - 'recurring_topics' (List[str]): Common topics from recent conversation.
                - 'pending_questions' (List[str]): Unanswered questions from recent user input.
                - 'recent_emotional_tones' (List[str]): Emotional keywords detected recently.
                - 'current_sentiment' (Dict[str, float]): Sentiment scores for the `user_input`
                  (e.g., `{'positive_score': ..., 'negative_score': ..., 'neutral_score': ...}`).
                - 'matched_patterns' (List[Dict[str, Any]]): A list of decision patterns that matched
                  the `user_input`, sorted by score (highest first). Each entry includes:
                    - 'pattern' (Dict[str, Any]): The original pattern configuration.
                    - 'score' (float): The final score of the match (after value weighting).
                    - 'response_style' (str): Suggested response style from the pattern.
                    - 'category' (str): Category of the pattern (e.g., "interrogative", "defensive").
                    - 'value_alignment' (Dict[str, Any], optional): Details if the pattern's score
                      was boosted due to alignment with character values. Includes 'value', 
                      'original_score', 'bonus', and 'final_score'.
                - 'prioritized_values' (List[str], optional): Character values directly triggered by
                  keywords in `user_input`, sorted by hierarchy.
                - 'moral_framework' (str, optional): Notes from the character's moral framework if relevant.
                - 'top_decision_confidence' (float): The score of the highest-ranking matched pattern,
                  representing confidence in that potential decision path.
                - 'default_approach' (str, optional): A fallback suggestion if no strong guidance
                  is generated (e.g., "Respond naturally based on character voice.").
        """
        # --- 1. Contextual Analysis ---
        # Analyze conversation history for recurring topics, pending questions, and recent emotional tones
        history_analysis = self._analyze_conversation_history()
        
        # Analyze current user input for sentiment
        sentiment_scores = self._detect_sentiment_in_input(user_input)
        
        # --- 2. Initialization ---
        # Access decision rules from the character's profile
        decision_rules: Dict[str, Any] = self.character_profile.decision_rules
        # Initialize the guidance dictionary, starting with matched_patterns as an empty list
        guidance: Dict[str, Any] = {'matched_patterns': []} 
        
        # Integrate context analysis results into guidance
        guidance.update(history_analysis) 
        guidance['current_sentiment'] = sentiment_scores
        
        # --- 3. Direct Character Aspects ---
        # Check explicit value hierarchy based on keywords in user input
        values_hierarchy: List[str] = decision_rules.get('values_hierarchy', [])
        if values_hierarchy:
            triggered_values: List[str] = []
            for value in values_hierarchy:
                if self._check_for_keywords(user_input, [value]):
                    triggered_values.append(value)
            if triggered_values:
                triggered_values.sort(key=lambda x: values_hierarchy.index(x))
                guidance['prioritized_values'] = triggered_values
        
        # Include moral framework notes if present
        moral_framework: str = decision_rules.get('moral_framework_notes', '')
        if moral_framework:
            guidance['moral_framework'] = moral_framework
        
        # --- 4. Pattern Matching and Scoring ---
        # Retrieve decision patterns from character profile
        decision_patterns: List[Dict[str, Any]] = decision_rules.get('decision_patterns', [])
        
        # Initial matching of patterns against user input
        raw_matched_patterns: List[Dict[str, Any]] = []
        for pattern_config in decision_patterns:
            score = self._match_decision_pattern(user_input, pattern_config)
            if score > 5.0: # Initial threshold for considering a pattern
                raw_matched_patterns.append({
                    'pattern': pattern_config, # The original pattern configuration
                    'score': score,
                    'response_style': pattern_config.get('then_response_style', ''),
                    'category': pattern_config.get('category', 'general')
                })
        
        # Adjust scores based on alignment with character's value hierarchy
        guidance['matched_patterns'] = self._weigh_against_value_hierarchy(raw_matched_patterns)

        # --- 5. Confidence and Default Approach ---
        # Calculate confidence score based on the top-scoring matched pattern
        if guidance['matched_patterns']:
            guidance['top_decision_confidence'] = guidance['matched_patterns'][0]['score']
        else:
            guidance['top_decision_confidence'] = 0.0
        
        # Determine if a default approach is needed
        # This applies if no prioritized values, moral framework, significant patterns, or strong sentiment are found.
        no_prioritized_values = not guidance.get('prioritized_values')
        no_moral_framework = not guidance.get('moral_framework')
        no_matched_patterns = not guidance.get('matched_patterns')
        neutral_sentiment = not (guidance.get('current_sentiment', {}).get('positive_score', 0) > 0 or \
                                 guidance.get('current_sentiment', {}).get('negative_score', 0) > 0)
        low_confidence = guidance.get('top_decision_confidence', 0.0) <= 5.0

        if no_prioritized_values and no_moral_framework and no_matched_patterns and neutral_sentiment:
            guidance['default_approach'] = "Respond naturally based on character voice."
        elif no_prioritized_values and no_moral_framework and low_confidence and neutral_sentiment : # Also consider low confidence with neutral sentiment
             guidance['default_approach'] = "Respond naturally based on character voice, considering context."
        
        return guidance
