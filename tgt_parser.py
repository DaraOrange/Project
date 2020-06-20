import codecs

def parse_tgt(input_filename):
    import re
    import codecs
    import os

    cnt = 0
    if input_filename[-4:] != ".tgt":
        return

    start_flag = 0
    eat_garbage_before_sentence = 0
    eat_garbage_after_sentence = 0
    c = 0
    sent_list = []
    sent_flag = True
    words = []
    st = {}

    rev_keys = {
        'Animacy': {'Anim', 'Inan'},
        'Case': {'Acc', 'Dat', 'Gen', 'Ins', 'Loc', 'Nom'},
        'Gender': {'Fem', 'Masc', 'Neut'},
        'Number': {'Plur', 'Sing'},
        'Degree': {'Cmp', 'Pos'},
        'Mood': {'Imp', 'Ind'},
        'Tense': {'Notpast', 'Past'},
        'VerbForm': {'Conv', 'Fin', 'Inf'},
        'Voice': {'Act', 'Mid'},
        'Person': {'1', '2', '3'},
        'Variant': {'Short'},
        'NumForm': {'Digit'}}

    keys = {}

    for item in rev_keys:
        for val in rev_keys[item]:
            keys[val] = item

    eng_feat_val = {"ИМ": "Nom", "РОД": "Gen", "ДАТ": "Dat", "ВИН": "Acc", "ТВОР": "Ins", "МЕСТН": "Loc",
                    "ПР": "Loc", "ЖЕН": "Fem", "МУЖ": "Masc", "СРЕД": "Neut", "ЕД": "Sing", 'МН': "Plur",
                    "НЕОД": "Inan", "ОД": "Anim", "КР": "Short", "ПРЕВ": "Pos",
                    "ДЕЕПР": "Conv", "ПРОШ": "Past", "НЕПРОШ": "Notpast", "НАСТ": "Notpast", "ИЗЪЯВ": "Ind",
                    "ИНФ": "Inf",
                    "СРАВ": "Cmp", "3-Л": "3", "2-Л": "2", "1-Л": "1", "ПОВ": "Imp"}

    garbage = ['СОВ', 'СТРАД', 'НЕСОВ', 'ПРИЧ']

    with codecs.open(input_filename, "r", "utf_8") as f:
        for line in f:
            if not start_flag:
                if not "<body>" in line:
                    continue
                else:
                    start_flag = 1
                    eat_garbage_before_sentence = 1
            else:
                if '</S>' in line:
                    if sent_flag:
                        sent_list.append(words)
                    sent_flag = True
                    words = []
                    eat_garbage_before_sentence = 1
                    continue
                if line == "</body>":
                    break
                if eat_garbage_before_sentence:
                    eat_garbage_before_sentence = 0
                    continue
                result = re.findall(r'<.*\">', line)
                text = re.findall(r'>.*<', line)
                if len(result) == 0 or len(text) == 0:
                    continue
                text = text[0][1:-1]
                feats = re.findall(r'[.\w-]+=\"[.\w+ -]+\"', result[0])
                word = {"TEXT": text}
                for feat in feats:
                    key, value = feat.split('=')
                    value = value[1:-1]
                    if key in {"DOM", "LINK", "LEMMA", "ID"}:
                        word[key] = value
                    if key == "FEAT":
                        word_feats = value.split()
                        if word_feats[0] in {"NUM", "PART", "CONJ", "ADV"}:
                            word["POS"] = word_feats[0]
                        if word_feats[0] == "PR":
                            word["POS"] = "ADP"
                        if len(word_feats) == 1:
                            word["FEAT"] = "_"
                            continue

                        if word_feats[0] == 'S':
                            word["POS"] = "NOUN"
                        if word_feats[0] == 'V':
                            word["POS"] = "VERB"
                            for feat in word_feats:
                                if feat == 'ПРИЧ':
                                    word["POS"] = "ADJ"
                                    break
                        if word_feats[0] == 'A':
                            word["POS"] = "ADJ"
                        if not "POS" in word:
                            sent_flag = False
                            continue
                        if not word["POS"] in st:
                            st[word["POS"]] = set()

                        word_feats = word_feats[1:]
                        feat_list = []
                        for feat in word_feats:
                            if not feat in garbage:
                                if not feat in eng_feat_val:
                                    continue
                                val = eng_feat_val[feat]
                                feat_list.append(keys[val] + '=' + val)
                            st[word["POS"]].add(feat)
                        if word["POS"] == "ADJ" and not "Degree=Cmp" in feat_list:
                            feat_list.append("Degree=Pos")
                        word["FEAT"] = '|'.join(feat_list)
                if (not "LEMMA" in word) or (not "POS" in word) or (not "FEAT" in word) or (not "TEXT" in word):
                    sent_flag = False
                    continue
                words.append(word)

    return sent_list