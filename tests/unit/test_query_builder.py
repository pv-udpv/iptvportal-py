"""Tests for query builder."""

import pytest
from iptvportal.query.builder import QueryBuilder
from iptvportal.query.operators import Q


def test_query_builder_select_basic():
    """Test basic SELECT query."""
    qb = QueryBuilder()
    
    query = qb.select(
        data=["id", "name"],
        from_="tv_channel",
        limit=10
    )
    
    assert query["jsonrpc"] == "2.0"
    assert query["id"] == 1
    assert query["method"] == "select"
    assert query["params"]["data"] == ["id", "name"]
    assert query["params"]["from"] == "tv_channel"
    assert query["params"]["limit"] == 10


def test_query_builder_select_with_where():
    """Test SELECT with WHERE clause."""
    qb = QueryBuilder()
    
    query = qb.select(
        data=["id", "name"],
        from_="tv_channel",
        where=Q.eq("id", 5402)
    )
    
    assert query["params"]["where"] == {"eq": ["id", 5402]}


def test_query_builder_insert():
    """Test INSERT query."""
    qb = QueryBuilder()
    
    query = qb.insert(
        into="tv_channel",
        columns=["name", "number"],
        values=[["Test Channel", 100]]
    )
    
    assert query["method"] == "insert"
    assert query["params"]["into"] == "tv_channel"
    assert query["params"]["columns"] == ["name", "number"]
    assert query["params"]["values"] == [["Test Channel", 100]]


def test_query_builder_update():
    """Test UPDATE query."""
    qb = QueryBuilder()
    
    query = qb.update(
        table="tv_channel",
        set_={"name": "Updated Name"},
        where=Q.eq("id", 5402)
    )
    
    assert query["method"] == "update"
    assert query["params"]["table"] == "tv_channel"
    assert query["params"]["set"] == {"name": "Updated Name"}
    assert query["params"]["where"] == {"eq": ["id", 5402]}


def test_query_builder_delete():
    """Test DELETE query."""
    qb = QueryBuilder()
    
    query = qb.delete(
        from_="tv_channel",
        where=Q.eq("id", 5402)
    )
    
    assert query["method"] == "delete"
    assert query["params"]["from"] == "tv_channel"
    assert query["params"]["where"] == {"eq": ["id", 5402]}


def test_query_builder_upsert():
    """Test UPSERT query."""
    qb = QueryBuilder()
    
    query = qb.upsert(
        into="subscriber",
        columns=["username", "password"],
        values=[["user1", "pass1"]],
        conflict_columns=["username"],
        update_set={"password": {"excluded": "password"}},
        returning=["id"]
    )
    
    assert query["method"] == "insert"
    assert query["params"]["on_conflict"]["columns"] == ["username"]
    assert query["params"]["on_conflict"]["do"] == "update"
    assert query["params"]["returning"] == ["id"]


# Q Operators Tests

def test_q_eq():
    """Test Q.eq operator."""
    result = Q.eq("id", 100)
    assert result == {"eq": ["id", 100]}


def test_q_gt():
    """Test Q.gt operator."""
    result = Q.gt("views", 1000)
    assert result == {"gt": ["views", 1000]}


def test_q_in():
    """Test Q.in_ operator."""
    result = Q.in_("id", [1, 2, 3])
    assert result == {"in": ["id", [1, 2, 3]]}


def test_q_like():
    """Test Q.like operator."""
    result = Q.like("name", "%test%")
    assert result == {"like": ["name", "%test%"]}


def test_q_ilike():
    """Test Q.ilike operator."""
    result = Q.ilike("name", "%test%")
    assert result == {"ilike": ["name", "%test%"]}


def test_q_and():
    """Test Q.and_ operator."""
    result = Q.and_(
        Q.eq("status", "active"),
        Q.gt("views", 100)
    )
    assert result == {
        "and": [
            {"eq": ["status", "active"]},
            {"gt": ["views", 100]}
        ]
    }


def test_q_or():
    """Test Q.or_ operator."""
    result = Q.or_(
        Q.eq("type", "movie"),
        Q.eq("type", "series")
    )
    assert result == {
        "or": [
            {"eq": ["type", "movie"]},
            {"eq": ["type", "series"]}
        ]
    }


def test_q_not():
    """Test Q.not_ operator."""
    result = Q.not_(Q.eq("status", "deleted"))
    assert result == {"not": [{"eq": ["status", "deleted"]}]}


def test_q_complex_condition():
    """Test complex nested conditions."""
    result = Q.and_(
        Q.or_(
            Q.eq("type", "movie"),
            Q.eq("type", "series")
        ),
        Q.gt("rating", 7.0),
        Q.not_(Q.eq("status", "deleted"))
    )
    
    assert result == {
        "and": [
            {
                "or": [
                    {"eq": ["type", "movie"]},
                    {"eq": ["type", "series"]}
                ]
            },
            {"gt": ["rating", 7.0]},
            {"not": [{"eq": ["status", "deleted"]}]}
        ]
    }
