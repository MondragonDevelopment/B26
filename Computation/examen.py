from itertools import combinations
import graphviz
from pprint import pprint
import math


class Automaton:
    def __init__(self, Q, sigma, delta, q0, F):
        # Q: List of tuples-states in the automaton
        # sigma: The alphabet accepted by the automaton
        # delta: List of lists, transitions table
        # q0: string with the name of the initial state
        # F: list (of sets) of final states

        self.Q = list(Q)
        self.sigma = list(sigma)
        self.delta = delta
        self.q0 = q0
        self.F = set(F)

    def draw(self, filename):
        """
        Generates and renders a state diagram of the NFA using Graphviz.
        Saves the file as 'filename.png' (or pdf/svg depending on preference).
        """
        # Create a directed graph with left-to-right orientation
        dot = graphviz.Digraph(comment='NFA State Diagram', graph_attr={'rankdir': 'LR'})
        
        # 1. Add an invisible starting point and an arrow pointing to the initial state
        dot.node('start', label='', shape='point', width='0')
        initial_label = str(self.q0)
        dot.edge('start', initial_label)
        
        # 2. Add all states, marking final states with a double circle
        for state in self.Q:
            state_label = str(state)
            if state in self.F:
                dot.node(state_label, shape='doublecircle')
            else:
                dot.node(state_label, shape='circle')
                
        # 3. Parse and add transitions from the delta table
        # We look up indices from self.Q to map row/column coordinates to real states/symbols
        for row_idx, row in enumerate(self.delta):
            from_state = self.Q[row_idx]
            
            for col_idx, destinations in enumerate(row):
                symbol = self.sigma[col_idx]
                
                # Format empty string or 'eps' as the standard Epsilon symbol (e)
                label_symbol = "e" if symbol in ("", "eps", "epsilon") else str(symbol)
                
                # Destinations in an NFA are collections/lists of states
                if destinations:
                    if type(destinations) is tuple:
                        dot.edge(str(from_state), str(destinations), label=label_symbol)
                        continue
                    for to_state in destinations:
                        dot.edge(str(from_state), str(to_state), label=label_symbol)
                        
        # Render the diagram to a file and open it
        dot.render(filename, format='png', cleanup=True)
        print(f"State diagram successfully saved to '{filename}.png'!")


class NFAFragment:
    """Helper class to hold temporary NFA pieces during construction."""
    def __init__(self, start, accept, states, transitions):
        self.start = start          # Start state of this fragment
        self.accept = accept        # Accept state of this fragment
        self.states = states        # Set of all states in this fragment
        self.transitions = transitions  # Dict: (state, symbol) -> set of target states


def toNFA(regex):
    pos = 0
    st_counter = 0

    def new_state():
        """Generates a unique state name."""
        nonlocal st_counter
        state = f"q{st_counter}"
        st_counter += 1
        return state

    def peek():
        return regex[pos] if pos < len(regex) else None

    def consume():
        nonlocal pos
        char = peek()
        pos += 1
        return char

    # --- Thompson Construction Rules ---

    def make_base(symbol):
        """Base case: a single literal character."""
        s0 = new_state()
        s1 = new_state()
        transitions = {(s0, symbol): {s1}}
        return NFAFragment(s0, s1, {s0, s1}, transitions)

    def make_empty_set():
        """Base case: the empty set (@), matches nothing (zero transitions)."""
        s0 = new_state()
        s1 = new_state()
        return NFAFragment(s0, s1, {s0, s1}, {})

    def make_concat(left, right):
        """Inductive case: Concatenation (left followed by right)."""
        states = left.states | right.states
        transitions = {**left.transitions, **right.transitions}
        
        epsilon_key = (left.accept, None)
        if epsilon_key in transitions:
            transitions[epsilon_key].add(right.start)
        else:
            transitions[epsilon_key] = {right.start}
            
        return NFAFragment(left.start, right.accept, states, transitions)

    def make_alternation(left, right):
        """Inductive case: Alternation (left | right)."""
        s0 = new_state()
        s_accept = new_state()
        states = left.states | right.states | {s0, s_accept}
        
        transitions = {**left.transitions, **right.transitions}
        transitions[(s0, None)] = {left.start, right.start}
        
        left_acc_key = (left.accept, None)
        right_acc_key = (right.accept, None)
        
        transitions[left_acc_key] = transitions.get(left_acc_key, set()) | {s_accept}
        transitions[right_acc_key] = transitions.get(right_acc_key, set()) | {s_accept}
        
        return NFAFragment(s0, s_accept, states, transitions)

    def make_star(frag):
        """Inductive case: Kleene Star (zero or more)."""
        s0 = new_state()
        s_accept = new_state()
        states = frag.states | {s0, s_accept}
        
        transitions = dict(frag.transitions)
        transitions[(s0, None)] = {frag.start, s_accept}
        
        frag_acc_key = (frag.accept, None)
        transitions[frag_acc_key] = transitions.get(frag_acc_key, set()) | {frag.start, s_accept}
        
        return NFAFragment(s0, s_accept, states, transitions)

    def make_plus(frag):
        """Inductive case: Plus operator (one or more)."""
        s0 = new_state()
        s_accept = new_state()
        states = frag.states | {s0, s_accept}
        
        transitions = dict(frag.transitions)
        transitions[(s0, None)] = {frag.start}
        
        frag_acc_key = (frag.accept, None)
        transitions[frag_acc_key] = transitions.get(frag_acc_key, set()) | {frag.start, s_accept}
        
        return NFAFragment(s0, s_accept, states, transitions)

    # --- Recursive Descent Parser Methods ---

    def parse_atom():
        char = peek()
        if char == "(":
            consume()  # eat '('
            nfa = parse()
            consume()  # eat ')'
            return nfa
        elif char == "@":
            consume()
            return make_empty_set()
        elif char and char not in "|*+()":
            consume()
            return make_base(char)
        raise ValueError(f"Unexpected character: {char}")

    def parse_repeat():
        nfa = parse_atom()
        while peek() in ("*", "+"):
            op = consume()
            if op == "*":
                nfa = make_star(nfa)
            elif op == "+":
                nfa = make_plus(nfa)
        return nfa

    def parse_concat():
        nfas = [parse_repeat()]
        while peek() and peek() not in "|)":
            nfas.append(parse_repeat())
        
        result = nfas[0]
        for next_nfa in nfas[1:]:
            result = make_concat(result, next_nfa)
        return result

    def parse():
        nfa = parse_concat()
        while peek() == "|":
            consume()  # eat '|'
            right_nfa = parse_concat()
            nfa = make_alternation(nfa, right_nfa)
        return nfa

    reserved = {"|", "*", "+", "(", ")", "@"}
    sigma = sorted(list(set(regex) - reserved))
    fragment = parse()
    Q = sorted(list(fragment.states))
    # F = set()

    # Format internal transitions into your delta table format

    delta = [[None for _ in range(len(sigma) + 1)] for _ in range(len(Q))]
    for (state, symbol), targets in fragment.transitions.items():
        sym_key = sigma.index(symbol) if symbol is not None else len(sigma)
        idx = Q.index(state)
        delta[idx][sym_key] = set(targets)
        
    q0 = fragment.start
    F = {fragment.accept}
    # print(F)

    return Automaton(Q=Q, sigma=sigma+[""], delta=delta, q0=q0, F=F)


def toDFA(NFA):
    Q, sigma, delta, q0, F = NFA.Q, NFA.sigma, NFA.delta, NFA.q0, NFA.F
    new_delta = []
    new_Q = []
    new_F = []
    new_sigma = sigma[:-1]

    def closure(q):
        queue = set()
        queue.add(q)
        state = set()
        while queue:
            # print(queue)
            curr = queue.pop()
            state.add(curr)
            trans = delta[Q.index(curr)][-1]
            if trans:
                for stt in trans:
                    if stt in state: continue
                    queue.add(stt)
        return state

    new_Q.append(tuple(closure(q0)))
    queue = [new_Q[0]]

    while queue:
        curr = queue.pop(0)
        # print(curr)
        reach = []
        for s in range(len(sigma) - 1):
            new_state = set()
            limbo = set()
            for state in curr:
                trans = delta[Q.index(state)][s]
                if trans:
                    for stt in trans:
                        limbo.add(stt)
            for stte in limbo:
                new_state = new_state.union(closure(stte))

                # I don't think so, but maybe here I need to sort the
                # new_state like this: new_state =
                # list(new_state.sort())

            if len(new_state) == 0:
                new_state = None
            else:
                new_state = tuple(new_state)
                
            reach.append(new_state)

            if new_state in new_Q or not new_state: continue

            queue.append(new_state)
            new_Q.append(new_state)
        new_delta.append(reach)

    # print(new_Q, new_F)
    
    for state in new_Q:
        for final in F:
            # print(final)
            if final in state:
                new_F.append(state)
                break

    return Automaton(new_Q, new_sigma, new_delta, new_Q[0], new_F)


def minDFA(DFA):
    non_F = [_ for _ in DFA.Q if _ not in DFA.F]
    if len(non_F) == 0:
        equiv = sorted([DFA.F])
    else:
        equiv = sorted([set(non_F), set(DFA.F)])

    equiv += [None]   # We have to take into account hthe empty set as
                      # a separate partition if it appears in thae
                      # trnasitions table
    new_Q = []
    new_delta = []
    new_F = []
    mapa = {}

    convergent = False
    
    def getPairs(iterable):
        """
        Yields combinations of the elements in the iterable one by one,
        for all lengths from 2 up to the total number of elements.
        """
        elements = list(iterable)
        n = len(elements)

        # Generate combinations for every size 'r' from 2 to n
        for combo in combinations(elements, 2):
            yield combo

    while not convergent:
        def newEquiv(equiv):
            # print("This is the equivalence partition:\n", equiv)
            new_equiv = []
            for part in equiv[:-1]:  # For each partition
                curr = part.copy()
                
                if len(curr) < 2:     # If there are no pairs...
                    new_equiv.append(part)
                    continue

                eq_states = []
                
                for pair in getPairs(part):
                    # print("Let's check if the pair ", pair, " goes to the same places.\n")
                    j = DFA.Q.index(pair[0])
                    k = DFA.Q.index(pair[1])

                    for m in range(len(DFA.sigma)):
                        j_trans, k_trans = DFA.delta[j][m], DFA.delta[k][m]
                        if j_trans == k_trans:
                            # print(f"They go the same places when receiving {DFA.sigma[m]} \n")
                            continue

                        idx = None

                        if k_trans is None or j_trans is None:
                            break

                        for n, part in enumerate(equiv[:-1]):
                            # print(k_trans, part)
                            if k_trans in part:
                                idx = n
                                break

                        # print(j_trans in equiv[idx])

                        if j_trans not in equiv[idx]:  # If j_trans not in the same partition as k_trans
                            # print(DFA.Q[j], DFA.Q[k], DFA.sigma[m])
                            break
                    else:
                        eq_states.append(pair)
                        for state in pair:
                            if state in curr:
                                curr.remove(state)
                if eq_states:
                    if len(eq_states) == math.comb(len(part), 2):
                        new_equiv.append(part)
                        continue
                    # print(eq_states)
                    start_pair = set(eq_states.pop(0))
                    curr -= start_pair
                    new_equiv.append(start_pair)
                    
                    while eq_states:
                        # print(new_equiv)
                        pair = set(eq_states.pop())
                        curr -= pair
                        for idx, par in enumerate(new_equiv):
                            if pair & par:
                                new_equiv[idx] = pair | par
                                break
                        else:
                            new_equiv.append(pair)

                # print(new_equiv)
                if curr:
                    # print("this is the rest: ", curr)
                    curr = [{_} for _ in curr]
                    # print("This is the rest fragmented:", curr)
                
                new_equiv += curr
                # print("--------\n", new_equiv, "\n--------- \n")
            return new_equiv

        new_equiv = sorted(newEquiv(equiv))
        
        # print(new_equiv, equiv, "\n\n\n")
        
        if new_equiv == equiv[:-1]:
            equiv = new_equiv
            convergent = True
        else:
            equiv = new_equiv + [None]

    conver = [_ for _ in equiv]
    # print(equiv)

    for i in range(len(conver)):  # for each partition
        partition = conver[i]
        final = False  # mark to see if the partition contains a final state
        initial = False

        if len(partition) > 1:
            # print(partition)
            new_partition = set()
            for state in partition:
                mapa[state] = i
                if state in DFA.F:
                    final = True
                if state == DFA.q0:
                    initial = True
                new_partition = new_partition.union(set(state))
            # equiv[i] = new_partition
        else:
            # print(partition)
            element = next(iter(partition))
            mapa[element] = i
            if element in DFA.F:
                final = True
            if element == DFA.q0:
                initial = True

        new_state = tuple(next(iter(partition)))
        new_Q.append(new_state)
        if final:
            new_F.append(new_state)
        if initial:
            q0 = new_state

    # print(equiv)
    for i in range(len(equiv)):
        new_trans = []
        for j in range(len(DFA.sigma)):
            dummy = next(iter(equiv[i]))
            idx = DFA.Q.index(dummy)
            trgt = DFA.delta[idx][j]
            if trgt:
                trgt_idx = mapa[trgt]
                new_trans.append(new_Q[trgt_idx])
            else:
                new_trans.append(None)
        new_delta.append(new_trans)

    return Automaton(new_Q, DFA.sigma, new_delta, q0, new_F)


if __name__ == '__main__':
    tries = 3

    print('-----WELCOME TO THE AUTOMATA MASTER-----\n')
    print("I can help you dealing with your Non-deterministic \nFinite Automaton or a Regular Expression\n")
    while tries > 0:
        print("Which one do you have?\n 1) NFA\n 2) RE\n")
        option = input("Enter an option below\n")
        if option == "1":
            Q = input("Enter the node names, separated by spaces.\n").split()
            sigma = input("Enter the alphabet accepted by your NFA. Separate each symbol with a space.\n").split()
            q0 = input(f"Enter the initial state (must be one of {Q}): \n").strip()
            F = input(f"Enter the final states separated by spaces (must belong to {Q}): \n").split()
            
            sigma.append("eps")
            delta = [[None for _ in range(len(sigma))] for _ in range(len(Q))]
            
            print("Enter the transitions. For each state and symbol, list destination states separated by spaces. Press enter if none.")
            for i in range(len(delta)):
                for j in range(len(delta[0])):
                    response = input(f"From {Q[i]} with {sigma[j]} :\n")
                    if response:
                        delta[i][j] = set(response.split())

            sigma.pop()
            sigma.append("")

            NFA = Automaton(Q, sigma, delta, q0, F)
            pprint(vars(NFA))
            # NFA.draw("NFA Diagram")

            DFA = toDFA(NFA)
            pprint(vars(DFA))
            # DFA.draw("DFA Diagram")

            DFA_min = minDFA(DFA)
            pprint(vars(DFA_min))
            # DFA_min.draw("DFA min Diagram")
            break

        elif option == "2":
            regex = input("Enter regular expression (use @ for empty set and | for union): \n")
            NFA = toNFA(regex)
            pprint(vars(NFA))
            # NFA.draw("NFA Diagram")

            DFA = toDFA(NFA)
            pprint(vars(DFA))
            # DFA.draw("DFA Diagram")

            DFA_min = minDFA(DFA)
            pprint(vars(DFA_min))
            # DFA_min.draw("DFA min Diagram")
            break
        
        else:
            tries -= 1
            print("That's not a valid option")
            if tries == 0:
                print("You have exceeded the maximum number of tries\nHave a nice one.")
