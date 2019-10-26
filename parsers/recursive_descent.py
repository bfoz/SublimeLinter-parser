import re

from collections import namedtuple

from ..grammar import Alternation, Concatenation, Repetition

Node = namedtuple('Node', ('rule', 'items'))

class RecursiveDescent:
    """ A Recursive Descent parser that uses a set of named-rules as its grammar """

    def __init__(self, named_rules, root_rule=None):
        try:
            self.root_rule = named_rules.root()
            self.grammar = named_rules
            self.named_rules = {}
        except AttributeError:
            if isinstance(named_rules, Alternation) or isinstance(named_rules, Concatenation) or isinstance(named_rules, Repetition):
                self.root_rule = named_rules
                self.named_rules = {}
            else:
                self.named_rules = named_rules
                self.root_rule = self.named_rules[root_rule]

    def parse(self, input):
        # Get the root rule
        self.index = 0
        return self._visit(self.root_rule, input)

    def _is_eof(self, input):
        if self.index >= len(input):
            return True

    def _visit(self, rule, input):
        if isinstance(rule, str):
            if input.startswith(rule, self.index):
                self.index += len(rule)
                return Node(rule, rule)

        elif hasattr(rule, "match"):
            match = rule.match(input, self.index)
            if match:
                self.index += len(match.group(0))
                return Node(rule, match.group(0))

        elif isinstance(rule, Alternation):
            index = self.index
            nodes = []
            for element in rule.elements:
                self.index = index
                node = self._visit(element, input)
                if node is not None:
                    if rule.ordered:
                        return Node(rule, node)
                    length = self.index - index
                    nodes.append([length, Node(rule, node)])

            if len(nodes) > 0:
                _longest = max(nodes, key=lambda x: x[0])
                self.index = index + _longest[0]
                return _longest[1]

        elif isinstance(rule, Concatenation):
            nodes = []
            for element in rule.elements:
                index = self.index
                node = self._visit(element, input)
                if node is None:
                    return None
                else:
                    nodes.append(node)
                    if rule.separator and (element is not rule.elements[-1]):
                        index = self.index
                        node = self._visit(rule.separator, input)
                        if not node:
                            self.index = index

            return Node(rule, nodes)

        elif isinstance(rule, Repetition):
            result = []
            if rule.minimum and (rule.minimum != 0):
                for i in range(0, rule.minimum):
                    position = self.index
                    a = self._visit(rule.element, input)
                    if a:
                        result.append(a)
                    else:
                        self.index = position   # Backtrack
                        break                   # Failure

            if rule.maximum:
                for i in range(0, (rule.maximum - (rule.minimum or 0))):
                    position = self.index
                    a = self._visit(rule.element, input)
                    if a:
                        result.append(a)
                    else:
                        self.index = position   # Backtrack
                        break                   # Failure
            else:
                # No max limit, so go until failure or EOS
                while True:
                    position = self.index
                    a = self._visit(rule.element, input)
                    if a:
                        result.append(a)
                    else:
                        self.index = position   # Backtrack
                        break                   # Failure
                    if self._is_eof(input):
                        break

            if rule.is_optional():
                return result[0] if len(result) == 1 else []
            else:
                return result

        else:
            raise TypeError("Unrecognized rule type: {} != {}".format(type(rule), Repetition))
