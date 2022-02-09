#!/usr/bin/env python3
from shutil import which
from pathlib import Path

import os
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from academic.import_bibtex import parse_bibtex_entry, slugify
from academic.editFM import EditableFM

_ROOT = os.path.dirname(__file__)

# A mapping from .bib field to a academic field.
# If a value is None, we don't convert it to academic field.
META_FIELD_MAPPING = {
    'www-url': 'url_web',
    'www-git': 'url_code',
    'award': None
}

def read_conf():
    """
    Returns a mapping between a conference name to its metadata
    """
    conf_bib = os.path.join(os.path.abspath(_ROOT), '../assets/pubs/conf.bib')
    assert(os.path.exists(conf_bib))

    confs = {}
    parser = BibTexParser(common_strings=True)
    bib_database =  bibtexparser.load(open(conf_bib), parser)
    for entry in bib_database.entries:
        id = entry['ID']
        del entry['ID']
        confs[id] = entry
    return confs

def update_conf(entry, confs):
    # If 'crossref' exists in a pub entry, update it with conference data
    if 'crossref' in entry:
        title = entry['title']
        conf = confs[entry['crossref']]
        entry.update(conf)
        entry['title'] = title
        del entry['crossref']

def create_meta_fields(entry):
    meta_fields = {}
    for key in META_FIELD_MAPPING.keys():
        if entry.get(key):
            meta_fields[key] = entry.get(key)
            del entry[key]
    return meta_fields

def update_meta_fields(page, meta_fields):
    for key, value in meta_fields.items():
        page_key = META_FIELD_MAPPING[key]
        if page_key is not None:
            page.fm[page_key] = value

def cleanup_page(entry):
    # TODO: Can we make incremental updates?
    pub_dir = 'publication'
    bundle_path = f"content/{pub_dir}/{slugify(entry['ID'])}"
    markdown_path = os.path.join(bundle_path, "index.md")
    if os.path.exists(markdown_path):
        os.unlink(markdown_path)

    cite_path = os.path.join(bundle_path, "cite.bib")
    if os.path.exists(cite_path):
        os.unlink(cite_path)

def create_page(entry):
    cleanup_page(entry)
    page = parse_bibtex_entry(entry, overwrite=True)
    # Delete 'publishDate' that changes our page even without any modification
    del page.fm["publishDate"]
    del page.fm["lastmod"]
    return page

def update_resources(page, entry):
    static_dir = os.path.join(_ROOT, '../static')
    resource_dir = os.path.join(static_dir, f"pubs/{entry['year']}/{entry['ID']}")
    abstract = resource_dir + '-abstract.md'
    if os.path.exists(abstract):
        page.fm['abstract'] = open(abstract).read()

    slides = resource_dir + '-slides.pdf'
    if os.path.exists(slides):
        page.fm['url_slides'] = os.path.relpath(slides, static_dir)

    paper = resource_dir + '.pdf'
    if os.path.exists(paper):
        page.fm['url_paper'] = os.path.relpath(paper, static_dir)

def main():
    confs = read_conf()

    parser = BibTexParser(common_strings=True)
    pub_bib = os.path.join(os.path.abspath(_ROOT), '../assets/pubs/pub.bib')
    bib_database = bibtexparser.load(open(pub_bib), parser)

    for i, entry in enumerate(bib_database.entries):
        update_conf(entry, confs)

        meta_fields = create_meta_fields(entry)
        page = create_page(entry)

        update_resources(page, entry)
        update_meta_fields(page, meta_fields)
        page.dump()

if __name__ == '__main__':
    main()
