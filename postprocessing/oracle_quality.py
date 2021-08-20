'''
Copyright (c) 2021, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
'''
import nltk
import os
from rouge import rouge_results_to_str, test_rouge


def write_to_file(file, line, gen):
    for g in gen:
        file.write(line + "\t" + g + "\n")
    file.write('\n')


def get_best_gen(gt, generations):
    output = ""
    bleu_max = 0
    for l1 in generations:
        t = nltk.translate.bleu_score.sentence_bleu([gt.split(' ')], l1.split(' '), weights=(0.5, 0.5))
        if t > bleu_max:
            bleu_max = t
            output = l1
    return output


def read_baseline(filename, count):
    file = open(filename)
    lines = [line.strip() for line in file.readlines()]

    best_gens = {}
    references = []
    for idx in range(0, len(lines), count+3):
        ref = lines[idx + 1]
        gen = [lines[idx + k] for k in range(2, count + 2)]

        best_gen = get_best_gen(ref, gen)
        best_gens[ref] = best_gen
        references.append(ref)

    return best_gens


def read_control(foldername):
    subfolders = ['head0', '0.2', '0.4', '0.6', '0.8', 'head1']
    data = {}
    for folder in subfolders:
        file = open(os.path.join(foldername, folder, 'dev_outfinal.txt'))
        lines = [line.strip() for line in file.readlines()]

        for idx in range(0, len(lines), 4):
            ref = lines[idx + 1]
            gen = lines[idx + 2]

            if ref in data.keys():
                data[ref].append(gen)
            else:
                data[ref] = [gen]

    best_gens = {}
    for ref in data:
        best_gen = get_best_gen(ref, data[ref])
        best_gens[ref] = best_gen

    return best_gens


if __name__ == "__main__":

    baseline_file = '../../data/newsroom_old/mixed/20k/model-bart/dev_outfinal5.txt'
    control_folder = '../../data/newsroom_old/mixed/20k_w_gates/seen_unseen_sent/model-bart-sent-4/'

    baseline_gens = read_baseline(baseline_file, count=6)
    control_gens = read_control(control_folder)

    refs = set(baseline_gens).intersection(set(control_gens))

    references = []
    baseline_outputs = []
    control_outputs = []
    for r in refs:
        references.append(r)
        baseline_outputs.append(baseline_gens[r])
        control_outputs.append(control_gens[r])

    results_dict_baseline = test_rouge(baseline_outputs, references, 1)
    results_dict_control = test_rouge(control_outputs, references, 1)

    print(rouge_results_to_str(results_dict_baseline))
    print(rouge_results_to_str(results_dict_control))

