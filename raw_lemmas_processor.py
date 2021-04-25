import json


word_lemma_dict = dict()
with open('dict_corp_lt.txt', 'r') as f:
    word_lemma_list = [(l.split()[0].strip(), l.split()[1].strip())
                       for l in f.readlines()]


for lemma, word in word_lemma_list:
    if lemma in word_lemma_dict:
        continue
    else:
        word_lemma_dict[lemma] = word


json.dump(word_lemma_dict,
          open('lemmas.json', 'w'),
          sort_keys=True,
          indent=4)
