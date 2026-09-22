# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

import os

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from app.a2ui_utils import a2ui_callback
from app.tools.elevation_tool import analyze_outdoor_route_feasibility
from app.tools.image_tool import generate_triathlon_badge_image
from app.tools.rag_tool import consult_triathlon_manual
from app.tools.video_tool import generate_triathlon_video
from app.tools.weather_tool import get_outdoor_training_weather
from app.tools.workout_tools import (
    get_workout_details,
    list_workouts,
    log_completed_workout,
)
from app.tools.zone_calculator import calculate_training_zones

AGENT_ENGINE_RESOURCE_NAME = os.getenv(
    "AGENT_ENGINE_RESOURCE_NAME",
    "projects/250828361255/locations/us-central1/reasoningEngines/8432659899007107072",
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are TriCoach AI, a personal fitness and triathlon coach. "
        "You remember the user's stated fitness goals, FTP, max heart rate, target race date, "
        "and preferences across conversations, using them to personalize your coaching recommendations. "
        "You can check live outdoor training weather conditions, calculate training zones, "
        "analyze route elevation, incline slope/grade, and feasibility for runners and cyclists, "
        "access a database of workout catalog items, log completed workouts, consult the triathlon training manual, "
        "generate motivational workout achievement badges, generate short triathlon training video clips, "
        "and execute Python code safely in a sandbox using your tools."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


def get_current_time(city: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    city_lower = city.lower()
    if "sf" in city_lower or "san francisco" in city_lower:
        tz_identifier = "America/Los_Angeles"
    elif "ny" in city_lower or "new york" in city_lower:
        tz_identifier = "America/New_York"
    elif "london" in city_lower:
        tz_identifier = "Europe/London"
    elif "tokyo" in city_lower:
        tz_identifier = "Asia/Tokyo"
    else:
        return f"Sorry, I don't have timezone information for city: {city}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=AGENT_ENGINE_RESOURCE_NAME
    ),
    tools=[
        PreloadMemoryTool(),
        get_outdoor_training_weather,
        get_current_time,
        list_workouts,
        get_workout_details,
        log_completed_workout,
        calculate_training_zones,
        consult_triathlon_manual,
        generate_triathlon_badge_image,
        generate_triathlon_video,
        analyze_outdoor_route_feasibility,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
