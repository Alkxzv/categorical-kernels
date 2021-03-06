import collections

import numpy as np

def get_pgen(X):
    """Obtains a probability mass function generator from `X`.

    :param X: Matrix where each row is an example and each column a categorical
        attribute.

    :returns: Probability mass function generator :math:`pgen_X`, such that
        ``pgen_x(i)`` returns the function :math:`p_i`. In turn, ``p_i(x)``
        returns the probability of category *x* in the *i*-th attribute.
    """
    m, n = X.shape
    # defaultdict initialises entries to 0.
    pmf = [collections.defaultdict(float) for _ in range(n)]
    for i in range(m):
        for j in range(n):
            c = X[i][j]
            pmf[j][c] += 1
    for j in range(len(pmf)):
        for i in pmf[j]:
            pmf[j][i] /= m
    # `pmf` is a list of dict (array<map<symbol, real>>), using it in the
    # kernels would require to pass the indices all the way down to the
    # univarate kernel. Using a couple of lambdas it can be turned into a
    # function generator such that pgen(j) returns the function p(c) for the
    # j-th attribute in pmf, which avoids some clutter in the code.
    return lambda j: lambda c: pmf[j][c]


def apply_pgen(pgen, X):
    """Applies `pgen` to each element in `X`.

    :param X: Matrix where each row is an example and each column a categorical
        attribute.

    :returns: Matrix *Y* of size :math:`m \\times n`, where
        :math:`Y_{i, j} = P_j(X_{i, j})`.
    """
    m, n = X.shape
    P = np.zeros(X.shape)
    p = 1.0 / (m + 1)
    for i in range(m):
        for j in range(n):
            P[i][j] = max(pgen(j)(X[i][j]), p)
    return P


def pgen(X):
    """Returns a function that applies `pgen` to each element in `X`.

    :param X: Matrix where each row is an example and each column a categorical
        attribute.

    :returns: Function that applies pgen to any matrix.
    """
    pgen = get_pgen(X)
    return lambda Y: apply_pgen(pgen, Y)


def dummy_variable(X):
    """Takes a matrix with a categorical variables and encodes them in dummy
    variable form. Say, for three categories:

    * 0 → 1 0 0
    * 1 → 0 1 0
    * 2 → 0 0 1

    So that it can be used with RBF kernel.
    """
    n, d = X.shape
    y = [[] for _ in range(n)]
    # For each attribute:
    for i in range(d):
        # Get the set of values from the examples:
        values = set()
        for j in range(n):
            values.add(X[j][i])
        # Assign an index to each value:
        index = dict()
        for j, v in enumerate(values):
            index[v] = j
        # Assing len(values) attributes to the example where
        # all but the value of the current one are 0
        for j in range(n):
            v = X[j][i]
            new = [0] * len(values)
            new[index[v]] = 1
            y[j] += new
    return np.array(y)
