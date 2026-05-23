"""Tests for envoy_local.router."""

import pytest
from envoy_local.router import (
    RouteMatch,
    RouteAction,
    RouteEntry,
    RouteError,
    build_routes,
    routes_to_envoy_list,
)


# --- RouteMatch ---

def test_route_match_default_prefix():
    m = RouteMatch()
    assert m.to_envoy_dict()["prefix"] == "/"


def test_route_match_custom_prefix():
    m = RouteMatch(prefix="/api")
    assert m.to_envoy_dict()["prefix"] == "/api"


def test_route_match_no_headers_by_default():
    m = RouteMatch()
    d = m.to_envoy_dict()
    assert "headers" not in d


def test_route_match_with_headers():
    headers = [{"name": "x-canary", "exact_match": "true"}]
    m = RouteMatch(prefix="/", headers=headers)
    d = m.to_envoy_dict()
    assert d["headers"] == headers


# --- RouteAction ---

def test_route_action_basic():
    a = RouteAction(cluster="my_cluster")
    d = a.to_envoy_dict()
    assert d["cluster"] == "my_cluster"
    assert d["timeout"] == "15s"


def test_route_action_custom_timeout():
    a = RouteAction(cluster="svc", timeout_seconds=30)
    assert a.to_envoy_dict()["timeout"] == "30s"


def test_route_action_no_retry_policy_by_default():
    a = RouteAction(cluster="svc")
    assert "retry_policy" not in a.to_envoy_dict()


def test_route_action_with_retry_policy():
    a = RouteAction(cluster="svc", retry_on="5xx", num_retries=3)
    d = a.to_envoy_dict()
    assert d["retry_policy"]["retry_on"] == "5xx"
    assert d["retry_policy"]["num_retries"] == 3


# --- build_routes ---

def test_build_routes_returns_list():
    routes = build_routes(cluster="upstream_a")
    assert isinstance(routes, list)
    assert len(routes) == 1


def test_build_routes_entry_type():
    routes = build_routes(cluster="upstream_a")
    assert isinstance(routes[0], RouteEntry)


def test_build_routes_empty_cluster_raises():
    with pytest.raises(RouteError, match="cluster name"):
        build_routes(cluster="")


def test_build_routes_bad_prefix_raises():
    with pytest.raises(RouteError, match="prefix"):
        build_routes(cluster="svc", prefix="api")


def test_build_routes_zero_timeout_raises():
    with pytest.raises(RouteError, match="timeout"):
        build_routes(cluster="svc", timeout_seconds=0)


# --- routes_to_envoy_list ---

def test_routes_to_envoy_list_structure():
    routes = build_routes(cluster="backend", prefix="/v1")
    result = routes_to_envoy_list(routes)
    assert isinstance(result, list)
    assert result[0]["match"]["prefix"] == "/v1"
    assert result[0]["route"]["cluster"] == "backend"


def test_routes_to_envoy_list_empty():
    assert routes_to_envoy_list([]) == []
