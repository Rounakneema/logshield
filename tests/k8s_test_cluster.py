"""
LogShield Isolated Kubernetes Test Cluster & Control Plane Harness
==================================================================
Runs an isolated, RFC-compliant mock Kubernetes API server on an ephemeral
localhost port to verify end-to-end autonomous containment actions:
- V1NetworkPolicy egress isolation creation & deletion
- Pod annotation and lifecycle patching
- Cross-workload isolation blast-radius verification
- RBAC rejection (HTTP 403) and API timeout/error handling
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional
from kubernetes import client


class IsolatedK8sApiHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default server log spam

    @property
    def cluster_state(self) -> Dict[str, Any]:
        return self.server.cluster_state

    def do_GET(self):
        # 1. API Discovery
        if self.path == "/api/v1":
            self._send_json(200, {
                "kind": "APIResourceList",
                "groupVersion": "v1",
                "resources": [
                    {"name": "pods", "namespaced": True, "kind": "Pod"},
                    {"name": "namespaces", "namespaced": False, "kind": "Namespace"}
                ]
            })
            return
        if self.path == "/apis/networking.k8s.io/v1":
            self._send_json(200, {
                "kind": "APIResourceList",
                "groupVersion": "networking.k8s.io/v1",
                "resources": [
                    {"name": "networkpolicies", "namespaced": True, "kind": "NetworkPolicy"}
                ]
            })
            return

        # 2. Read Pod: /api/v1/namespaces/{ns}/pods/{name}
        if "/api/v1/namespaces/" in self.path and "/pods/" in self.path:
            parts = self.path.split("?")[0].split("/")
            ns = parts[4]
            name = parts[6]
            key = f"{ns}/{name}"
            if key in self.cluster_state["pods"]:
                self._send_json(200, self.cluster_state["pods"][key])
            else:
                self._send_json(404, {"kind": "Status", "status": "Failure", "message": f"Pod {name} not found"})
            return

        # 3. Read NetworkPolicy: /apis/networking.k8s.io/v1/namespaces/{ns}/networkpolicies/{name}
        if "/apis/networking.k8s.io/v1/namespaces/" in self.path and "/networkpolicies/" in self.path:
            parts = self.path.split("?")[0].split("/")
            ns = parts[5]
            name = parts[7]
            key = f"{ns}/{name}"
            if key in self.cluster_state["network_policies"]:
                self._send_json(200, self.cluster_state["network_policies"][key])
            else:
                self._send_json(404, {"kind": "Status", "status": "Failure", "message": f"NetworkPolicy {name} not found"})
            return

        self._send_json(404, {"kind": "Status", "status": "Failure", "message": "Endpoint not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

        # Error injection simulation
        if self.cluster_state.get("inject_rbac_rejection"):
            self._send_json(403, {
                "kind": "Status",
                "status": "Failure",
                "message": "User system:serviceaccount:logshield:sidecar cannot create resource 'networkpolicies' in namespace",
                "reason": "Forbidden",
                "code": 403
            })
            return

        # Create NetworkPolicy: /apis/networking.k8s.io/v1/namespaces/{ns}/networkpolicies
        if "/apis/networking.k8s.io/v1/namespaces/" in self.path and self.path.endswith("/networkpolicies"):
            parts = self.path.split("/")
            ns = parts[5]
            name = body.get("metadata", {}).get("name")
            key = f"{ns}/{name}"
            self.cluster_state["network_policies"][key] = body
            self._send_json(201, body)
            return

        self._send_json(400, {"kind": "Status", "status": "Failure", "message": "Bad Request"})

    def do_PATCH(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

        # Patch Pod: /api/v1/namespaces/{ns}/pods/{name}
        if "/api/v1/namespaces/" in self.path and "/pods/" in self.path:
            parts = self.path.split("?")[0].split("/")
            ns = parts[4]
            name = parts[6]
            key = f"{ns}/{name}"
            if key in self.cluster_state["pods"]:
                pod = self.cluster_state["pods"][key]
                ann = body.get("metadata", {}).get("annotations", {})
                pod.setdefault("metadata", {}).setdefault("annotations", {}).update(ann)
                self._send_json(200, pod)
            else:
                self._send_json(404, {"kind": "Status", "status": "Failure", "message": f"Pod {name} not found"})
            return

        self._send_json(400, {"kind": "Status", "status": "Failure", "message": "Bad Request"})

    def do_DELETE(self):
        # Delete NetworkPolicy: /apis/networking.k8s.io/v1/namespaces/{ns}/networkpolicies/{name}
        if "/apis/networking.k8s.io/v1/namespaces/" in self.path and "/networkpolicies/" in self.path:
            parts = self.path.split("?")[0].split("/")
            ns = parts[5]
            name = parts[7]
            key = f"{ns}/{name}"
            if key in self.cluster_state["network_policies"]:
                del self.cluster_state["network_policies"][key]
                self._send_json(200, {"kind": "Status", "status": "Success", "message": f"NetworkPolicy {name} deleted"})
            else:
                self._send_json(404, {"kind": "Status", "status": "Failure", "message": f"NetworkPolicy {name} not found"})
            return

        self._send_json(400, {"kind": "Status", "status": "Failure", "message": "Bad Request"})

    def _send_json(self, status: int, data: Dict[str, Any]):
        out = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


class IsolatedKubernetesCluster:
    def __init__(self, port: int = 0):
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.cluster_state: Dict[str, Any] = {
            "pods": {},
            "network_policies": {},
            "inject_rbac_rejection": False
        }
        self.api_client: Optional[client.ApiClient] = None

    def start(self):
        self.server = HTTPServer(("127.0.0.1", self.port), IsolatedK8sApiHandler)
        self.server.cluster_state = self.cluster_state
        self.port = self.server.server_port

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        # Build official Kubernetes ApiClient pointing to our isolated server
        k8s_conf = client.Configuration()
        k8s_conf.host = f"http://127.0.0.1:{self.port}"
        k8s_conf.verify_ssl = False
        self.api_client = client.ApiClient(configuration=k8s_conf)

        self._seed_default_workloads()
        return self

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _seed_default_workloads(self):
        """Seeds initial test pods into the cluster."""
        pods = [
            {"name": "auth-service-pod-1", "ns": "production", "app": "auth-service-pod-1"},
            {"name": "payment-service-pod-2", "ns": "production", "app": "payment-service-pod-2"},
            {"name": "notification-service-pod-3", "ns": "production", "app": "notification-service-pod-3"}
        ]
        for p in pods:
            key = f"{p['ns']}/{p['name']}"
            self.cluster_state["pods"][key] = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {
                    "name": p["name"],
                    "namespace": p["ns"],
                    "labels": {"app": p["app"], "env": "prod"},
                    "annotations": {}
                },
                "status": {"phase": "Running"}
            }

    def reset(self):
        self.cluster_state["network_policies"].clear()
        self.cluster_state["inject_rbac_rejection"] = False
        self._seed_default_workloads()
