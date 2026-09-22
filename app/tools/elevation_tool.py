"""Route elevation and grade analysis tool for outdoor runners and cyclists."""

import math
from typing import Any
import httpx

OPEN_METEO_ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two lat/lon coordinates."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def analyze_outdoor_route_feasibility(
    latitudes: list[float], longitudes: list[float]
) -> dict[str, Any]:
    """Analyze outdoor route elevation, incline slope/grade, and feasibility for runners and cyclists.

    Args:
        latitudes: List of latitude coordinates along the route (at least 2 points).
        longitudes: List of longitude coordinates along the route (at least 2 points).

    Returns:
        Analysis dictionary containing total distance (km), elevation gain/loss (m), max slope grade (%),
        segment-by-segment details, and workout feasibility recommendations for running and cycling.
    """
    if len(latitudes) < 2 or len(longitudes) < 2 or len(latitudes) != len(longitudes):
        return {
            "error": "Please provide at least 2 matching latitude and longitude points."
        }

    try:
        lat_str = ",".join(map(str, latitudes))
        lon_str = ",".join(map(str, longitudes))
        response = httpx.get(
            OPEN_METEO_ELEVATION_URL,
            params={"latitude": lat_str, "longitude": lon_str},
            timeout=10.0,
        )
        response.raise_for_status()
        elevations = response.json().get("elevation", [])

        if not elevations or len(elevations) != len(latitudes):
            return {"error": "Failed to fetch elevation data for coordinates."}

        total_distance_m = 0.0
        elevation_gain_m = 0.0
        elevation_loss_m = 0.0
        segments = []
        max_grade = 0.0

        for i in range(len(latitudes) - 1):
            dist = _haversine_distance(
                latitudes[i], longitudes[i], latitudes[i + 1], longitudes[i + 1]
            )
            total_distance_m += dist
            elev_diff = elevations[i + 1] - elevations[i]

            if elev_diff > 0:
                elevation_gain_m += elev_diff
            else:
                elevation_loss_m += abs(elev_diff)

            grade = (elev_diff / dist * 100) if dist > 0 else 0.0
            if abs(grade) > abs(max_grade):
                max_grade = grade

            segments.append(
                {
                    "segment": i + 1,
                    "distance_m": round(dist, 1),
                    "elevation_start_m": elevations[i],
                    "elevation_end_m": elevations[i + 1],
                    "grade_percent": round(grade, 2),
                }
            )

        # Feasibility assessment
        abs_max_grade = abs(max_grade)
        if abs_max_grade <= 3.0:
            running_feasibility = "Excellent (Flat to gentle slope, ideal for speed work, tempo runs, or endurance pacing)."
            cycling_feasibility = "Excellent (Fast, smooth terrain suitable for time trials or recovery rides)."
        elif abs_max_grade <= 7.0:
            running_feasibility = "Moderate (Rolling hills, great for building endurance and leg power)."
            cycling_feasibility = "Good (Steady moderate climbs, ideal for aerobic threshold work)."
        elif abs_max_grade <= 12.0:
            running_feasibility = "Challenging (Steep incline, best for hill repeats or strength-building sessions)."
            cycling_feasibility = "Challenging (Category 2/3 climb, requires low gearing and strong effort)."
        else:
            running_feasibility = "Severe (Very steep grade, high joint strain; recommended for short power hill sprints or trail hiking)."
            cycling_feasibility = "Extreme (Cat 1/HC wall, extremely tough climbing, requires compact chainrings and steep climbing technique)."

        return {
            "total_distance_km": round(total_distance_m / 1000, 2),
            "elevation_gain_m": round(elevation_gain_m, 1),
            "elevation_loss_m": round(elevation_loss_m, 1),
            "max_grade_percent": round(max_grade, 2),
            "running_feasibility": running_feasibility,
            "cycling_feasibility": cycling_feasibility,
            "segments": segments,
        }
    except Exception as e:
        return {"error": f"Failed to analyze route feasibility: {str(e)}"}
