#!/usr/bin/python
import matplotlib.pyplot as plt 
import random
from collections import Counter
import numpy as np

import matplotlib.patches as mpatches
CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']
color1 = CB_color_cycle[0]
color2 = CB_color_cycle[4]
color3 = CB_color_cycle[8]

colors = {'pull': color1,
          'push': color2,
          'push&pull': color3}

DEBUG = False

class Node:
    def __init__(self, use_age=False, use_median=False, t_max=100):
        self.rumor = False
        self.neighbor = None
        self.next_rumor = False
        self.use_age = use_age
        self.age = None

        # median counter state
        self.use_median = use_median
        self.counter = 0
        self.t_max = t_max
        self.next_counters = []

    def draw_neighbor(self, arr):
        self.neighbor = random.choice(arr)

    def set_neighbor(self, neighbor):
        self.neighbor = neighbor

    # if we have the rumor
    #  - we can send the rumor over as their next_rumor
    # if they have the rumor
    #  - we can take the rumor and set it as our next_rumor

    def pull(self):
        if self.neighbor.rumor:
            self.next_rumor = self.neighbor.rumor
            return 1
        return 0

    def push(self):
        if self.rumor: 
            self.neighbor.next_rumor = self.rumor 
            return 1
        return 0

    def push_and_pull(self):
        val = 0
        if self.rumor and self.neighbor.rumor:
            self.next_counters.append(self.counter)
            self.neighbor.next_counters.append(self.counter)
            val += 2
        else:
            if self.rumor:
                self.neighbor.next_rumor = self.rumor
                val += 1
            elif self.neighbor.rumor:
                self.next_rumor = self.neighbor.rumor
                val += 1
        return val

    def update_state(self):
        if not self.use_median:
            if self.rumor:
                return True
            self.rumor = self.next_rumor
        else:
            if not self.rumor and self.next_rumor:
                self.rumor = self.next_rumor
                self.counter = 1
            elif self.rumor:
                greater_or_eq = sum([v >= self.counter for v in self.next_counters])
                lower = len(self.next_counters) - greater_or_eq
                switch_C = any([v >= self.t_max for v in self.next_counters])
                if self.counter < self.t_max and greater_or_eq > lower: 
                    self.counter += 1
                if switch_C:
                    self.counter = self.t_max
                self.next_counters = []
        return self.rumor

    def initialize_rumor(self):
        self.rumor = True
        self.next_rumor = True

def randomly_initialize(n):
    return random.randint(0, n - 1)

def randomly_assign(n):
    return [random.randint(0, n - 1) for _ in range(n)]

def assign_and_step(state, assignments, scheme):
    spread = 0
    transmissions = 0
    for i in range(len(state)):
        node = state[i]
        neighbor = assignments[i]
        node.set_neighbor(state[neighbor])
    for i in range(len(state)):
        node = state[i]
        if scheme == 'pull':
            transmissions += node.pull()
        elif scheme == 'push':
            transmissions += node.push()
        else:
            transmissions += node.push_and_pull()
    for i in range(len(state)):
        node = state[i]
        spread += node.update_state()
    return spread, transmissions

def print_mappings(mappings):
    for scheme in mappings: 
        print(''.join(['1' if node.rumor else '0' for node in mappings[scheme]["state"]]), scheme, mappings[scheme]['finished'])

def initialize_state(n):
    return {"state": [Node() for _ in range(n)], "record":[], "transmissions":[], "finished": 0}

def plot_graphs_rounds(n, mapping, name, average=False):
    legend_handles = []
    for scheme in mapping: 
        if type(mapping[scheme]) == list:
            runs = len(mapping[scheme])
            if average:
                counter = Counter()
                for entry in mapping[scheme]:
                    record = entry['record']
                    counter += Counter(record)
                curr = 0
                averaged_record = []
                for i in range(n):
                    if i in counter:
                        curr += counter[i]
                    averaged_record.append(curr / runs)
                plt.plot(range(1, n + 1), averaged_record, color=colors[scheme])

            else:
                for entry in mapping[scheme]:
                    x = entry['record']
                    y = range(1, len(x) + 1)
                    plt.plot(x, y, color=colors[scheme])

        else:
            x = mapping[scheme]['record']
            y = range(1, len(x) + 1)
            plt.plot(x, y, color=colors[scheme])
        legend_handles.append(mpatches.Patch(color=colors[scheme], label=scheme))
    plt.legend(handles=legend_handles)
    plt.xlabel('# of knowledgeable nodes')
    plt.ylabel('round')
    plt.title(name.replace('_', ' '))
    plt.savefig('graphs/{}.png'.format(name))
    plt.close()

def plot_graphs_transmissions(n, mapping, name, average=False):
    legend_handles = []
    for scheme in mapping: 
        if type(mapping[scheme]) == list:
            runs = len(mapping[scheme])
            if average:
                counter = Counter()
                for entry in mapping[scheme]:
                    record = entry['transmissions']
                    counter += Counter(record)
                curr = 0
                averaged_record = []

                for i in range(max(counter)):
                    if i in counter:
                        curr += counter[i]
                    averaged_record.append(curr / runs)
                plt.plot(averaged_record, range(1, len(averaged_record) + 1), color=colors[scheme])

            else:
                for entry in mapping[scheme]:
                    y = entry['transmissions']
                    x = range(1, len(y) + 1)
                    plt.plot(x, y, color=colors[scheme])

        else:
            x = mapping[scheme]['transmissions']
            y = range(1, len(x) + 1)
            plt.plot(x, y, color=colors[scheme])
        legend_handles.append(mpatches.Patch(color=colors[scheme], label=scheme))
    plt.legend(handles=legend_handles)
    plt.xlabel('rounds')
    plt.ylabel('transmissions')
    plt.title(name.replace('_', ' '))
    plt.savefig('graphs/{}.png'.format(name))
    plt.close()


def plot_histograms_rounds(mapping, name):
    legend_handles = []
    histograms = {}
    for scheme in mapping: 
        assert(type(mapping[scheme]) == list)
        runs = len(mapping[scheme])
        h = []
        for i in range(runs):
            entry = mapping[scheme][i]
            rounds = entry['finished']
            h.append(rounds)
        histograms[scheme] = h
    bins = np.histogram(np.hstack([histograms[scheme] for scheme in histograms]), bins=20)[1]
    for scheme in histograms:
        plt.hist(histograms[scheme], bins, color=colors[scheme])
        legend_handles.append(mpatches.Patch(color=colors[scheme], label=scheme))
    plt.legend(handles=legend_handles)
    plt.xlabel('rounds')
    plt.ylabel('frequency')
    plt.title(name.replace('_', ' '))
    plt.savefig('graphs/{}.png'.format(name))
    plt.close()

def plot_histograms_transmissions(mapping, name):
    legend_handles = []
    histograms = {}
    for scheme in mapping: 
        assert(type(mapping[scheme]) == list)
        runs = len(mapping[scheme])
        h = []
        for i in range(runs):
            entry = mapping[scheme][i]
            rounds = entry['transmissions'][-1]
            h.append(rounds)
        histograms[scheme] = h
    bins = np.histogram(np.hstack([histograms[scheme] for scheme in histograms]), bins=20)[1]
    for scheme in histograms:
        plt.hist(histograms[scheme], bins, color=colors[scheme])
        legend_handles.append(mpatches.Patch(color=colors[scheme], label=scheme))
    plt.legend(handles=legend_handles)
    plt.xlabel('transmissions')
    plt.ylabel('frequency')
    plt.title(name.replace('_', ' '))
    plt.savefig('graphs/{}.png'.format(name))
    plt.close()

def run_singles(n):
    mappings = {}
    mappings['pull'] = initialize_state(n)
    mappings['push'] = initialize_state(n)
    mappings['push&pull'] = initialize_state(n)
    spreader = randomly_initialize(n)
    if DEBUG: print('initially')
    for scheme in mappings:
        mappings[scheme]["state"][spreader].initialize_rumor()
    if DEBUG: print_mappings(mappings)
    round_num = 0
    while any([not mappings[scheme]["finished"] for scheme in mappings]):
        if DEBUG: print()
        assignments = randomly_assign(n)
        if DEBUG: print(assignments)
        for scheme in mappings:
            if not mappings[scheme]['finished']:
                v = assign_and_step(mappings[scheme]['state'], assignments, scheme)
                mappings[scheme]["record"].append(v)
                if v == n: 
                    mappings[scheme]['finished'] = round_num
        round_num += 1
        if DEBUG: print_mappings(mappings)

    plot_graphs_rounds(n, mappings, 'single_run', average=False)



def average_runs(n, runs=100):
    mappings = {}
    mappings['pull'] = [initialize_state(n) for _ in range(runs)]
    mappings['push'] = [initialize_state(n) for _ in range(runs)]
    mappings['push&pull'] = [initialize_state(n) for _ in range(runs)]
    for i in range(runs):
        spreader = randomly_initialize(n)
        for scheme in mappings:
            mappings[scheme][i]["state"][spreader].initialize_rumor()
        round_num = 0
        while any([not mappings[scheme][i]["finished"] for scheme in mappings]):
            assignments = randomly_assign(n)
            for scheme in mappings:
                if not mappings[scheme][i]['finished']:
                    v, transmissions = assign_and_step(mappings[scheme][i]['state'], assignments, scheme)
                    mappings[scheme][i]["record"].append(v)
                    mappings[scheme][i]["transmissions"].append(transmissions + mappings[scheme][i]["transmissions"][-1] if mappings[scheme][i]["transmissions"] else transmissions)
                    if v == n: 
                        mappings[scheme][i]['finished'] = round_num
            round_num += 1

    plot_graphs_rounds(n, mappings, 'nodes_vs_averaged_rounds_n={}_runs={}'.format(n, runs), average=True)
    plot_graphs_rounds(n, mappings, 'nodes_vs_rounds_n={}_runs={}'.format(n, runs), average=False)
    plot_graphs_transmissions(n, mappings, 'nodes_vs_averaged_transmissions_n={}_runs={}'.format(n, runs), average=True)
    plot_graphs_transmissions(n, mappings, 'nodes_vs_transmissions_n={}_runs={}'.format(n, runs), average=False)
    plot_histograms_rounds(mappings, 'rounds_vs_frequency_n={}_runs={}'.format(n, runs))
    plot_histograms_transmissions(mappings, 'transmissions_vs_frequency_n={}_runs={}'.format(n, runs))


def main():
    n = 10000
    # run_singles(n)
    average_runs(n, runs=200)

if __name__ == '__main__':
    main()

