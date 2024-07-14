import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json

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
        self.language_keywords = {
            'c': ['printf', 'scanf', 'malloc', 'free', 'struct', 'typedef'],
            'cpp': ['cout', 'cin', 'vector', 'class', 'namespace', 'template'],
            'python': ['def', 'class', 'import', 'from', 'with', 'as'],
            'java': ['public', 'private', 'class', 'interface', 'extends', 'implements']
        }

    def recognize_intent(self, intent_data, context):
        """
        Recognize the intent from the intent_data and context using semantic analysis.

        Args:
            intent_data (dict): The processed input data.
            context (dict): The context information.

        Returns:
            dict: A dictionary containing the recognized intent, confidence score, and relevant entities.
        """
        text = intent_data['raw_text']
        annotations = self._get_corenlp_annotations(text)

        semantic_intent = self._analyze_semantic_intent(annotations)
        language = self.recognize_language_specific_intent(annotations)
        confidence_score = self._calculate_confidence(semantic_intent, annotations, language)
        relevant_entities = self._extract_relevant_entities(annotations, semantic_intent)

        return {
            'primary_intent': semantic_intent,
            'language': language,
            'confidence_score': confidence_score,
            'relevant_entities': relevant_entities
        }

    def recognize_language_specific_intent(self, annotations):
        tokens = [token['word'].lower() for token in annotations['sentences'][0]['tokens']]
        for language, keywords in self.language_keywords.items():
            if any(keyword in tokens for keyword in keywords):
                return language
        return 'generic'

    def _analyze_semantic_intent(self, annotations):
        """
        Analyze the semantic intent of the given text using CoreNLP annotations.
        """
        tokens = annotations['sentences'][0]['tokens']
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
                'network': ['get', 'post', 'request', 'fetch'],
                'variable': ['set', 'get', 'delete', 'assign'],
                'control_flow': ['if', 'while', 'repeat', 'try', 'for', 'switch'],
                'function': ['define', 'call', 'return', 'invoke'],
                'input_output': ['ask', 'display', 'write', 'read', 'print', 'input'],
                'data_structure': ['create', 'add', 'remove', 'sort', 'search', 'access'],
                'algorithm': ['find', 'calculate', 'check', 'solve', 'optimize']
            }

            for category, keywords in action_categories.items():
                if verb_lemma in keywords:
                    if category == 'create' and object_lemma == 'file':
                        return 'create_file'
                    elif category == 'delete' and object_lemma == 'file':
                        return 'delete_file'
                    elif category == 'update' and object_lemma == 'file':
                        return 'update_file'
                    elif category == 'list' and object_lemma == 'file':
                        return 'list_files'
                    elif category == 'execute' and object_lemma == 'code':
                        return 'execute_code'
                    elif category == 'execute' and object_lemma == 'command':
                        return 'execute_system_command'
                    elif category == 'search' and object_lemma == 'file':
                        return 'search_file'
                    elif category == 'move' and object_lemma == 'file':
                        return 'move_file'
                    elif category == 'copy' and object_lemma == 'file':
                        return 'copy_file'
                    elif category == 'process' and object_lemma == 'process':
                        return 'manage_process'
                    elif category == 'network' and object_lemma == 'request':
                        return 'network_operation'
                    elif category == 'variable' and object_lemma == 'variable':
                        return 'manage_variable'
                    elif category == 'control_flow':
                        return 'control_flow'
                    elif category == 'function':
                        return 'function_operation'
                    elif category == 'input_output':
                        return 'io_operation'
                    elif category == 'data_structure':
                        return 'data_structure_operation'
                    elif category == 'algorithm':
                        return 'algorithm_execution'
                    else:
                        return category

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

        language_score = self._calculate_language_specific_confidence(tokens, language)

        confidence = (dep_score * 0.5) + (abs(sentiment_intensity) * 0.2) + (language_score * 0.3)
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

    def recognize_c_intent(self, tokens, context):
        c_specific_keywords = ['pointer', 'memory', 'allocation', 'struct', 'union', 'typedef']
        if any(keyword in tokens for keyword in c_specific_keywords):
            return 'c_specific'
        return 'generic'

    def recognize_cpp_intent(self, tokens, context):
        cpp_specific_keywords = ['object', 'inheritance', 'polymorphism', 'encapsulation', 'template']
        if any(keyword in tokens for keyword in cpp_specific_keywords):
            return 'cpp_specific'
        return 'generic'

    def recognize_python_intent(self, tokens, context):
        python_specific_keywords = ['list comprehension', 'generator', 'decorator', 'lambda', 'dictionary']
        if any(keyword in tokens for keyword in python_specific_keywords):
            return 'python_specific'
        return 'generic'

    def recognize_java_intent(self, tokens, context):
        java_specific_keywords = ['interface', 'abstract class', 'package', 'garbage collection', 'jvm']
        if any(keyword in tokens for keyword in java_specific_keywords):
            return 'java_specific'
        return 'generic'

    def _calculate_language_specific_confidence(self, tokens, language):
        language_specific_keywords = {
            'c': ['pointer', 'memory', 'allocation', 'struct', 'union', 'typedef'],
            'cpp': ['object', 'inheritance', 'polymorphism', 'encapsulation', 'template'],
            'python': ['list comprehension', 'generator', 'decorator', 'lambda', 'dictionary'],
            'java': ['interface', 'abstract class', 'package', 'garbage collection', 'jvm']
        }

        if language in language_specific_keywords:
            keywords = language_specific_keywords[language]
            matches = sum(1 for keyword in keywords if keyword in tokens)
            return min(matches / len(keywords), 1.0)
        return 0.0