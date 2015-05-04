import re


class Language(object):

    def is_matchable(self):
        return False

    def derive(self, ch):
        raise Exception("Not Implemented. %s Trying to derive char:'%s'." %
                        (type(self), ch))

    def __add__(self, other):
        _other = other
        if other is None:  # one or more '*_' syntax
            _other = Star.make(self)

        if isinstance(other, basestring) or isinstance(other, str):
            _other = Character(other)

        return And.make(self, _other)

    def __or__(self, other):
        return Or.make(self, to_language(other))

    def __mul__(self, other):
        return Star.make(self)


class Reject(Language):
    '''A [Language] that rejects everything.
    '''
    def derive(self, ch):
        return reject

    def __repr__(self):
        return 'Reject'


class Match(Language):
    '''A [Language] that matches the defined [Language].
    '''

    def is_matchable(self):
        return True

    def derive(self, ch):
        return reject

    def __repr__(self):
        return 'Match'


reject = Reject()
match = Match()


class Character(Language):
    '''A [Language] that matches a specific character.
    '''

    def __init__(self, char):
        self.char = char

    def derive(self, ch):
        if self.char == ch:
            return match
        return reject

    def __repr__(self):
        return 'C(%s)' % self.char


class Or(Language):
    '''A [Language] that matches either of two [Language]s.
    '''

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_matchable(self):
        return self.left.is_matchable() or self.right.is_matchable()

    def derive(self, ch):
        return Or.make(self.left.derive(ch), self.right.derive(ch))

    @staticmethod
    def make(left, right):
        if (left is reject and right is reject):
            return reject
        if left is reject:
            return right
        if right is reject:
            return left
        if (left is match or right is match):
            return match
        return Or(left, right)

    def __repr__(self):
        return 'Or(%s, %s)' % (self.left, self.right)


class And(Language):
    '''A [Language] that matches two [Language]s in sequence.
    '''

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_matchable(self):
        return self.left.is_matchable() and self.right.is_matchable()

    def derive(self, ch):
        if self.left.is_matchable():
            return Or.make(And.make(self.left.derive(ch), self.right),
                           self.right.derive(ch))

        return And.make(self.left.derive(ch), self.right)

    @staticmethod
    def make(left, right):
        if left is match:
            return right

        if (left is reject) or (right is reject):
            return reject

        return And(left, right)

    def __repr__(self):
        return 'And(%s, %s)' % (self.left, self.right)


class Star(Language):
    '''A [Language] that matches the kleene star of a [Language].
    '''

    def __init__(self, language):
        self.language = language

    def is_matchable(self):
        return True

    def derive(self, ch):
        return And.make(self.language.derive(ch), Star.make(self.language))

    @staticmethod
    def make(language):
        if language in [match, reject]:
            return language
        return Star(language)

    def __repr__(self):
        return 'Star(%s)' % (self.language)


class Optional(Language):
    '''A [Language] that matches zero or one of a [Language].
    '''
    def __init__(self, language):
        self.language = language

    def is_matchable(self):
        return True

    def derive(self, ch):
        return self.language.derive(ch)

    @staticmethod
    def make(language):
        if language in [match, reject]:
            return language
        return Optional(language)

    def __repr__(self):
        return 'Optional(%s)' % (self.language)


class RegExp(Language):
    '''Helper [Language] represents a regular expression matcher.
    '''

    def __init__(self, regex):
        self._regex = regex
        self.regexp = re.compile(regex)

    def derive(self, ch):
        if self.regexp.match(ch):
            return match
        return reject

    def __repr__(self):
        return 'RE(%s)' % (self._regex)


class Not(Language):
    '''Helper [Language] represents the revese of another [Language].
    '''
    def __init__(self, language):
        self.language = language

    def derive(self, ch):
        d = self.language.derive(c)
        if d is match:
            return reject
        elif d is reject:
            return match
        return Not(d)


class NotCharacter(Character):

    def __init__(self, ch):
        super(NotCharacter, self).__init__(ch)

    def derive(self, ch):
        if ch == c:
            reject
        return match


LETTER = RegExp('[a-zA-Z]')
DIGIT = RegExp('[0-9]')
HEX = RegExp('[0-9a-fA-F]')
NEWLINE = Optional(RegExp('[\r]')) + RegExp('[\n]')
_ = None  # Used for +_ and *_


def word(string):
    '''Helper function to create string matcher.
    '''

    if not string:
        raise 'string is empty.'

    if len(string) == 1:
        return Character(string)

    return And.make(Character(string[0]), word(string[1:]))


def to_language(thing):
    '''Helper function that tries to convert thing to a Language.
    '''

    if isinstance(thing, basestring) or isinstance(thing, str):
        return word(thing)

    if isinstance(thing, Language):
        return thing

    if isinstance(thing, Rule):
        return thing.language

    raise "Couldn't convert [%s] to a Language" % thing


class Rule(object):

    def __init__(self, language=None, action=None, root_rule=None):
        self.language = language
        self.action = action
        self.root_rule = root_rule

    def derive(self, ch):
        rule = self.root_rule or self
        return Rule(self.language.derive(ch), self.action, rule)

    def is_match(self):
        return self.language is match

    def is_reject(self):
        return self.language is reject

    def is_matchable(self):
        return self.language.is_matchable()

    def emit(self, token_creator):
        def action(state, lexer):
            token = token_creator()
            token.value = state.matched_input
            token.position = lexer.position
            return lexer.emit(token, state)
        self.action = action
        return self.action

    def __div__(self, token_creator):
        '''Syntactic suguar to add an action.
        '''
        return self.emit(token_creator)

    def __rshift__(self, action):
        def _action(state, lexer):
            next_state = action(state, lexer)
            next_state.matched_input = state.matched_input
            return next_state
        self.action = _action

    def __repr__(self):
        return 'Rule(%s)' % (self.language)


class Token(object):
    def __init__(self):
        self.value = None
        self.position = None
        self.skip = False

    def __new__(cls, skip=False):
        def init(instance, skip=skip):
            instance.skip = skip

        # TODO(Sam): This will replace the orginal __init__. We probably should
        #            not do that and call this method too.
        cls.__init__ = init
        instance = super(Token, cls).__new__(cls)
        return instance

    def __repr__(self):
        return 'Token(%s:%s)' % (self.value, self.position or '0')


class State(object):

    def __init__(self, matched_input='', rules=None):
        self.matched_input = matched_input
        self.rules = rules or []

    def must_accept(self):
        if len(self.rules) == 1:
            return self.rules[0].is_match()
        return False

    def can_match_more(self):
        return [(not _.is_reject()) for _ in self.rules]

    def has_exact_match(self):
        return [_.is_match() for _ in self.rules]

    def has_matchables(self):
        return [_.is_matchable() for _ in self.rules]

    def is_reject(self):
        return all([_.is_reject() for _ in self.rules])

    def next(self, ch, context):
        derived_rules = [_.derive(ch) for _ in self.rules]
        matching_rules = [_ for _ in derived_rules if not _.is_reject()]
        return DerivedState(self.matched_input + ch, matching_rules)

    def dispatch(self, context):
        exact_match = [_ for _ in self.rules if _.is_match()]
        matchables = [_ for _ in self.rules if _.is_matchable()]

        state_like = None

        if exact_match:
            state_like = exact_match[0].action(self, context)
        elif matchables:
            state_like = matchables[0].action(self, context)
        else:
            raise Exception("Something not right here .. should have state,"
                            "or state creator function [%s], Matching: [%s]" %
                            (self.rules, self.matched_input))

        if isinstance(state_like, State):
            return state_like

        # At this point the matchedInput has been taken care of so we will
        # just reset it.
        #context.top().matched_input = ''
        return context.top()()

    def on(self, thing):
        rule = Rule(language=to_language(thing))
        self.rules.append(rule)
        return rule

    def __div__(self, thing):
        '''Syntactic sugure for defining rules.
        '''
        return self.on(thing)


class RejectState(State):

    def is_reject(self):
        return True

    def dispatch(self, context):
        raise 'Dispatching a reject state! Something is not right.'


class DerivedState(State):

    def __init__(self, matched_input, rules):
        super(DerivedState, self).__init__(matched_input, rules)


class Lexer(object):

    def __init__(self, initial_state=None, output=None):
        self.initial_state = initial_state or State
        self.output = output

        self.current_state = self.initial_state()
        self.last_matching_state = None
        self.last_dispatchable_state = None
        self.stack = [self.current_state]
        self.position = 0
        self.remaining_input = None

    def next(self, ch):
        self.current_state = self.current_state.next(ch, self)
        if self.current_state.has_exact_match():
            self.last_matching_state = self.current_state
            self.last_dispatchable_state = self.current_state
            return self.current_state

        else:
            if self.current_state.can_match_more():
                self.last_matching_state = self.current_state
                if self.current_state.has_matchables():
                    self.last_dispatchable_state = self.current_state
                return self.current_state

            if self.last_matching_state is not None:
                if self.last_matching_state.has_matchables():
                    self.remaining_input = self.get_remaining_input(
                        self.current_state, self.last_matching_state)
                    self.current_state = self.last_matching_state.dispatch(self)
                else:
                    self.remaining_input = self.get_remaining_input(
                        self.current_state, self.last_dispatchable_state)
                    self.current_state = self.last_dispatchable_state.dispatch(self)

                self.last_matching_state = None
                self.last_dispatchable_state = None

                for c in self.remaining_input:
                    self.current_state = self.next(c)

                return self.current_state

        raise Exception('No rule defined for input [%s] at position %s.' % (
            self.current_state.matched_input, self.position))

    def get_remaining_input(self, left, right):
        return re.sub('^' + re.escape(right.matched_input), '', left.matched_input)

    def emit(self, token, state):
        self.output.add(token)
        self.position += len(state.matched_input)
        state.matched_input = ''
        return self.top()

    def push(self, state):
        self.stack.append(state)
        return state

    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def done(self):
        '''Tells the lexer that we are done feeding charachters and match what
        ever is remaining.
        '''
        self.next('')

    def lex(self, input_string):
        for c in input_string:
            self.next(c)
        self.done()
