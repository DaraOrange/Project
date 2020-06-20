import itertools
import copy


def find_id(sent, root):
    id = -1
    for i, w in enumerate(sent):
        if w["ID"] == root:
            id = i
    return id


def add_children(sent):
    for word in sent:
        word["CHILDS"] = set()
    for word in sent:
        if word["DOM"] != "0":
            sent[int(word["DOM"]) - 1]["CHILDS"].add(word["ID"])


def generate_tree(sent, root, buffer):
    id = find_id(sent, root)
    if id == -1:
        return
    buffer.add(sent[id]["ID"])
    for ch in sent[id]["CHILDS"]:
        generate_tree(sent, ch, buffer)


def id_comp(w):
    return int(w["ID"])


def find_min_and_max_in_subtree(sent, root):
    id = find_id(sent, root)
    tot_mn, tot_mx = root, root
    for ch in sent[id]["CHILDS"]:
        mn, mx = find_min_and_max_in_subtree(sent, ch)
        if int(mn) < int(tot_mn):
            tot_mn = mn
        if int(mx) > int(tot_mx):
            tot_mx = mx
    return tot_mn, tot_mx


def swap_childs(inp_sent, w, old_to_new):
    sent = copy.deepcopy(inp_sent)
    num_of_childs = len(w["CHILDS"])
    if num_of_childs < 2:
        return None

    ch1 = -1
    ch2 = -1
    for ch in w["CHILDS"]:
        cur_id = find_id(sent, ch)
        if sent[cur_id]["LINK"] in swap_links:
            if ch1 == -1:
                ch1 = cur_id
            else:
                ch2 = cur_id
                break

    if ch1 == -1 or ch2 == -1:
        return None

    if ch1 > ch2:
        t = ch1
        ch1 = ch2
        ch2 = t

    mn1, mx1 = find_min_and_max_in_subtree(sent, sent[ch1]["ID"])
    mn2, mx2 = find_min_and_max_in_subtree(sent, sent[ch2]["ID"])
    cnt = find_id(sent, mn1)

    sent_cp = copy.deepcopy(sent)
    left = sent_cp[cnt]["ID"]
    q_list = []
    for i, w in enumerate(sent):
        if int(w["ID"]) >= int(mn1) and int(w["ID"]) <= int(mx1):
            q_list.append(i)

    for i, w in enumerate(sent):
        if int(w["ID"]) > int(mx1) and int(w["ID"]) <= int(mx2):
            old_to_new[sent[i]["ID"]] = sent_cp[cnt]["ID"]
            sent[i]["ID"] = sent_cp[cnt]["ID"]
            cnt += 1
    right = sent_cp[cnt]["ID"]
    for i in q_list:
        old_to_new[sent[i]["ID"]] = sent_cp[cnt]["ID"]
        sent[i]["ID"] = sent_cp[cnt]["ID"]
        cnt += 1
    sent.sort(key=id_comp)
    # fix parents

    return sent


def generate_candidates(sent, split_links, min_len, lim):
    min_len = min(min_len, len(sent))
    destroy_candidates = list()
    for word in sent:
        if word["LINK"] in split_links:
            destroy_candidates.append(word["ID"])

    new_sents = set()
    counter = 0
    new_sents_size = 0
    it = 0

    for L in range(0, len(destroy_candidates) + 1):
        for subset in itertools.combinations(destroy_candidates, L):
            new_sent = copy.deepcopy(sent)
            add_children(new_sent)
            trees = []
            s_str = ""
            for cand in subset:
                buffer = set()
                generate_tree(new_sent, cand, buffer)
                s_str = " ".join(word["ID"] for word in new_sent if not word["ID"] in buffer)
                new_sent = [word for word in new_sent if not word["ID"] in buffer]

            it += 1
            if it >= 1000:
                new_sents = [[int(id) for id in s.split()] for s in new_sents]
                return new_sents
            if len(new_sent) >= min_len and len(s_str):
                new_sents.add(s_str)
                if len(new_sents) >= lim:
                    new_sents = [[int(id) for id in s.split()] for s in new_sents]
                    return new_sents
    new_sents = [[int(id) for id in s.split()] for s in new_sents]
    return new_sents


def get_perms_result(sents, min_sent_length, num_of_new_sents, links_list):
    new_sents = []

    for id in range(len(sents)):
        perms = generate_candidates(sents[id], links_list, min_sent_length, num_of_new_sents)
        for perm in perms:
            new_sents.append(([sents[id][i - 1] for i in perm]))
            if len(new_sents) >= num_of_new_sents:
                return new_sents
    return new_sents


def remove_useless_nodes(perm_sents):
    se = set()
    new_perm_sents = []
    for sent in perm_sents:
        new_sent = []
        for word in sent:
            if (float(word["ID"]).is_integer()):
                new_sent.append(word)
        new_perm_sents.append(new_sent)
    return new_perm_sents


import random


def get_perms_for_list_of_sentences(perm_sents, num_of_perms, perms_from_one, links_list):
    perm_sents = remove_useless_nodes(perm_sents)
    full_perms = []
    cnt = 0
    add = 0
    for sent in perm_sents:
        cnt += 1
        all_perms = get_perms_result([sent], 7, perms_from_one + add, links_list)
        if len(all_perms) <= perms_from_one + add:
            add = perms_from_one + add - len(all_perms)
        full_perms += all_perms
        if len(full_perms) > num_of_perms:
            break
    return full_perms

def get_perms_result(sents, min_sent_length, num_of_new_sents, links_list):
    new_sents = []

    for id in range(len(sents)):
        perms = generate_candidates(sents[id], links_list, min_sent_length, num_of_new_sents)
        for perm in perms:
            new_sents.append(([sents[id][i - 1] for i in perm]))
            if len(new_sents) >= num_of_new_sents:
                return new_sents
    print(len(new_sents))
    return new_sents

import random

def get_perms_for_list_of_sentences(perm_sents, num_of_perms, perms_from_one, links_list):
    perm_sents = remove_useless_nodes(perm_sents)
    full_perms = []
    cnt = 0
    add = 0
    for sent in perm_sents:
        cnt += 1
        all_perms = get_perms_result([sent], 7, perms_from_one + add, links_list)
        if len(all_perms) <= perms_from_one + add:
            add = perms_from_one + add - len(all_perms)
        full_perms += all_perms
        if len(full_perms) % 500 == 0:
            print(len(full_perms))
        if len(full_perms) > num_of_perms:
            print(cnt)
            break
    return full_perms

def tune_number_of_pos(orig_dataset, perms_dataset, len_after_tuning, pos):
    avg_len_orig = sum([sum([1 for word in sent if word["POS"] == pos]) for sent in orig_dataset]) / len(orig_dataset)
    num_of_words_perm = sum([sum([1 for word in sent if word["POS"] == pos]) for sent in perms_dataset])
    l = 0
    r = len(perms_dataset) - 1
    while abs(num_of_words_perm / (r - l + 1) - avg_len_orig) > 1 and r - l + 1 > len_after_tuning:
        if num_of_words_perm / (r - l + 1) > avg_len_orig:
            num_of_words_perm -= sum([1 for word in perms_dataset[r] if word["POS"] == pos])
            r -= 1
        else:
            num_of_words_perm -= sum([1 for word in perms_dataset[l] if word["POS"] == pos])
            l += 1
    return perms_dataset[l:r+1]

def tune_length(orig_dataset, perms_dataset, len_after_tuning):
    avg_len_orig = sum([len(sent) for sent in orig_dataset]) / len(orig_dataset)
    num_of_words_perm = sum([len(sent) for sent in perms_dataset])
    l = 0
    r = len(perms_dataset) - 1
    while abs(num_of_words_perm / (r - l + 1) - avg_len_orig) > 1 and r - l + 1 > len_after_tuning:
        if num_of_words_perm / (r - l + 1) > avg_len_orig:
            num_of_words_perm -= len(perms_dataset[r])
            r -= 1
        else:
            num_of_words_perm -= len(perms_dataset[l])
            l += 1
    return perms_dataset[l:r+1]