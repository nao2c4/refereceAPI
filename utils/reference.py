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
        self.authors = list(map(self._get_author, self.data['author']))
        self.initial_authors = list(map(self._get_initial_author, self.data['author']))
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
        self.authors = []
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

    def jjap_like(self, initial: bool = True) -> str:
        return '{}. "{}", {} ({}), {} ({}), {} ({}).\nDOI: {}{}'.format(
            self._get_authors_jjap_like(initial),
            self.capitalized_title,
            self.full_journal,
            self.short_journal,
            self.volume,
            self.issue,
            self.page,
            self.year,
            self.url_doi,
            self.doi,
        )
    
    def bibtex(self) -> str:
        return '\n'.join([
            '@article{',
            ('\n' + ' '*4).join([
                '  {},'.format(self.doi),
                'author={{{}}},'.format(' and '.join(self.authors)),
                'year={{{}}},'.format(self.year),
                'title={{{}}},'.format(self.capitalized_title),
                'journal={{{}}},'.format(self.full_journal),
                'volume={{{}}},'.format(self.volume),
                'number={{{}}},'.format(self.issue),
                'pages={{{}}},'.format(self.page),
                'doi={{{}{}}},'.format(self.url_doi, self.doi),
            ])
            ,'}',
        ])
    
    def _get_authors_jjap_like(self, initial: bool = True) -> str:
        authors = (
            self.initial_authors
            if initial
            else self.authors
        )
        size = len(authors)
        if size == 0:
            return ''
        if size == 1:
            return authors[0]
        if size == 2:
            return authors[0] + ', ' + authors[1]
        return ', '.join(authors[:-1]) + ', and ' + authors[-1]

    @staticmethod
    def _get_author(dic: dict) -> str:
        if 'given' not in dic:
            return dic['family']
        return ' '.join([dic['given'], dic['family']])
    
    @staticmethod
    def _get_initial_author(dic: dict) -> str:
        if 'given' not in dic:
            return dic['family']
        givens = dic['given'].split(' ')
        return ' '.join([name[0] + '.' for name in givens] + [dic['family']])
    
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
