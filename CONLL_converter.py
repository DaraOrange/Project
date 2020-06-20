import re
import codecs
import os

def sents_from_CONLL(filename):
    sents = []
    cur_sent = []
    with codecs.open(filename, "r", "utf_8" ) as f:
        cnt = 0
        for line in f:
            if line[0] == "#" or line[0] == "=":
                continue
            if (line == '\n'):
                if len(cur_sent):
                    sents.append(cur_sent)
                cur_sent = []
                cnt += 1
                continue
            line = line[:-1]
            if (line[0] == '#'):
                continue
            id, text, lemma, pos, _, feat, dom, link, _, _ = line.strip().split("\t")[0:10]
            cur_sent.append({"TEXT": text,
                    "LEMMA": lemma,
                    "POS": pos,
                    "FEAT": feat,
                    "LINK": link,
                    "DOM" : dom,
                    "ID": id})
    return sents

def sent_to_CONLL(sent, fs, save_tree_info=False):
    str_sent = list()
    for id in range(0, len(sent)):
        for f in ["FEAT", "LEMMA", "POS", "TEXT"]:
            if sent[id][f] == "":
                sent[id][f] = "_"
        str_word = (
            "\t".join(
                [
                    sent[id]["TEXT"],
                    sent[id]["LEMMA"],
                    sent[id]["POS"],
                    sent[id]["FEAT"]
                ]
            )
        )
        if (cnt < 100):
            print(str_word)
        if save_tree_info:
            str_word += (
                "\t".join(
                    [
                        sent[id]["LINK"],
                        sent[id]["DOM"]
                    ]
                )
            )
        str_sent.append(str_word)
        str_sent.append("\n")
    str_sent.append("\n")
    fs.writelines(str_sent)
    fs.flush()

def to_CONLL(sent_list, fn, save_tree_info = False):
    fs = open(fn, 'w')
    for sent in sent_list:
        sent_to_CONLL(sent, fs)