"""Review completion is separate from a simulated follow-up action."""
def cluster_status(action, feedback=None):
    if feedback and feedback.get("verdict") == "dismiss" or action == "dismiss":
        return "✓ Selesai ditinjau · pola wajar (simulasi)", "teal", True
    if action == "field_audit":
        return "◷ Dalam pemeriksaan · rencana lapangan dicatat", "amber", False
    if action == "freeze" or feedback and feedback.get("verdict") == "confirm":
        return "◷ Dalam pemeriksaan · penangguhan simulasi dicatat", "amber", False
    return "○ Belum ditinjau", "grey", False
