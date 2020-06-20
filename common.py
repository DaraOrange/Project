from tools.perms_creator import get_sentences

def average_num_of_pos(sents, pos):
    n = len(sents)
    ans = 0
    for sent in sents:
        verb_cnt = sum(word['POS'] == pos for word in sent)
        print(sent, verb_cnt)
        ans += verb_cnt
    return ans / n

def get_stat_links(train):
    stat_links = {}
    for sent in train:
        for w in sent:
            if not w["LINK"] in stat_links:
                stat_links[w["LINK"]] = 1
            else:
                stat_links[w["LINK"]] += 1
    return stat_links

def samp_link(link):
    for sent in sorted_sents:
        if (len(sent) > 20):
            continue
        for w in sent:
            if w["LINK"] == link:
                print(w)
                print(sent[int(w["DOM"])-1])
                print_sents([sent])
                return

def print_sents(samp):
    for s in samp:
        samp_snt = []
        for w in s:
            samp_snt.append(w["TEXT"])
        print(" ".join(samp_snt))

input_filename = "../data/converted_perms.txt"
sents = get_sentences(input_filename, True)
print(average_num_of_pos(sents[:5], 'VERB'))