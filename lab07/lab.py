import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.
class BadDictionaryError(Exception):
    pass

def check_zero(n):
    return (type(n) == Num and n.n == 0) or n == 0

def check_one(n):
    return type(n) == Num and n.n == 1

class Symbol:
    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)


class Var(Symbol):
    precedence = 34
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"

    def deriv(self, wrt):
        return Num(1) if self.name == wrt else Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        try:
            return mapping[self.name]
        except KeyError as e:
            raise BadDictionaryError(e)

class Num(Symbol):
    precedence = 34
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"

    def deriv(self, wrt):
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return self.n

class BinOp(Symbol):

    left_paren_need = False
    right_paren_need = False

    def __init__(self, left, right):
        if isinstance(left, int):
            self.left = Num(left)
        if isinstance(left, str):
            self.left = Var(left)
        if isinstance(left, Symbol):
            self.left = left

        if isinstance(right, int):
            self.right = Num(right)
        if isinstance(right, str):
            self.right = Var(right)
        if isinstance(right, Symbol):
            self.right = right

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.left) + ", " + repr(self.right) + ")"

    def __str__(self):
        l, r = str(self.left), str(self.right)
        if self.left.precedence < self.precedence or (self.left.precedence == self.precedence and self.left_paren_need):
            l = "(" + str(self.left) + ")"
        if self.right.precedence < self.precedence or (self.right.precedence == self.precedence and self.right_paren_need):
            r = "(" + str(self.right) + ")"
        return l + " " + self.op_symbol + " " + r
    
class Add(BinOp):
    op_symbol = "+"
    precedence = 0
    
    def deriv(self, wrt):
        return self.left.deriv(wrt) + self.right.deriv(wrt) #can use + since __add__ is defined in Symbol class

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if (type(l), type(r)) == (Num, Num):
            return Num(l.n + r.n)
        elif check_zero(l):
            return r
        elif check_zero(r):
            return l
        else:
            return l + r
    
    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)

class Sub(BinOp):
    op_symbol = "-"
    precedence = 0
    right_paren_need = True

    def deriv(self, wrt):
        return self.left.deriv(wrt) - self.right.deriv(wrt) #can use - since __sub__ is defined in Symbol class

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if (type(l), type(r)) == (Num, Num):
            return Num(l.n - r.n)
        elif check_zero(r):
            return l
        else:
            return l - r

    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)
class Mul(BinOp):
    op_symbol = "*"
    precedence = 1

    def deriv(self, wrt):
        return self.left * self.right.deriv(wrt) + self.right * self.left.deriv(wrt)

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if (type(l), type(r)) == (Num, Num):
            return Num(l.n * r.n)
        elif check_zero(l) or check_zero(r):
            return Num(0)
        elif check_one(l):
            return r
        elif check_one(r):
            return l
        else:
            return l * r

    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)

class Div(BinOp):
    op_symbol = "/"
    precedence = 1
    right_paren_need = True

    def deriv(self, wrt):
        return (self.right * self.left.deriv(wrt) - self.left * self.right.deriv(wrt)) / (self.right * self.right)
    
    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if (type(l), type(r)) == (Num, Num):
            return Num(l.n / r.n)
        elif check_zero(l):
            return Num(0)
        elif check_one(r):
            return l
        else:
            return l / r
    
    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)
print(check_zero(0))
class Pow(BinOp):
    op_symbol = "**"
    precedence = 2
    left_paren_need = True

    def deriv(self, wrt):
        if type(self.right) != Num:
            raise TypeError
        return self.right * (self.left ** (self.right - 1)) * self.left.deriv(wrt)

    def simplify(self):
        print(self)
        l = self.left.simplify()
        r = self.right.simplify()
        if (type(l), type(r)) == (Num, Num):
            return Num(l.n ** r.n)
        elif check_zero(r) or check_one(l):
            return Num(1)
        elif check_zero(l):
            return Num(0)
        elif check_one(r):
            return l
        else:
            return l ** r

    def eval(self, mapping):
        return self.left.eval(mapping) ** self.right.eval(mapping)

def tokenize(expression):
    out = expression.replace(")", " ) ")
    out = out.replace("(", " ( ")
    return out.split()

op_dict = {
    "+": Add,
    "-": Sub,
    "*": Mul,
    "/": Div,
    "**": Pow,
}

def parse(tokens):
    def parse_expression(i):
        token = tokens[i]

        if token.isdigit() or (token[1:].isdigit() and token[0] == "-"):
            return Num(int(token)), i+1
        elif token != "(":
            return Var(token), i+1
        else:
            E1, i = parse_expression(i+1)
            op = tokens[i]
            E2, i = parse_expression(i+1)
            return op_dict[op](E1, E2), i+1
       
    parsed_expression, _ = parse_expression(0)
    return parsed_expression

def expression(expression):
    return parse(tokenize(expression))
    
if __name__ == "__main__":
    doctest.testmod()
    test1 = Var('x') * Var('y') + Var('z') ** Num(2)
    print(test1.eval({'x': 2, 'y':3, 'z':4}))
    print(test1)
    print(repr(test1))

    test2 = 5 * (Var('a') - Var('b')) + Var('c') ** Var('d')
    print(test2.eval({'a':1, 'b': 3, 'c': 4, 'd':2}))
    print(test2)
    print(repr(test2))
    
    #test3 = Var('m') - Var('n')
    #test3.eval({'m': 3})
    
    """a = Var('x')
    b = Add('x', 'x')
    print(type(a))
    print(type(b))
    print(type(b) == BinOp)
    print(isinstance(b, BinOp))"""