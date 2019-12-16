import os
import re
import sys
import string
import codecs
import subprocess

from pattern.en import parse

stopwords = [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now']

def convert_tag_format(query):
    word = query.split(' ')
    postag = [(x.split('/')[0], x.split('/')[1]) for x in word]
    return postag


def get_pos_tags(text):
    tagged_sent = parse(text)
    return convert_tag_format(tagged_sent), tagged_sent


def normalise(word):
    word = word.lower()
    return word


## conditions for acceptable word: length, stopword
def acceptable_word(word):
    accepted = bool(2 <= len(word) <= 40
                    and word.lower() not in stopwords)
    return accepted


## extract entity from BIO encoding
def extract_entity(filetext):
    last_entity = ''
    last_tag = ''
    mention2entities = {}
    for line in filetext.split('\n'):
        line = line.strip()
        if line == '':
            continue
        line_split = line.split('\t')
        if re.search('B-', line_split[1]):
            if last_entity != '':
                if not last_tag in mention2entities:
                    mention2entities[last_tag] = []
                mention2entities[last_tag].append(last_entity.strip())
            last_entity = line_split[0] + ' '
            last_tag = line_split[1][2:]
        elif re.search('I-', line_split[1]):
            last_entity += line_split[0] + ' '
    if last_entity != '':
        if not last_tag in mention2entities:
            mention2entities[last_tag] = []
        mention2entities[last_tag].append(last_entity.strip())
    return mention2entities


def get_entities_from_phrase(tagged_sent, phrase2consider):
    word = tagged_sent.split(' ')
    bio_tags = [normalise(x.split('/')[0]) + '\t' + x.split('/')[2] for x in word]
    bio_text = '\n'.join(bio_tags)
    mention2entities = extract_entity(bio_text)
    mention2entities.keys()

    ## strip off unacceptable words
    _mention2entities = {}
    for mention in mention2entities:
        if not mention in phrase2consider:
            continue
        _mention2entities[mention] = []
        for entity in mention2entities[mention]:
            _entity = ' '.join([word for word in entity.split(' ') if acceptable_word(word)]).strip()
            if _entity != '':
                _mention2entities[mention].append(_entity)

    entities = []
    for mention in _mention2entities:
        entities.extend(_mention2entities[mention])
    return entities


def get_keywords(text, phrase2consider=['NP', 'ADJP']):
    _text = text
    try:
        postoks, tagged_sent = get_pos_tags(_text)
        entities = get_entities_from_phrase(tagged_sent, phrase2consider)
    except:
        return []
    return entities

### END Keyword extraction ###