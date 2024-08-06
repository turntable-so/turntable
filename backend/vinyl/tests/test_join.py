import pytest

from internal_project.sources.local_filesystem.store_num_transactions import (
    StoreNumTransactions,
)
from internal_project.sources.local_filesystem.stores import Stores
from vinyl.lib.set import join


def test_two_way_auto_join_with_match():
    a = Stores()
    b = StoreNumTransactions()
    y = a.select({"cit": a.city, "nbr": a.store_nbr})
    z = b.select({"nbr2": b.store_nbr, "t": b.transactions})

    j = join(y, z)
    j2 = join(z, y)
    j3 = y * z
    j4 = z * y

    assert all(len(t._conn_replace.items()) == 2 for t in [j, j2, j3, j4])

    assert all(
        [
            t._reproducible_hash() == "3f7641d3d68c717ab276776599ca72d2"
            for t in [j, j2, j3, j4]
        ]
    )


def test_two_way_auto_join_without_match():
    a = Stores()
    b = StoreNumTransactions()
    y = a.select({"cit": a.city, "nbr": a.store_nbr})
    z = b.select({"t": b.transactions})

    # automatic joins with the join function don't allow cross joins by default
    with pytest.raises(ValueError):
        join(y, z)
        j2 = join(z, y)

    # automatic joins with the multiply symbol allow for up to one cross join, these have different hashes because cross join order is based on input order by default
    j1 = join(y, z, auto_allow_cross_join=True)
    j2 = join(z, y, auto_allow_cross_join=True)
    j3 = y * z
    j4 = z * y

    assert all(len(t._conn_replace.items()) == 2 for t in [j1, j2, j3, j4])

    assert all(
        [t._reproducible_hash() == "a28237374e96fa9c2e6ee31bab97424a" for t in [j1, j3]]
    )
    assert all(
        [t._reproducible_hash() == "dcba46d0f9dae45d48b5fa0b01fa7ca4" for t in [j2, j4]]
    )
