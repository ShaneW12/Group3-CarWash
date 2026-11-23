
import json
import os

from datetime import date, datetime
from pathlib import Path

from django.conf import settings
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError


# Change this through your environment if needed.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

PROMPT_FILE = (
    Path(settings.BASE_DIR)
    / "prompts"
    / "scheduling_v1.txt"
)


class AIRecommendationError(Exception):
    """Raised when an AI recommendation cannot be obtained."""


def load_scheduling_prompt():
    """
    Read the versioned LLM prompt from disk.
    """
    return PROMPT_FILE.read_text(
        encoding="utf-8"
    )


def recommend_appointment(
    appointment_date,
    selected_services,
    duration_minutes,
    available_slots
):
    """
    Ask Gemini to recommend one of the available
    appointment starting times.

    This function does NOT create appointments.

    Returns:
        {
            "recommended_time": "HH:MM",
            "reason": "Explanation..."
        }

    Returns None if there are no available slots.
    """

    if not isinstance(appointment_date, date) or isinstance(
        appointment_date, datetime
    ):
        raise ValueError("Invalid appointment date.")

    if (
        isinstance(duration_minutes, bool)
        or not isinstance(duration_minutes, int)
        or duration_minutes <= 0
    ):
        raise ValueError("Invalid service duration.")

    if not selected_services:
        raise ValueError("At least one service is required.")

    if not available_slots:
        return None

    # Never trust the LLM to determine availability.
    # These slots must come from scheduling.py.
    valid_slots = set(available_slots)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise AIRecommendationError(
            "GEMINI_API_KEY is not configured."
        )

    prompt_template = load_scheduling_prompt()

    prompt = (
        prompt_template
        .replace(
            "{appointment_date}",
            appointment_date.isoformat()
        )
        .replace(
            "{selected_services}",
            json.dumps(
                selected_services,
                ensure_ascii=False
            )
        )
        .replace(
            "{duration_minutes}",
            str(duration_minutes)
        )
        .replace(
            "{available_slots}",
            json.dumps(available_slots)
        )
    )

    try:
        with genai.Client(api_key=api_key) as client:

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=500,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "recommended_time": {
                                "type": "STRING"
                            },
                            "reason": {
                                "type": "STRING"
                            },
                        },
                        "required": [
                            "recommended_time",
                            "reason",
                        ],
                    },
                ),
            )

        if not response.text:
            raise AIRecommendationError(
                "Gemini returned an empty response."
            )

        result = json.loads(response.text)

        if not isinstance(result, dict):
            raise AIRecommendationError(
                "Gemini returned an invalid response."
            )

        recommended_time = result.get(
            "recommended_time"
        )

        reason = result.get("reason")

        # Critical safeguard:
        # Reject any time not provided by our
        # deterministic scheduling engine.
        if (
            not isinstance(recommended_time, str)
            or recommended_time not in valid_slots
        ):
            raise AIRecommendationError(
                "Gemini recommended an unavailable time."
            )

        if (
            not isinstance(reason, str)
            or not reason.strip()
        ):
            raise AIRecommendationError(
                "Gemini returned an invalid explanation."
            )

        return {
            "recommended_time": recommended_time,
            "reason": reason.strip()[:500],
        }

    except AIRecommendationError:
        raise

    except ServerError as exc:
            if exc.code == 503:
                raise AIRecommendationError(
                    "Gemini is temporarily unavailable due to high demand."
                ) from exc
    
            raise AIRecommendationError(
                f"Gemini server error ({exc.code})."
            ) from exc
    
    except ClientError as exc:
            raise AIRecommendationError(
                f"Gemini rejected the request ({exc.code}). "
                "Check the configured model and API access."
            ) from exc
    
    except Exception as exc:
            raise AIRecommendationError(
                "Unable to generate an AI recommendation."
            ) from exc