import logging
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

from Assistant import DiscordBot

class Parser:
    # https://realpython.com/nltk-nlp-python/
    DEFAULT_LANG = 'english'

    def __init__(self, phrase, lang=DEFAULT_LANG):
        self.lang = lang
        self.stop_words = stopwords.words(self.lang)
        self.stemmer = SnowballStemmer(self.lang)
        self.lemmatizer = WordNetLemmatizer()
        self._phrase = phrase
        self.phrase = self._phrase.casefold()
        self.words = self._tokenize()
        self.tags = self._tag()
        self.keywords = {}

    def _chunk(self, attr, grammar):
        """
        Searches for a specified chunk pattern and returns the matching
        chunks if found.
        :param attr: Attribute of the search (NP=noun phrase, etc)
        :param grammar: Regex grammar to search for
        :return: Set of matching chunks if found
        """

        regex = f'{attr}: {{{grammar}}}'
        chunk_parser = nltk.RegexpParser(regex)
        chunks = set()
        tree = chunk_parser.parse(self.tags)
        for element in tree:
            if hasattr(element, 'label') and element.label() == attr:
                chunk = ' '.join(i[0] for i in element)
                chunks.add(chunk)
        return chunks

    def _extract_ne(self):
        """
        Searches for named elements and returns the matching elements
        if found.
        This function will also search for missing dependencies and
        install them if not found.
        :return: Set of mathcing elements if found
        """

        try:
            nltk.data.find('chunkers/maxent_ne_chunker')
        except LookupError as e:
            logging.error(e)
            nltk.download('maxent_ne_chunker')

        try:
            nltk.data.find('corpora/words')
        except LookupError as e:
            logging.error(e)
            nltk.download('words')

        named_elements = set()
        tree = nltk.ne_chunk(self.tags, binary=True)
        for element in tree:
            if hasattr(element, 'label') and element.label() == 'NE':
                named_element = ' '.join(i[0] for i in element)
                named_elements.add(named_element)
        return named_elements

    def _filter(self):
        """
        Filters a list of words against a master stopwords list.
        This function will also search for missing dependencies and install
        them if not found.
        :return: List of filtered words.
        """

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError as e:
            logging.error(e)
            nltk.download('stopwords')
        return [w for w in self.words if w.casefold() not in self.stop_words]

    def _lemmatize(self):
        """
        Lemmatizes a list of words.
        This function will also search for missing dependencies and install
        them if not found.
        :return: List of filtered words.
        """

        try:
            nltk.data.find('corpora/wordnet')
        except LookupError as e:
            logging.error(e)
            nltk.download('wordnet')

        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError as e:
            logging.error(e)
            nltk.download('omw-1.4')

        return [self.lemmatizer.lemmatize(word) for word in self.words]

    def _stem(self):
        """
        Stems a list of words.
        :return: List of Stemmed words.
        """

        return [self.stemmer.stem(word) for word in self.words]

    def _tag(self):
        """
        Tags a list of words with their major parts of speech.
        This function will also search for missing dependencies and install
        them if not found.
        :return: List of tagged words.
        """

        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError as e:
            logging.error(e)
            nltk.download('averaged_perceptron_tagger')

        return nltk.pos_tag(self.words)

    def _tokenize(self):
        """
        Tokenizes a phrase into a list of words.
        This function will also search for missing dependencies and install
        them if not found.
        :return: List of tokenized words.
        """

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError as e:
            logging.error(e)
            nltk.download('punkt')

        return word_tokenize(self.phrase)

    def parse(self):
        """
        Parses a phrase and attemps to extract keywords from it.
        :return: Handler with any found keywords
        """

        logging.debug(f"WORDS: {self.words}")
        logging.debug(f"TAGGED WORDS: {self.tags}")

        search = Searcher(self)
        self.keywords = {
            'hello': search.hello(),
            'google': search.google()
        }
        return Handler(self.keywords)


class Searcher:
    def __init__(self, parser):
        self.parser = parser

    def _search(self, regex, return_group=0):
        """
        Searches a string with a specified regular expression pattern.
        :param regex: Regular expression pattern
        :param return_group: Int number of a specific group to return
        :return: Regex search results group if found
        """

        result = None
        matches = re.search(regex, self.parser.phrase)
        if hasattr(matches, 'groups'):
            if return_group:
                result = matches.group(return_group)
            else:
                result = matches.groups()
        return result

    def hello(self, regex=None):
        """
        Performs a regular expression search for a greeting.
        :param regex: Regular expression override
        :return: True if found
        """

        if regex is None:
            regex = re.compile(
                r'(hi|hello|greetings|hiya|hey|hola)\s', flags=re.IGNORECASE
            )
        hello = self._search(regex, 1)
        if hello is not None:
            hello = True
        return hello

    def google(self, regex=None):
        """
        Performs a regular expression search for a greeting.
        :param regex: Regular expression override
        :return: True if found
        """

        if regex is None:
            regex = re.compile(
                r'((how\s+do\s+(?:i|you))|'
                r'(why\s+does\s+my)'
                r'.*)', flags=re.IGNORECASE
            )
        help = self._search(regex, 1)
        if help is not None:
            help = True
        return help


class Handler:
    def __init__(self, keywords):
        self.keywords = [k for k, v in keywords.items() if v is not None]

        # Handlers dict is composed of a Tuple of required keywords for
        # a key along with a list of handlers that can be triggered from
        # those keywords
        self.handlers = {
            ('hello',): self._say_hello,
            ('google',): self._lmgt,
        }

    async def _lmgt(self, message, callback=None):
        lmgt = 'https://letmegooglethat.com'

        content = message.content

        if '?' in content:
            content = content.split('?')[0]

        regex = re.compile(
            r'((how\s+do\s+(?:i|you))|'
            r'(why\s+does\s+my)'
            r'.*)', flags=re.IGNORECASE
        )

        query_string = re.search(regex, content)

        query = re.sub(r'[^\w]+', '+', query_string.group(1))
        if query.endswith('+'):
            query = query[:-1]

        await DiscordBot.fake_type(message.channel, seconds=2)
        await message.reply(f"{lmgt}/?q={query}")

    async def _say_hello(self, message, callback=None):
        await DiscordBot.fake_type(message.channel)
        await message.reply(f"Hello {message.author.mention}.")

    def find_handler(self):
        """
        Loops through the keywords to find any handlers that can be
        triggered.
        :return: List of handler Tuples
        """

        handlers = []
        for trigger_keywords, function in self.handlers.items():
            if all(keyword in self.keywords for keyword in trigger_keywords):
                handlers.append(function)
        return handlers
