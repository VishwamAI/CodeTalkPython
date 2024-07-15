import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
from langchain import LLMChain, PromptTemplate
from langchain.llms import Gemma  # or LLaMA

class IntentRecognizer:
    """
    A class for recognizing intents from processed input using semantic analysis and NLP techniques.
    """

    def _get_corenlp_annotations(self, text):
        url = "http://localhost:9000"
        properties = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse',
            'outputFormat': 'json'
        }
        data = text.encode('utf-8')
        response = requests.post(url, params={'properties': json.dumps(properties)}, data=data)
        return json.loads(response.text)

    def __init__(self):
        """
        Initialize the IntentRecognizer with necessary NLP components for semantic analysis.
        """
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.sia = SentimentIntensityAnalyzer()
        self.language_specific_patterns = {
            'c': [
                (r'\bprintf\s*\(', 'print_statement'),
                (r'\bscanf\s*\(', 'input_statement'),
                (r'\bmalloc\s*\(', 'memory_allocation'),
                (r'\bfree\s*\(', 'memory_deallocation'),
                (r'\bstruct\s+\w+', 'struct_definition'),
                (r'\btypedef\s+', 'type_definition')
            ],
            'cpp': [
                (r'\bcout\s*<<', 'print_statement'),
                (r'\bcin\s*>>', 'input_statement'),
                (r'\bvector<', 'vector_usage'),
                (r'\bclass\s+\w+', 'class_definition'),
                (r'\bnamespace\s+\w+', 'namespace_definition'),
                (r'\btemplate\s*<', 'template_usage')
            ],
            'python': [
                (r'\bprint\s*\(', 'print_statement'),
                (r'\binput\s*\(', 'input_statement'),
                (r'\bdef\s+\w+\s*\(', 'function_definition'),
                (r'\bclass\s+\w+', 'class_definition'),
                (r'\bimport\s+', 'import_statement'),
                (r'\bfrom\s+\w+\s+import', 'from_import_statement')
            ],
            'java': [
                (r'\bSystem\.out\.println\s*\(', 'print_statement'),
                (r'\bScanner\s+\w+\s*=', 'input_statement'),
                (r'\bpublic\s+class\s+\w+', 'class_definition'),
                (r'\bprivate\s+\w+\s+\w+', 'private_member'),
                (r'\binterface\s+\w+', 'interface_definition'),
                (r'\bextends\s+\w+', 'class_inheritance')
            ]
        }
        self.llm = Gemma()  # or LLaMA()
        self.intent_chain = LLMChain(llm=self.llm, prompt=self._create_intent_prompt())

    def recognize_intent(self, intent_data, context, language='generic'):
        """
        Recognize the intent from the intent_data and context using semantic analysis.

        Args:
            intent_data (dict): The processed input data.
            context (dict): The context information.
            language (str): The programming language to consider for intent recognition.

        Returns:
            dict: A dictionary containing the recognized intent, confidence score, and relevant entities.
        """
        text = intent_data['raw_text']

        # Use LangChain model for intent recognition
        result = self.intent_chain.run(instruction=text)

        # Parse the result and extract information
        lines = result.strip().split('\n')
        primary_intent = lines[0].split(':')[1].strip()
        relevant_entities = self._parse_entities(lines[1])
        confidence_score = float(lines[2].split(':')[1].strip())

        # Use existing methods for language-specific matching
        matched_intent = self._match_intent(word_tokenize(text), language)

        return {
            'primary_intent': primary_intent,
            'matched_intent': matched_intent,
            'language': language,
            'confidence_score': confidence_score,
            'relevant_entities': relevant_entities
        }

    def _match_intent(self, tokens, language):
        instruction = ' '.join(tokens)
        if language in self.language_specific_patterns:
            for pattern, intent in self.language_specific_patterns[language]:
                if re.search(pattern, instruction):
                    return intent
        return 'generic'

    def _analyze_semantic_intent(self, annotations):
        """
        Analyze the semantic intent of the given text using LangChain and CoreNLP annotations.
        """
        tokens = annotations['sentences'][0]['tokens']
        text = ' '.join(token['word'] for token in tokens)

        # Use LangChain model for complex instructions
        result = self.intent_chain.run(instruction=text)
        lines = result.strip().split('\n')
        langchain_intent = lines[0].split(':')[1].strip()

        # If LangChain provides a clear intent, use it; otherwise, fall back to rule-based analysis
        if langchain_intent != 'unknown':
            return langchain_intent

        # Existing rule-based analysis
        dependencies = annotations['sentences'][0]['basicDependencies']

        root_verb = next((token for dep in dependencies if dep['dep'] == 'ROOT' for token in tokens if token['index'] == dep['governor']), None)
        direct_object = next((token for dep in dependencies if dep['dep'] == 'dobj' for token in tokens if token['index'] == dep['dependent']), None)

        if root_verb and direct_object:
            verb_lemma = root_verb['lemma']
            object_lemma = direct_object['lemma']

            action_categories = {
                'create': ['create', 'make', 'generate', 'produce'],
                'delete': ['delete', 'remove', 'erase', 'eliminate'],
                'update': ['update', 'modify', 'change', 'alter'],
                'list': ['list', 'show', 'display', 'enumerate'],
                'execute': ['run', 'execute', 'perform', 'do'],
                'search': ['search', 'find', 'locate'],
                'move': ['move', 'transfer', 'relocate'],
                'copy': ['copy', 'duplicate', 'replicate'],
                'process': ['start', 'stop', 'restart', 'kill'],
                'network': ['get', 'post', 'request', 'fetch', 'download', 'upload'],
                'variable': ['set', 'get', 'delete', 'assign', 'declare', 'initialize'],
                'control_flow': ['if', 'else', 'while', 'for', 'switch', 'break', 'continue'],
                'function': ['define', 'call', 'return', 'invoke', 'create'],
                'input_output': ['ask', 'display', 'write', 'read', 'print', 'input', 'output'],
                'data_structure': ['create', 'add', 'remove', 'sort', 'search', 'access', 'append', 'insert'],
                'algorithm': ['find', 'calculate', 'check', 'solve', 'optimize', 'analyze'],
                'file': ['open', 'close', 'read', 'write', 'append', 'delete', 'rename'],
                'system': ['execute', 'run', 'start', 'stop', 'restart', 'configure']
            }

            for category, keywords in action_categories.items():
                if verb_lemma in keywords:
                    if category == 'file':
                        return f'{verb_lemma}_file'
                    elif category == 'variable':
                        return f'{verb_lemma}_variable'
                    elif category == 'function':
                        return f'{verb_lemma}_function'
                    elif category == 'data_structure':
                        if object_lemma in ['list', 'array']:
                            return f'{verb_lemma}_list'
                        elif object_lemma in ['dictionary', 'dict', 'map']:
                            return f'{verb_lemma}_dictionary'
                        else:
                            return f'{verb_lemma}_data_structure'
                    elif category == 'control_flow':
                        return f'{verb_lemma}_control_flow'
                    elif category == 'network':
                        return f'{verb_lemma}_network'
                    elif category == 'system':
                        return f'{verb_lemma}_system'
                    elif category == 'input_output':
                        return f'{verb_lemma}_io'
                    elif category == 'algorithm':
                        return f'{verb_lemma}_algorithm'
                    else:
                        return f'{category}_{verb_lemma}'

        # Check for specific patterns in the dependencies
        for dep in dependencies:
            if dep['dep'] == 'compound' and dep['governorGloss'] == 'loop':
                return 'create_loop'
            elif dep['dep'] == 'nsubj' and dep['dependentGloss'] == 'if':
                return 'create_conditional'

        return 'unknown'

    def _calculate_confidence(self, intent, annotations, language):
        """
        Calculate the confidence score based on dependency parsing, sentiment analysis, and language-specific factors.
        """
        if intent == 'unknown':
            return 0.0

        tokens = annotations['sentences'][0]['tokens']
        dependencies = annotations['sentences'][0]['basicDependencies']

        expected_deps = ['nsubj', 'dobj', 'prep']
        dep_score = sum(1 for dep in dependencies if dep['dep'] in expected_deps) / len(expected_deps)

        text = ' '.join(token['word'] for token in tokens)
        sentiment_scores = self.sia.polarity_scores(text)
        sentiment_intensity = sentiment_scores['compound']

        matched_intent = self._match_intent([token['word'] for token in tokens], language)
        language_score = self._calculate_language_specific_confidence(tokens, language)
        intent_match_score = 1.0 if matched_intent != 'generic' else 0.5

        confidence = (dep_score * 0.4) + (abs(sentiment_intensity) * 0.2) + (language_score * 0.2) + (intent_match_score * 0.2)
        return min(confidence, 1.0)

    def _extract_relevant_entities(self, annotations, intent):
        """
        Extract entities relevant to the semantic intent using CoreNLP annotations.
        """
        relevant_entities = {}
        ner_tags = [token['ner'] for token in annotations['sentences'][0]['tokens']]

        for token, ner_tag in zip(annotations['sentences'][0]['tokens'], ner_tags):
            if ner_tag != 'O':  # Not 'Other'
                relevant_entities.setdefault(ner_tag, []).append(token['word'])

        dependencies = annotations['sentences'][0]['basicDependencies']
        if intent in ['create_file', 'delete_file', 'update_file']:
            file_name = next((token['word'] for dep in dependencies if dep['dep'] == 'dobj' for token in annotations['sentences'][0]['tokens'] if token['index'] == dep['dependent']), None)
            if file_name:
                relevant_entities['FILE'] = [file_name]

        # Extract additional context-specific entities
        for token in annotations['sentences'][0]['tokens']:
            if token['pos'].startswith('NN'):
                relevant_entities.setdefault('NOUN', []).append(token['word'])
            elif token['pos'].startswith('VB'):
                relevant_entities.setdefault('VERB', []).append(token['word'])
            elif token['pos'].startswith('JJ'):
                relevant_entities.setdefault('ADJECTIVE', []).append(token['word'])
            elif token['pos'] == 'CD':
                relevant_entities.setdefault('NUMBER', []).append(token['word'])

        return relevant_entities

    def _match_intent(self, tokens, language):
        instruction = ' '.join(tokens)
        if language in self.language_specific_patterns:
            for pattern, intent in self.language_specific_patterns[language]:
                if re.search(pattern, instruction):
                    return intent
        return 'generic'

    def _extract_intent_data(self, tokens, matched_intent, language):
        instruction = ' '.join(tokens)
        if language in self.language_specific_patterns:
            for pattern, intent in self.language_specific_patterns[language]:
                if intent == matched_intent:
                    match = re.search(pattern, instruction)
                    if match:
                        return match.group(0)
        return None

    def _calculate_language_specific_confidence(self, tokens, language):
        if language in self.language_specific_patterns:
            patterns = self.language_specific_patterns[language]
            matches = sum(1 for pattern, _ in patterns if any(re.search(pattern, token) for token in tokens))
            return min(matches / len(patterns), 1.0)
        return 0.0