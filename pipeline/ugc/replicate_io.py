"""Replicate helper: resolve the model's LIVE input schema, validate our inputs
against it before paying, run, and download the output file.

Why: model input names change between versions. Hard-coded version hashes and
field names (as in the original Google plan) break silently. This checks first.
"""
from __future__ import annotations

from pathlib import Path

import requests

from .common import StageError, env, log


def _client():
    import replicate
    return replicate.Client(api_token=env("REPLICATE_API_TOKEN"))


def input_schema(model_ref: str) -> dict:
    client = _client()
    model = client.models.get(model_ref)
    ver = model.latest_version
    if ver is None:
        raise StageError(f"{model_ref}: no published version")
    props = ver.openapi_schema["components"]["schemas"]["Input"]["properties"]
    required = ver.openapi_schema["components"]["schemas"]["Input"].get("required", [])
    return {"version": ver.id, "properties": props, "required": required}


def validate(model_ref: str, inputs: dict, stage: str) -> dict:
    sch = input_schema(model_ref)
    unknown = [k for k in inputs if k not in sch["properties"]]
    missing = [k for k in sch["required"] if k not in inputs]
    if unknown or missing:
        raise StageError(
            f"{stage}: inputs do not match {model_ref} schema.\n"
            f"  unknown keys: {unknown}\n  missing required: {missing}\n"
            f"  model accepts: {sorted(sch['properties'])}\n"
            f"Fix the `inputs:` mapping in config.yaml."
        )
    log(stage, f"{model_ref} schema OK (version {sch['version'][:12]})")
    return sch


def build_inputs(mapping: dict, files: dict[str, Path], values: dict) -> tuple[dict, list]:
    """mapping values: '@name' -> open file files[name]; '$name' -> values[name]; else literal."""
    out, handles = {}, []
    for k, v in mapping.items():
        if isinstance(v, str) and v.startswith("@"):
            fh = open(files[v[1:]], "rb")
            handles.append(fh)
            out[k] = fh
        elif isinstance(v, str) and v.startswith("$"):
            out[k] = values[v[1:]]
        else:
            out[k] = v
    return out, handles


def run_to_file(model_ref: str, inputs: dict, dest: Path, stage: str) -> Path:
    client = _client()
    log(stage, f"running {model_ref} (this is a paid call)")
    result = client.run(model_ref, input=inputs)
    item = result[0] if isinstance(result, list) else result
    if hasattr(item, "read"):
        dest.write_bytes(item.read())
    else:
        url = str(item)
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        dest.write_bytes(r.content)
    if dest.stat().st_size < 10_000:
        raise StageError(f"{stage}: output {dest} is only {dest.stat().st_size} bytes; model likely failed")
    log(stage, f"saved -> {dest}")
    return dest
