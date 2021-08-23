import re
import requests


class Reference:
    
    url_base = r'https://api.crossref.org/works/'
    url_doi = r'https://doi.org/'
    
    def __init__(self, debug: bool = False):
        self._debug = debug
        self.fn = lambda x: (print(x) if self._debug else x)

    def __call__(self, doi: str) -> 'Reference':
        self.doi = doi
        response = requests.get(self.url_base + self.doi)
        if response.status_code != 200:
            self._set_dummy()
            return self
        self.raw_data = response.json()
        self.data = self.raw_data['message']
        self.parse()
        return self
    
    def parse(self):
        self.fn(self._get_title())
        self.fn(self._get_authors())
        self.fn(self._get_journal())
        self.fn(self._get_details())
        self.fn(self._get_year())
    
    def _get_title(self) -> bool:
        self.title, self._title = self._get_params('title')
        self.capitalized_title = self._capitalize(self.title)
        return bool(self._title)
    
    def _get_authors(self) -> int:
        self.authors = list(filter(lambda s: s is not None, map(self._get_author, self.data['author'])))
        self.initial_authors = list(filter(lambda s: s is not None, map(self._get_initial_author, self.data['author'])))
        return len(self.authors)
    
    def _get_journal(self) -> bool:
        self.full_journal, self._full_journal = self._get_params('container-title')
        self.short_journal, self._short_journal = self._get_params('short-container-title')
        return bool(self._full_journal) or bool(self._short_journal)
    
    def _get_details(self) -> bool:
        self.volume, _ = self._get_params('volume')
        self.issue, _ = self._get_params('issue')
        self.page, _ = self._get_params('page')
        return (self.volume is None) or (self.issue is None) or (self.page is None)
        
    def _get_params(self, key: str) -> tuple:
        if key not in self.data.keys():
            return '', []
        value = self.data[key]
        if not(value):
            return '', []
        if type(value) != list:
            return value, []
        return value[0], value[1:]

    def _get_year(self) -> bool:
        if 'issued' not in self.data:
            self.year = 'Unknown'
            return True
        if 'date-parts' not in self.data['issued']:
            self.year = 'Unknown'
            return True
        if not(self.data['issued']['date-parts']):
            self.year = 'Unknown'
            return True
        self.year = self.data['issued']['date-parts'][0][0]
        return False
    
    def _get_year_old(self) -> bool:
        if 'license' not in self.data:
            self.year = 'Unknown'
            return True
        years = list(map(lambda x: x['start']['date-parts'][0][0], self.data['license']))
        self.year = years[0]
        return any([years[0] != year for year in years[1:]])
    
    def _set_dummy(self):
        self.title = ''
        self.capitalized_title = ''
        self.authors = []
        self.initial_authors = []
        self.full_journal = ''
        self.short_journal = ''
        self.volume = ''
        self.issue = ''
        self.page = ''
        self.year = '404'
        
    def _capitalize(self, title: str):
        return re.sub(
            r"[A-Za-z]+('[A-Za-z]+)?",
            lambda mo: self._capitalize_word(mo.group(0)),
            title,
        )

    @staticmethod
    def _get_author(dic: dict) -> str:
        if 'family' not in dic:
            return None
        if 'given' not in dic:
            return dic['family']
        return ' '.join([dic['given'], dic['family']])
    
    @staticmethod
    def _get_initial_author(dic: dict) -> str:
        if 'family' not in dic:
            return None
        if 'given' not in dic:
            return dic['family']
        names = (dic['given'] + ' ' + dic['family']).split(' ')
        return re.sub(
            r"[A-Za-z]+('[A-Za-z]+)?",
            lambda mo: mo.group(0)[0] + '.',
            ' '.join(names[:-1]),
        ) + ' ' + names[-1]
    
    @staticmethod
    def _capitalize_word(word: str) -> str:
        if any([word == s for s in [
            'a', 'an', 'the', 'and', 'as', 'but', 'for', 'if',
            'nor', 'once', 'or', 'so', 'than', 'till', 'when', 'yet',
            'at', 'by', 'down', 'for', 'from', 'in', 'into', 'like',
            'near', 'of', 'off', 'on', 'onto', 'out', 'over', 'past',
            'to', 'up', 'upon', 'with',
        ]]):
            return word
        return word.capitalize()
