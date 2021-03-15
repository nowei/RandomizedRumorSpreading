#!/usr/bin/python
import matplotlib.pyplot as plt 
import random
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

    def push(self):
        if self.rumor: 
            self.neighbor.next_rumor = self.rumor 

    def push_and_pull(self):
        if self.rumor:
            self.neighbor.next_rumor = self.rumor
        elif self.neighbor.rumor:
            self.next_rumor = self.neighbor.rumor

        if self.rumor and self.neighbor.rumor:
            self.next_counters.append(self.counter)
            self.neighbor.next_counters.append(self.counter)

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
    for i in range(len(state)):
        node = state[i]
        neighbor = assignments[i]
        node.set_neighbor(state[neighbor])
    for i in range(len(state)):
        node = state[i]
        if scheme == 'pull':
            node.pull()
        elif scheme == 'push':
            node.push()
        else:
            node.push_and_pull()
    for i in range(len(state)):
        node = state[i]
        spread += node.update_state()
    return spread

def print_mappings(mappings):
    for scheme in mappings: 
        print(''.join(['1' if node.rumor else '0' for node in mappings[scheme]["state"]]), scheme, mappings[scheme]['finished'])

def initialize_state(n):
    return {"state": [Node() for _ in range(n)], "record":[], "finished": 0}

def plot_graphs(mapping, name, average=False):
    legend_handles = []
    for scheme in mapping: 
        if type(mapping[scheme]) == list:
            pass
            # if average:

            # else:
            #     for state, record, finished in mapping[scheme]:
            #         plt.plot(x, y, color=color1)
        else:
            x = mapping[scheme]['record']
            y = range(1, len(x) + 1)
            plt.plot(x, y, color=colors[scheme])
        legend_handles.append(mpatches.Patch(color=colors[scheme], label=scheme))
    plt.legend(handles=legend_handles)
    plt.xlabel('# of knowledgeable nodes')
    plt.ylabel('round')
    plt.savefig('graphs/{}.png'.format(name))
    plt.close()

def plot_histograms(mapping):
    pass

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

    plot_graphs(mappings, 'single_run', average=False)


def average_runs(n, runs=100):
    pass

def main():
    n = 1000
    run_singles(n)

if __name__ == '__main__':
    main()

