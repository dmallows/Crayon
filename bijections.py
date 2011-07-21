from math import log,exp

def log_bijection(a, b):
    m = 1.0 / a
    d = log(m * b)
    A = 1.0 / d
    C = a
    return (lambda x: A*log(m*x), lambda x: C*exp(d*x))

def lin_bijection(a, b):
    range = b - a
    m = 1.0 / range 

    return (lambda x: (x-a)*m, lambda x: range*x + a) 
