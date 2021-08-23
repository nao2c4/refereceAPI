from utils.reference import Reference


def jjap_like(ref: 'Reference', initial: bool = True) -> str:
    return '{}. "{}", {} ({}), {} ({}), {} ({}).\nDOI: {}{}'.format(
        _get_authors_jjap_like(ref, initial),
        ref.capitalized_title,
        ref.full_journal,
        ref.short_journal,
        ref.volume,
        ref.issue,
        ref.page,
        ref.year,
        ref.url_doi,
        ref.doi,
    )


def bibtex(ref: 'Reference') -> str:
    return '\n'.join([
        '@article{',
        ('\n' + ' '*4).join([
            '  {},'.format(ref.doi),
            'author={{{}}},'.format(' and '.join(ref.authors)),
            'year={{{}}},'.format(ref.year),
            'title={{{}}},'.format(ref.capitalized_title),
            'journal={{{}}},'.format(ref.full_journal),
            'volume={{{}}},'.format(ref.volume),
            'number={{{}}},'.format(ref.issue),
            'pages={{{}}},'.format(ref.page),
            'doi={{{}{}}},'.format(ref.url_doi, ref.doi),
        ])
        ,'}',
    ])


def _get_authors_jjap_like(ref: 'Reference', initial: bool = True) -> str:
    authors = (
        ref.initial_authors
        if initial
        else ref.authors
    )
    size = len(authors)
    if size == 0:
        return ''
    if size == 1:
        return authors[0]
    if size == 2:
        return authors[0] + ', ' + authors[1]
    return ', '.join(authors[:-1]) + ', and ' + authors[-1]
