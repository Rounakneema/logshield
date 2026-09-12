import os
import base64
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# The sidecar container definition
SIDECAR_CONTAINER = {
    "name": "logshield-sidecar",
    "image": "logshield-sidecar:latest",
    "imagePullPolicy": "IfNotPresent",
    "env": [
        {
            "name": "POD_NAME",
            "valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}}
        },
        {
            "name": "NAMESPACE",
            "valueFrom": {"fieldRef": {"fieldPath": "metadata.namespace"}}
        },
        {"name": "LOG_INPUT_PATH", "value": "/shared/app.log"}
    ],
    "volumeMounts": [
        {"name": "shared-logs", "mountPath": "/shared", "readOnly": True},
        {"name": "sidecar-data", "mountPath": "/data"}
    ],
    "securityContext": {
        "readOnlyRootFilesystem": True,
        "allowPrivilegeEscalation": False,
        "runAsNonRoot": True,
        "runAsUser": 1000
    }
}

# The volumes required by the sidecar
SIDECAR_VOLUMES = [
    {"name": "shared-logs", "emptyDir": {}},
    {"name": "sidecar-data", "emptyDir": {}}
]

def generate_patch(pod):
    """
    Generates a JSON Patch to inject the LogShield sidecar and volumes.
    Also modifies existing application containers to mount the shared logs volume
    so they can write to /shared/app.log if they aren't already logging there.
    """
    patch = []
    
    # 1. Inject Sidecar Container
    containers = pod.get("spec", {}).get("containers", [])
    if "containers" not in pod.get("spec", {}):
        patch.append({"op": "add", "path": "/spec/containers", "value": [SIDECAR_CONTAINER]})
    else:
        patch.append({"op": "add", "path": "/spec/containers/-", "value": SIDECAR_CONTAINER})
        
        # Optionally inject volume mounts into existing containers
        if len(containers) > 0:
            first_container = containers[0]
            volume_mounts = first_container.get("volumeMounts", [])
            has_shared_logs = any(vm.get("name") == "shared-logs" for vm in volume_mounts)
            if not has_shared_logs:
                if "volumeMounts" not in first_container:
                    patch.append({"op": "add", "path": "/spec/containers/0/volumeMounts", "value": [{"name": "shared-logs", "mountPath": "/shared"}]})
                else:
                    patch.append({"op": "add", "path": "/spec/containers/0/volumeMounts/-", "value": {"name": "shared-logs", "mountPath": "/shared"}})

    # 2. Inject Volumes
    volumes = pod.get("spec", {}).get("volumes", [])
    if "volumes" not in pod.get("spec", {}):
        patch.append({"op": "add", "path": "/spec/volumes", "value": SIDECAR_VOLUMES})
    else:
        for vol in SIDECAR_VOLUMES:
            patch.append({"op": "add", "path": "/spec/volumes/-", "value": vol})
            
    return patch

@app.route('/mutate', methods=['POST'])
def mutate():
    request_info = request.json
    if not request_info or "request" not in request_info:
        return jsonify({"response": {"allowed": True, "status": {"message": "Invalid request"}}})

    req = request_info["request"]
    uid = req.get("uid")
    pod = req.get("object", {})

    # Default response: allow without patching
    response = {
        "uid": uid,
        "allowed": True
    }

    # Check if already injected
    containers = pod.get("spec", {}).get("containers", [])
    already_injected = any(c.get("name") == "logshield-sidecar" for c in containers)
    
    if not already_injected:
        patch = generate_patch(pod)
        patch_bytes = json.dumps(patch).encode("utf-8")
        
        response["patchType"] = "JSONPatch"
        response["patch"] = base64.b64encode(patch_bytes).decode("utf-8")
        print(f"[LogShield] Injected sidecar into pod {pod.get('metadata', {}).get('name', 'unknown')}")

    return jsonify({
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": response
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    cert_path = os.getenv("TLS_CERT", "/etc/webhook/certs/tls.crt")
    key_path = os.getenv("TLS_KEY", "/etc/webhook/certs/tls.key")
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        app.run(host='0.0.0.0', port=8443, ssl_context=(cert_path, key_path))
    else:
        print("WARNING: Starting without TLS. Kubernetes requires TLS for webhooks.")
        app.run(host='0.0.0.0', port=8443)
