import codecs
from tools.CONLL_converter import to_CONLL

def prepare_sent(sent):
    ids = sorted([int(word["ID"]) for word in sent])
    if ids[-1] == len(sent):
        return
    for i in range(len(sent)):
        if ids[i] == i + 1:
            continue
        for j in range(len(sent)):
            if sent[j]["DOM"] == "_root":
                continue
            if int(sent[j]["DOM"]) == ids[i]:
                sent[j]["DOM"] = i + 1
        sent[i]["ID"] = i + 1

def get_sentences(input_filename, train_style = False):
    res = []
    cur_sent = []
    num = 1
    with codecs.open("./" + input_filename, "r", "utf_8" ) as f:
        for line in f:
            if (line == '\n'):
                if (len(cur_sent)):
                    if not train_style:
                        prepare_sent(cur_sent)
                    res.append(cur_sent)
                cur_sent = []
                continue
            if not train_style:
                text, lemma, pos, feat, link, dom, id = line.strip().split("\t")[0:7]
                cur_sent.append({"TEXT": text,
                        "LEMMA": lemma,
                        "POS": pos,
                        "FEAT": feat,
                        "LINK": link,
                        "DOM" : dom,
                        "ID": id})
            else:
                text, lemma, pos, feat = line.strip().split("\t")[0:4]
                cur_sent.append({"TEXT": text,
                        "LEMMA": lemma,
                        "POS": pos,
                        "FEAT": feat})

    return res

import itertools
import copy

def generate_tree(sent, root, buffer):
    buffer.add(sent[int(root) - 1]["ID"])
    for ch in sent[int(root) - 1]["CHILDS"]:
        generate_tree(sent, ch, buffer)

def generate_candidates(sent, split_links, min_len):
    min_len = min(min_len, len(sent))
    destroy_candidates = list()
    for word in sent:
        if word["LINK"] in split_links:
            destroy_candidates.append(word["ID"])

    new_sents = set()
    counter = 0
    new_sents_size = 0
    for L in range(0, len(destroy_candidates) + 1):
        for subset in itertools.combinations(destroy_candidates, L):
            destroy_strategy = set()
            destroy_sent = copy.deepcopy(sent)
            for word in destroy_sent:
                word["CHILDS"] = set()

            for a in subset:
                destroy_strategy.add(a)
            roots = list()
            for word in destroy_sent:
                if word["ID"] in destroy_strategy:
                    word["DOM"] = -1
                    roots.append(word["ID"])
                elif word["DOM"] == -1:
                    roots.append(word["ID"])
                else:
                    if word["DOM"] != "_root" and int(word["DOM"]) <= len(sent):
                        if len(destroy_sent) < int(word["DOM"]):
                            print(destroy_sent)
                        destroy_sent[int(word["DOM"]) - 1]["CHILDS"].add(word["ID"])
            for root in roots:
                buffer = set()
                generate_tree(destroy_sent, root, buffer)
                if len(buffer) >= min_len:
                    b_str = "_".join([str(x) for x in buffer])
                    new_sents.add(b_str)
                    if new_sents_size < len(new_sents):
                        new_sents_size = len(new_sents)
                    counter += 1
                    if counter > 1000:
                        new_sents = [[int(id) for id in s.split("_")] for s in new_sents]
                        return new_sents

    new_sents = [sorted([int(id) for id in s.split("_")]) for s in new_sents]
    return new_sents


def get_perms_result(sents, min_sent_length, links_list, get_max_len=False, process_all=False):
    new_sents = []
    cnt = 0
    ans = []

    for id in range(len(sents)):
        perms = generate_candidates(sents[id], links_list, min_sent_length)
        for perm in perms:
            new_sents.append(([sents[id][i - 1] for i in perm]))
        if len(perms) > len(ans):
            print([word["TEXT"] for word in sents[id]])
            print(sents[id])
            ans = []
            for perm in perms:
                ans.append([sents[id][i - 1] for i in perm])
    if process_all and get_max_len:
        return new_sents, ans

    if process_all:
        return new_sents

    if get_max_len:
        return ans

def write_perms(input_filename):
    sents = get_sentences(input_filename)
    links_list = [
        'unknown',
        'квазиагент',
        'опред',
        '1-компл',
        'релят',
        'предик',
        '2-компл',
        'огранич'
    ]
    all_perms, max_perm = get_perms_result(sents, 5, links_list, True, True)
    to_CONLL(all_perms, "converted_perms.txt")