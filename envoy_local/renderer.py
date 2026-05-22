"""Renders EnvoyConfig objects into a valid envoy.yaml bootstrap configuration."""

import yaml
from typing import Any, Dict

from envoy_local.config import EnvoyConfig


def _build_cluster(upstream) -> Dict[str, Any]:
    return {
        "name": upstream.cluster_name(),
        "connect_timeout": "1s",
        "type": "STRICT_DNS",
        "lb_policy": "ROUND_ROBIN",
        "load_assignment": {
            "cluster_name": upstream.cluster_name(),
            "endpoints": [
                {
                    "lb_endpoints": [
                        {
                            "endpoint": {
                                "address": {
                                    "socket_address": {
                                        "address": upstream.host,
                                        "port_value": upstream.port,
                                    }
                                }
                            }
                        }
                    ]
                }
            ],
        },
    }


def _build_virtual_host(upstreams) -> Dict[str, Any]:
    routes = [
        {
            "match": {"prefix": f"/{u.name}/"},
            "route": {"cluster": u.cluster_name()},
        }
        for u in upstreams
    ]
    return {
        "name": "local_services",
        "domains": ["*"],
        "routes": routes,
    }


def render(config: EnvoyConfig) -> str:
    """Return a YAML string representing the Envoy bootstrap configuration."""
    config.validate()

    bootstrap = {
        "admin": {
            "address": {
                "socket_address": {"address": "127.0.0.1", "port_value": config.admin_port}
            }
        },
        "static_resources": {
            "listeners": [
                {
                    "name": "main_listener",
                    "address": {
                        "socket_address": {
                            "address": config.listener.address,
                            "port_value": config.listener.port,
                        }
                    },
                    "filter_chains": [
                        {
                            "filters": [
                                {
                                    "name": "envoy.filters.network.http_connection_manager",
                                    "typed_config": {
                                        "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                                        "stat_prefix": "ingress_http",
                                        "route_config": {
                                            "virtual_hosts": [_build_virtual_host(config.upstreams)]
                                        },
                                        "http_filters": [{"name": "envoy.filters.http.router"}],
                                    },
                                }
                            ]
                        }
                    ],
                }
            ],
            "clusters": [_build_cluster(u) for u in config.upstreams],
        },
    }

    return yaml.dump(bootstrap, default_flow_style=False, sort_keys=False)
