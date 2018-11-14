
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/shravanc/Downloads/vision-project-a05a746e5354.json"

"""Outlines document text given an image.
Example:
    python doctext.py resources/text_menu.jpg
"""
# [START vision_document_text_tutorial]
# [START vision_document_text_tutorial_imports]
import argparse
from enum import Enum
import io
import spacy
from spacy.matcher import Matcher

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw


all_entities = []
def add_event_ent(matcher, doc, i, matches):
    label = doc.vocab.strings[matches[i][0]]
    print('Label====>', label)
    _, start, end = matches[i]
    entity_type = None
    entity_type = doc.vocab.strings[label]

    entity = (entity_type, start, end)
    doc.ents += (entity,)
    all_entities.append(doc[start:end].text)


def initialize_spacy():
    nlp = spacy.load('en_core_web_sm')

    ner = nlp.get_pipe('ner')
    ner.add_label('LICENSE')
    ner.add_label('EXPIRY')
    ner.add_label('ISSUED')

    matcher = Matcher(nlp.vocab)

    matcher.add('LICENSE', add_event_ent,
                [{'LOWER': 'license'}, {'LOWER': 'number'}, {'ORTH': ':'}, {'IS_DIGIT': True}],
                [{'LOWER': 'license'}, {'LOWER': 'number'}, {'ORTH': ':'}, {}],
                [{'LOWER': 'credential'}, {'LOWER': 'number'}, {'ORTH': ':'}, {'ENT_TYPE': 'CARDINAL'}],
                [{'LOWER': 'identification'}, {'LOWER': 'number'}, {'ORTH': ':'}, {'ENT_TYPE': 'CARDINAL'}],
                [{'LOWER': 'identification'}, {'LOWER': 'number'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'license'}, {'LOWER': 'no'}, {'ORTH': '.'}, {'IS_DIGIT': True}],
                [{'LOWER': 'license'}, {'LOWER': 'no'}, {'ORTH': '.'}, {'IS_DIGIT': True}, {'ORTH': '.'}, {'IS_DIGIT': True}],
                )

    matcher.add('ISSUED', add_event_ent,
                [{'LOWER': 'date'}, {'LOWER': 'issued'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'issued'}, {'ORTH': 'on'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'issuance'}, {'lower': 'date'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'effective'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                )

    matcher.add('EXPIRY', add_event_ent,
                [{'LOWER': 'date'}, {'LOWER': 'issued'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'expires'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'expiration'}, {'LOWER': 'date'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'expiration'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
                [{'LOWER': 'expire'}, {'LOWER': 'on'}, {'ORTH': ':'}, {'ENT_TYPE': 'DATE'}],
            )

    return nlp, matcher

def get_all_entities(paragraphs):
    nlp, matcher = initialize_spacy()

    all_entities = []
    for each_para in paragraphs:
        doc = nlp(u"{}".format(each_para))
        matcher(doc)

        if doc.ents:
            for ent in doc.ents:
                if ent.label_ in ('LICENSE','EXPIRY','ISSUED','GPE'):
                    all_entities.append(ent.text)
        
    return all_entities


def get_all_sentences(document):
    list_of_paragraphs = []
    lop = []
    blocks = {}
    paragraphs = {}
    words = []
    letters = []
    for page in document.pages:
        for block_index, block in enumerate(page.blocks):
            for index, paragraph in enumerate(block.paragraphs):
                words = []
                for word in paragraph.words:
                    letters = []
                    for symbol in word.symbols:
                        letters.append(symbol.text)
                    words.append(''.join(letters))
                    # print('========WORD=======')
                    # print(word)
                # print('========WORDS=======')
                # print(words)
                lop.append(' '.join(words))
            paragraphs["paragraph_{}".format(index)] = ' '.join(words)
#            blocks["block_{}".format(block_index)] = paragraphs
            list_of_paragraphs.append(' '.join(words))
            paragraphs = {}
 
    print("**********************************VISION DATA*********************************")
    # print(blocks)
    blocks["list_of_paragraphs"] = lop #list_of_paragraphs
    blocks["spacy"] = get_all_entities(lop)
    # blocks["entities"] = get_all_entities(lop)
#   [d for d in exampleSet if d['type'] in keyValList]
    # blocks["state"] = [ e for e in blocks["entities"] if e["entities"]["label"] == "GPE"]
    #blocks["state"] = blocks["entities"] #.select{|h| h["entities"]["label"] == "GPE" }
#    blocks["lop"] = lop
    return blocks

def get_document_bounds(image_file):
    # [START vision_document_text_tutorial_detect_bounds]
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    print("********************************document************************************")
    return get_all_sentences(document)



















