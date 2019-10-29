#! /usr/bin/env python3
"""
sentenceParser.py - Extracts a random sample

Copyleft 2019 dragos240
Distributed under the terms of the GPLv3 license.
"""

import re
import random
from os import listdir
from os import path

ALPHA_PAT = re.compile('^[A-Za-z]')
QUOTE_START = '“'
QUOTE_END = '”'
DEFAULT_MIN_WORDS_LENGTH = 4
DEFAULT_CUT_OFF_LENGTH = 5
BOOKS_DIR = path.expanduser("~/.local/share/bookSampler/samples")


def error(msg):
    print("ERR: {}. Exiting...".format(msg))


class TextParser:
    def __init__(self, text,
                 cut_off_length=DEFAULT_CUT_OFF_LENGTH,
                 min_words_length=DEFAULT_MIN_WORDS_LENGTH):
        self.text = text
        self.cut_off_length = cut_off_length
        self.min_words_length = min_words_length
        self.paragraphs = []
        self.getParagraphs()

    def getParagraphs(self):
        for paraIdx, para in enumerate(self.text.splitlines()):
            if re.search(ALPHA_PAT, para.split(' ')[0]):
                self.paragraphs.append(para.rstrip())

    def findFirstMatch(self, pat, para):
        mat = re.search(pat, para)
        if mat:
            matObj = mat.group()
            return (mat.end(), matObj)
        return (-1, None)

    def getRandomParagraph(self):
        para = random.choice(self.paragraphs)
        return para

    def getRandomSentence(self):
        # Paragraph must be DEFAULT_MIN_WORDS_LENGTH long
        para = self.getRandomParagraph()
        sentences = []
        offset = 0
        fullStop = '.'
        while True:
            # Get first full stop and its index
            paraIdx, fullStop = self.findFirstMatch('\?|!|\.', para[offset:])
            if paraIdx == -1:
                # if no more are found
                break
            # sentence from current position to full stop index
            sent = para[offset:offset + paraIdx].lstrip()
            if sent.startswith(QUOTE_START):
                paraIdx, _ = self.findFirstMatch(QUOTE_END, para[offset:])
                sent = para[offset:offset + paraIdx].lstrip()
            offset += paraIdx
            if len(sent) < self.min_words_length:
                continue
            sentences.append(sent)
        # get a random sentence and strip it of whitespace
        sent = random.choice(sentences).strip()
        return sent

    def getRandomSentenceFragment(self):
        sent = self.getRandomSentence()
        words = sent.split(' ')
        # check if sentence is short enough
        if len(words) <= self.cut_off_length:
            return sent
        # try separating at commas
        end = ''
        if sent.startswith(QUOTE_START):
            end = QUOTE_END
        fragment = [x.strip() for x in sent.split(',')][0]
        if len(fragment.split(' ')) <= self.cut_off_length:
            return fragment + end
        # otherwise cut off at cut_off_length
        return " ".join(fragment.split(' ')[:self.cut_off_length]) +\
            '...' + end


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extracts a random sample")
    parser.add_argument('filename', help="The file to sample")
    parser.add_argument('--cut-off', '-c',
                        help="Number of words to cut off at",
                        type=int, default=DEFAULT_CUT_OFF_LENGTH)
    parser.add_argument('--min-words', '-m',
                        help="Minimum number of words in sentence",
                        type=int, default=DEFAULT_MIN_WORDS_LENGTH)
    parser.add_argument('--sample-type', '-t',
                        choices=['paragraph', 'sentence', 'fragment'],
                        help="Specifies what to extract",
                        default='fragment')
    args = parser.parse_args()

    filename = args.filename
    if path.exists(path.join(BOOKS_DIR, filename)):
        filename = path.join(BOOKS_DIR, filename)
        if path.isdir(filename):
            # choose a random file from dir
            book = random.choice(listdir(filename))
            filename = path.join(filename, book)
    elif not path.exists(filename):
        error("Cannot open nonexistent file {}".format(filename))
        return

    cut_off = args.cut_off
    min_words = args.min_words

    if cut_off < min_words:
        cut_off = min_words

    if min_words < 1:
        error("Must have a minimum word count of 1")
        return

    if min_words > cut_off:
        min_words = cut_off

    with open(filename, 'r') as f:
        tp = TextParser(f.read(), cut_off, min_words)
        funcs = {
            'paragraph': tp.getRandomParagraph,
            'sentence': tp.getRandomSentence,
            'fragment': tp.getRandomSentenceFragment
        }
        func = funcs[args.sample_type]
        print(func())


if __name__ == "__main__":
    main()
