import re


class JackTokenizer:
    KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
                'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
    SYMBOLS = set('{}()[].,;+-*/&|<>=~')

    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            self.text = f.read()

        self._remove_comments()
        self._tokenize()
        self.current_token_index = -1

    def _remove_comments(self):
        self.text = re.sub(r'//.*', '', self.text)
        self.text = re.sub(r'/\*.*?\*/', '', self.text, flags=re.DOTALL)

    def _tokenize(self):
        token_pattern = re.compile(r'("[^"\n]*"|[{}()\[\].,;+\-*/&|<>=~]|\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b)')
        self.tokens = token_pattern.findall(self.text)

    def hasMoreTokens(self):
        return self.current_token_index + 1 < len(self.tokens)

    def advance(self):
        self.current_token_index += 1

    def getToken(self):
        return self.tokens[self.current_token_index]

    def peekNextToken(self):
        if self.current_token_index + 1 < len(self.tokens):
            return self.tokens[self.current_token_index + 1]
        return None

    def tokenType(self):
        token = self.getToken()
        if token in self.KEYWORDS: return "KEYWORD"
        if token in self.SYMBOLS: return "SYMBOL"
        if token.startswith('"'): return "STRING_CONST"
        if token.isdigit(): return "INT_CONST"
        return "IDENTIFIER"

    def keyword(self):
        return self.getToken()

    def symbol(self):
        return self.getToken()

    def identifier(self):
        return self.getToken()

    def intVal(self):
        return int(self.getToken())

    def stringVal(self):
        return self.getToken()[1:-1]