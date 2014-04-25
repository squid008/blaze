
from blaze.objects.table import *
from multipledispatch import dispatch
from toolz.curried import *
import itertools
from collections import Iterator

base = (int, float, str, bool)

seq = (tuple, list, Iterator)

@dispatch(Projection, seq)
def compute(t, l):
    indices = [t.table.columns.index(col) for col in t.columns]
    return list(map(get(indices), l))


@dispatch(Column, seq)
def compute(t, l):
    index = t.table.columns.index(t.columns[0])
    return [x[index] for x in l]


@dispatch(base, object)
def compute(a, b):
    return a


@dispatch(Relational, seq)
def compute(t, l):
    lhs_istable = isinstance(t.lhs, Table)
    rhs_istable = isinstance(t.rhs, Table)

    if lhs_istable and rhs_istable:

        l1, l2 = itertools.tee(l, 2)
        lhs = compute(t.lhs, l1)
        rhs = compute(t.rhs, l2)

        return (t.op(left, right) for left, right in zip(lhs, rhs))

    elif lhs_istable:

        lhs = compute(t.lhs, l)
        right = compute(t.rhs, None)

        return (t.op(left, right) for left in lhs)

    elif rhs_istable:

        rhs = compute(t.rhs, l)
        left = compute(t.lhs, None)

        return (t.op(left, right) for right in rhs)


@dispatch(Selection, seq)
def compute(t, l):
    l, l2 = itertools.tee(l)
    return (x for x, tf in zip(compute(t.table, l), compute(t.predicate, l2))
              if tf)


@dispatch(Table, seq)
def compute(t, l):
    return l
