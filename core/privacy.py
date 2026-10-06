"""Role-view helpers for the synthetic demo; these are not access controls."""
from __future__ import annotations

import hashlib


def mask_participant_id(value: str) -> str:
    token = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:8].upper()
    return f"PESERTA-{token}"


def mask_graph(nodes: list[dict], edges: list[dict]) -> tuple[list[dict], list[dict]]:
    mapping = {}
    masked_nodes = []
    for node in nodes:
        item = dict(node)
        if item.get("type") == "pasien":
            old = str(item["id"])
            person = old.removeprefix("p_")
            new = "p_" + mask_participant_id(person)
            mapping[old] = new
            item["id"] = new
            item["label"] = f"Peserta {mask_participant_id(person)}"
        masked_nodes.append(item)
    masked_edges = [dict(e, src=mapping.get(e["src"], e["src"]), dst=mapping.get(e["dst"], e["dst"]))
                    for e in edges]
    return masked_nodes, masked_edges
