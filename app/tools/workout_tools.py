"""Firestore tools for TriCoach AI workout catalog and logging."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

from google.cloud.firestore_v1.base_query import FieldFilter

PROJECT_ID = "qwiklabs-gcp-01-57b0d8b0ef08"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def list_workouts(sport: Optional[str] = None) -> List[Dict[str, Any]]:
    """List workouts from the training catalog, optionally filtered by sport/type.

    Args:
        sport: Optional sport filter ('swimming', 'cycling', or 'running').

    Returns:
        List of workout dictionary records.
    """
    db = _get_firestore_client()
    query = db.collection("workouts")
    if sport:
        query = query.where(filter=FieldFilter("type", "==", sport.lower()))

    docs = query.stream()
    workouts = []
    for doc in docs:
        data = doc.to_dict()
        data["doc_id"] = doc.id
        workouts.append(data)
    return workouts


def get_workout_details(workout_id: str) -> Dict[str, Any]:
    """Get detailed specifications for a specific workout template by ID.

    Args:
        workout_id: The unique identifier for the workout (e.g. 'w1', 'w2').

    Returns:
        Workout specification dictionary or an error message if not found.
    """
    db = _get_firestore_client()
    doc_ref = db.collection("workouts").document(workout_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["doc_id"] = doc.id
        return data
    return {"error": f"Workout '{workout_id}' not found."}


def log_completed_workout(
    title: str,
    sport: str,
    duration_minutes: int,
    target_zone: str,
    description: str,
    tss_estimate: Optional[int] = 50,
) -> Dict[str, Any]:
    """Log a new completed or custom workout session into the database.

    Args:
        title: Title of the workout.
        sport: Sport type ('swimming', 'cycling', 'running', or 'strength').
        duration_minutes: Duration of the session in minutes.
        target_zone: Heart rate or power target zone (e.g., 'Zone 2', 'Zone 4').
        description: Summary notes or workout session details.
        tss_estimate: Estimated Training Stress Score (default: 50).

    Returns:
        Confirmation dictionary with doc_id and status.
    """
    db = _get_firestore_client()
    doc_ref = db.collection("workouts").document()
    workout_data = {
        "workout_id": doc_ref.id,
        "title": title,
        "type": sport.lower(),
        "duration_minutes": duration_minutes,
        "target_zone": target_zone,
        "description": description,
        "tss_estimate": tss_estimate,
    }
    doc_ref.set(workout_data)
    return {
        "status": "success",
        "message": f"Successfully logged workout '{title}'",
        "workout_id": doc_ref.id,
        "details": workout_data,
    }
