from blaze.expr.optimize import lean_projection, _lean
from blaze.expr import symbol, summary, by, By, Field, Projection, merge, sum

t = symbol('t', 'var * {x: int, y: int, z: int, w: int}')


def test_lean_on_Symbol():
    assert _lean(t, fields=['x'])[0] == t[['x']]
    assert _lean(t, fields=['x', 'y', 'z', 'w'])[0] == t


def test_lean_projection():
    assert lean_projection(t[t.x > 0].y)._child._child is t[['x', 'y']]


def test_lean_projection_by():
    assert lean_projection(by(t.x, total=t.y.sum()))._child is t[['x', 'y']]


def test_lean_by_with_summary():
    assert lean_projection(by(t.x, total=t.y.sum()))._child is t[['x', 'y']]

    tt = t[['x', 'y']]
    result = lean_projection(by(t.x, a=t.y.sum(), b=t.z.sum())[['x', 'a']])
    expected = Projection(
        By(Field(tt, 'x'), summary(a=sum(Field(tt, 'y')))),
        ('x', 'a'),
    )
    assert result is expected


def test_summary():
    expr, fields = _lean(summary(a=t.x.sum(), b=t.y.sum()), fields=['a'])
    assert expr is summary(a=t.x.sum())
    assert fields == {'x'}


def test_sort():
    assert lean_projection(t.sort('x').y) is t[['x','y']].sort('x').y


def test_merge():
    expr = lean_projection(merge(a=t.x+1, y=t.y))
    assert expr._child is t[['x', 'y']]


def test_add():
    expr = t.x + 1
    expr2, fields = _lean(expr, fields=set(['x']))
    assert expr2 is expr
    assert fields == {'x'}

    expr = (t.x + t.y).label('a')
    expr2, fields = _lean(expr, fields=set(['a']))
    assert expr2 is expr
    assert fields == {'x', 'y'}


def test_label():
    expr = t.x.label('foo')
    expr2, fields =  _lean(expr, fields=set(['foo']))
    assert expr2 is expr
    assert fields == {'x'}


def test_relabel():
    expr = t.relabel(x='X', y='Y')
    expr2, fields = _lean(expr, fields=set(['X', 'z']))
    assert expr2 is t[['x', 'z']].relabel(x='X')
    assert fields == {'x', 'z'}


def test_merge_with_table():
    expr = lean_projection(merge(t, a=t.x+1))
    assert expr is expr  # wut?


def test_head():
    assert (
        lean_projection(t.sort('x').y.head(5)) is
        t[['x','y']].sort('x').y.head(5)
    )


def test_elemwise_thats_also_a_column():
    t = symbol('t', 'var * {x: int, time: datetime, y: int}')
    expr = t[t.x > 0].time.truncate(months=1)
    expected = t[['time', 'x']]
    result = lean_projection(expr)
    assert result._child._child._child is expected


def test_distinct():
    expr = t.distinct()[['x', 'y']]
    assert lean_projection(expr) is expr


def test_like():
    t = symbol('t', 'var * {name: string, x: int, y: int}')
    expr = t[t.name.like('Alice')].y
    result = lean_projection(expr)
    assert result._child._child is t[['name', 'y']]
