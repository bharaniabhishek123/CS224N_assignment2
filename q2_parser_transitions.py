class PartialParse(object):
    def __init__(self, sentence):
        """Initializes this partial parse.

        Your code should initialize the following fields:
            self.stack: The current stack represented as a list with the top of the stack as the
                        last element of the list.
            self.buffer: The current buffer represented as a list with the first item on the
                         buffer as the first item of the list
            self.dependencies: The list of dependencies produced so far. Represented as a list of
                    tuples where each tuple is of the form (head, dependent).
                    Order for this list doesn't matter.

        The root token should be represented with the string "ROOT"

        Args:
            sentence: The sentence to be parsed as a list of words.
                      Your code should not modify the sentence.
        """
        # The sentence being parsed is kept for bookkeeping purposes. Do not use it in your code.
        self.sentence = sentence

        ### YOUR CODE HERE
        if len(sentence)==0:
            self.stack = ["ROOT"]
            self.buffer = list()
            self.dependencies = list(tuple())
        else:
            self.stack = ["ROOT"]
            self.buffer = sentence[:]
            self.dependencies = list(tuple())
            # self.dependencies.append((self.stack,self.buffer))
        ### END YOUR CODE

    def parse_step(self, transition):
        """Performs a single parse step by applying the given transition to this partial parse

        Args:
            transition: A string that equals "S", "LA", or "RA" representing the shift, left-arc,
                        and right-arc transitions. You can assume the provided transition is a legal
                        transition.
        """
        ### YOUR CODE HERE
        # print "inside parse_step"
        # print "transition passed : {:} ".format(transition)
        # print "sentence passed: {:} ".format(self.sentence)
        # print "buffer passed: {:} ".format(self.buffer)
        # print "stack passed: {:} ".format(self.stack)
        # print "dependencies passed: {:} ".format(self.dependencies)
        if transition=='S':

            temp = self.buffer.pop(0)
            self.stack.append(temp)

        elif transition=='LA':
            last2 = self.stack.pop(-2)
            last = self.stack[-1]
            self.dependencies.append((last,last2))
        else:
            if len(self.buffer)==0 and len(self.stack)==2:
                # print "IF"
                last = self.stack.pop(-1)
                self.dependencies.append(("ROOT",last))
                # print tuple(sorted(self.dependencies))
                # print tuple(self.sentence)

            else:
                # print "ELSE"
                last2 = self.stack[-2]
                last = self.stack.pop(-1)
                self.dependencies.append((last2,last))

        ### END YOUR CODE

    def parse(self, transitions):
        """Applies the provided transitions to this PartialParse

        Args:
            transitions: The list of transitions in the order they should be applied
        Returns:
            dependencies: The list of dependencies produced when parsing the sentence. Represented
                          as a list of tuples where each tuple is of the form (head, dependent)
        """
        for transition in transitions:

            self.parse_step(transition)
        return self.dependencies


def minibatch_parse(sentences, model, batch_size):
    """Parses a list of sentences in minibatches using a model.

    Args:
        sentences: A list of sentences to be parsed (each sentence is a list of words)
        model: The model that makes parsing decisions. It is assumed to have a function
               model.predict(partial_parses) that takes in a list of PartialParses as input and
               returns a list of transitions predicted for each parse. That is, after calling
                   transitions = model.predict(partial_parses)
               transitions[i] will be the next transition to apply to partial_parses[i].
        batch_size: The number of PartialParses to include in each minibatch
    Returns:
        dependencies: A list where each element is the dependencies list for a parsed sentence.
                      Ordering should be the same as in sentences (i.e., dependencies[i] should
                      contain the parse for sentences[i]).
    """

    ### YOUR CODE HERE
    # print "Inside minbatch_parse"
    partial_parses = []

    #initialize partial_parses as a list of PartialParses for all setences

    for sentence in sentences:
            parse = PartialParse(sentence)
            partial_parses.append(parse)
    unfinished_parses = partial_parses[:]

    # temp= model.predict(partial_parses)
    # print  temp

    # transitions1 = model.predict(partial_parses) # first set of predictions are S S S S
    # print "minibatch_parse the predictions are {:}",format(transitions1)

    dep = [p.dependencies for p in partial_parses]
    # print "Dependencies before while loop",format(dep)
    # cnt = 0
    while len(unfinished_parses) >0:
            mb = unfinished_parses[0:batch_size]
            # print len(mb)
            trans= model.predict(mb)

            for parse,transitions in zip(mb,trans):
                # cnt+=1
                # print "Counter {:}",format(cnt)
                # print "Transitions{:}",format(transitions)
                # print "Sentence {:}".format(parse.sentence)
                # print "Buffer before parse_Step{:}".format(parse.buffer)
                # print "Stack before parse_Step{:}".format(parse.stack)
                parse.parse_step(transitions)
                # print "Buffer after parse_Step{:}".format(parse.buffer)
                # print "Stack  after parse_Step{:}".format(parse.stack)
                # print "parse.dependencies: {:}",format(parse.dependencies)
                if len(parse.buffer) ==0 and len(parse.stack)==1:
                    unfinished_parses.remove(parse)

    dep1 = [p.dependencies for p in partial_parses]

    # print dep1
    dependencies =dep1[:]
    ### END YOUR CODE

    return dependencies


def test_step(name, transition, stack, buf, deps,
              ex_stack, ex_buf, ex_deps):
    """Tests that a single parse step returns the expected output"""
    # print "inside test_step"
    pp = PartialParse([])
    # print "call after PartialParse([])"
    pp.stack, pp.buffer, pp.dependencies = stack, buf, deps

    pp.parse_step(transition)
    stack, buf, deps = (tuple(pp.stack), tuple(pp.buffer), tuple(sorted(pp.dependencies)))
    assert stack == ex_stack, \
        "{:} test resulted in stack {:}, expected {:}".format(name, stack, ex_stack)
    assert buf == ex_buf, \
        "{:} test resulted in buffer {:}, expected {:}".format(name, buf, ex_buf)
    assert deps == ex_deps, \
        "{:} test resulted in dependency list {:}, expected {:}".format(name, deps, ex_deps)
    print "{:} test passed!".format(name)


def test_parse_step():
    """Simple tests for the PartialParse.parse_step function
    Warning: these are not exhaustive
    """
    # print "inside test_parse_step"

    test_step("SHIFT", "S", ["ROOT", "the"], ["cat", "sat"], [],
              ("ROOT", "the", "cat"), ("sat",), ())
    test_step("LEFT-ARC", "LA", ["ROOT", "the", "cat"], ["sat"], [],
              ("ROOT", "cat",), ("sat",), (("cat", "the"),))
    test_step("RIGHT-ARC", "RA", ["ROOT", "run", "fast"], [], [],
              ("ROOT", "run",), (), (("run", "fast"),))


def test_parse():
    """Simple tests for the PartialParse.parse function
    Warning: these are not exhaustive
    """
    sentence = ["parse", "this", "sentence"]
    # print "Before call to PartialParse(sentence).parse"
    dependencies = PartialParse(sentence).parse(["S", "S", "S", "LA", "RA", "RA"])
    # print "After call to PartialParse(sentence).parse"

    dependencies = tuple(sorted(dependencies))
    expected = (('ROOT', 'parse'), ('parse', 'sentence'), ('sentence', 'this'))
    assert dependencies == expected,  \
        "parse test resulted in dependencies {:}, expected {:}".format(dependencies, expected)
    assert tuple(sentence) == ("parse", "this", "sentence"), \
        "parse test failed: the input sentence should not be modified"
    print "parse test passed!"


class DummyModel(object):
    """Dummy model for testing the minibatch_parse function
    First shifts everything onto the stack and then does exclusively right arcs if the first word of
    the sentence is "right", "left" if otherwise.
    """
    def predict(self, partial_parses):
        return [("RA" if pp.stack[1] is "right" else "LA") if len(pp.buffer) == 0 else "S"
                for pp in partial_parses]


class DummyModel1(object):
    def predict1(self,pp):
        result = []
        for pp_1 in pp:
            print "predict1 sentence {:}",format(pp_1.sentence)
            print "predict1 buffer {:}",format(pp_1.buffer)
            print "predict1 stack {:}",format(pp_1.stack)
            if len(pp_1.buffer)<>0:
                result.append("S")
            elif pp_1.stack[1] is "right":
                result.append("RA")
            else:
                result.append("LA")
        return result


def test_minibatch_parse1():

    instance_dummy = DummyModel1()
    sentences = [["right", "arcs", "only"],
                 ["right", "arcs", "only", "again"],
                 ["left", "arcs", "only"],
                 ["left", "arcs", "only", "again"]]
    partial_parses1=[]
    for sentence in sentences:
            parse = PartialParse(sentence)
            print "PartialParse sentence {:}",format(parse.sentence)
            print "PartialParse stack {:}",format(parse.stack)
            print "PartialParse buffer {:}", format(parse.buffer)

            partial_parses1.append(parse)



    transitions1 = instance_dummy.predict1(partial_parses1)
    print transitions1

def test_dependencies(name, deps, ex_deps):
    """Tests the provided dependencies match the expected dependencies"""
    deps = tuple(sorted(deps))
    assert deps == ex_deps, \
        "{:} test resulted in dependency list {:}, expected {:}".format(name, deps, ex_deps)


def test_minibatch_parse():
    """Simple tests for the minibatch_parse function
    Warning: these are not exhaustive
    """
    sentences = [["right", "arcs", "only"],
                 ["right", "arcs", "only", "again"],
                 ["left", "arcs", "only"],
                 ["left", "arcs", "only", "again"]]
    deps = minibatch_parse(sentences, DummyModel(), 2)
    test_dependencies("minibatch_parse", deps[0],
                      (('ROOT', 'right'), ('arcs', 'only'), ('right', 'arcs')))
    test_dependencies("minibatch_parse", deps[1],
                      (('ROOT', 'right'), ('arcs', 'only'), ('only', 'again'), ('right', 'arcs')))
    test_dependencies("minibatch_parse", deps[2],
                      (('only', 'ROOT'), ('only', 'arcs'), ('only', 'left')))
    test_dependencies("minibatch_parse", deps[3],
                      (('again', 'ROOT'), ('again', 'arcs'), ('again', 'left'), ('again', 'only')))
    print "minibatch_parse test passed!"

if __name__ == '__main__':
    # test_parse_step()
    # test_parse()
    test_minibatch_parse()
    # test_minibatch_parse1()
