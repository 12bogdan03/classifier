import json
from splitter import TextSplitter
import string

lemmas_dict = json.load(open('lemmas.json'))
lemmas_dict = dict((k.lower(), v.lower()) for k, v in lemmas_dict.items())

s = TextSplitter()

with open('stop_words.txt', 'r+', encoding="utf-8") as f:
    stop_words = [i.strip() for i in f.readlines()]


def get_lemma(word):
    return lemmas_dict.get(word)


def lemmatize_text(text):
    try:
        tokens = text.split()
    except AttributeError:
        print(text)
    for i, token in enumerate(tokens):
        lemma = get_lemma(token)
        if lemma:
            tokens[i] = lemma
    return ' '.join(tokens)


def lemmatize_text_to_tokens(text):
    tokens = s.split_on_words(text)
    for i, token in enumerate(tokens):
        for symbol in string.punctuation:
            token = token.strip(symbol)
        if token.strip().lower() not in stop_words and \
            token not in string.punctuation and \
                not token.isdigit():
            lemma = get_lemma(token.strip().lower())
            if lemma:
                tokens[i] = lemma
            else:
                tokens[i] = token.strip().lower()
        else:
            tokens[i] = None

    return [t for t in tokens if t]
