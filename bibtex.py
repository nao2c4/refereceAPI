from utils import Reference, bibtex
import pyperclip


if __name__ == '__main__':
    ref = Reference()
    while True:
        doi = input('DOI: ')
        ref(doi.replace('_', '/'))
        print(bibtex(ref))
        pyperclip.copy(bibtex(ref))
