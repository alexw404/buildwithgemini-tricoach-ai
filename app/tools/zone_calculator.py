"""Training zone calculator tool for TriCoach AI."""

from typing import Any, Dict, Optional


def calculate_training_zones(
    ftp: Optional[int] = None, max_hr: Optional[int] = None
) -> Dict[str, Any]:
    """Calculate personalized cycling power zones and heart rate training zones.

    Args:
        ftp: Functional Threshold Power in Watts (e.g. 250).
        max_hr: Maximum Heart Rate in beats per minute (e.g. 185).

    Returns:
        Dictionary containing power zones (Watts) and heart rate zones (BPM).
    """
    result: Dict[str, Any] = {}

    if ftp is not None and ftp > 0:
        result["power_zones_watts"] = {
            "ftp": ftp,
            "zone_1_active_recovery": f"< {round(ftp * 0.55)}W",
            "zone_2_endurance": f"{round(ftp * 0.55)}W - {round(ftp * 0.75)}W",
            "zone_3_tempo": f"{round(ftp * 0.76)}W - {round(ftp * 0.90)}W",
            "zone_4_threshold": f"{round(ftp * 0.91)}W - {round(ftp * 1.05)}W",
            "zone_5_vo2max": f"{round(ftp * 1.06)}W - {round(ftp * 1.20)}W",
            "zone_6_anaerobic": f"{round(ftp * 1.21)}W - {round(ftp * 1.50)}W",
            "zone_7_neuromuscular": f"> {round(ftp * 1.50)}W",
        }

    if max_hr is not None and max_hr > 0:
        result["heart_rate_zones_bpm"] = {
            "max_hr": max_hr,
            "zone_1_warmup": f"{round(max_hr * 0.50)} - {round(max_hr * 0.60)} bpm",
            "zone_2_aerobic": f"{round(max_hr * 0.60)} - {round(max_hr * 0.70)} bpm",
            "zone_3_tempo": f"{round(max_hr * 0.70)} - {round(max_hr * 0.80)} bpm",
            "zone_4_threshold": f"{round(max_hr * 0.80)} - {round(max_hr * 0.90)} bpm",
            "zone_5_vo2max": f"{round(max_hr * 0.90)} - {max_hr} bpm",
        }

    if not result:
        return {
            "error": "Please provide at least one metric: ftp (e.g. 250) or max_hr (e.g. 185)."
        }

    return result
