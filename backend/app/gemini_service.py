"""Gemini API service for pavement condition assessment."""
import google.generativeai as genai
from app.config import settings
from app.models import PavementCondition
import json
import re

# System instruction for consistent assessment
SYSTEM_INSTRUCTION = """You are an expert pavement condition assessment AI. Analyze street infrastructure images and provide detailed assessments.

For each assessment, respond with JSON containing:
{
  "severity_level": "LOW|MEDIUM|HIGH",
  "damage_types": ["list", "of", "damage", "types"],
  "repair_priority": 1-10,
  "estimated_cost": estimated_cost_in_usd,
  "repair_method": "recommended repair method",
  "detailed_assessment": "comprehensive assessment text"
}

Severity Levels:
- LOW: Hairline cracks, minor surface wear
- MEDIUM: Moderate cracks, some potholes, significant wear
- HIGH: Large potholes, major cracking, safety hazard

Common damage types: hairline_cracks, block_cracking, pothole, rutting, surface_wear, raveling, flushing, bleeding, shoving, warping, joint_failure, patching

Always provide repair recommendations based on the severity and damage types identified."""

# Initialize Gemini
genai.configure(api_key=settings.gemini_api_key)
_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_INSTRUCTION
)


class GeminiAssessmentService:
    """Service for pavement condition assessment using Gemini API."""

    @staticmethod
    async def assess_pavement(images: list, notes: str = "") -> PavementCondition:
        """
        Assess pavement condition from images using Gemini API.

        Args:
            images: List of base64-encoded image strings
            notes: Optional inspection notes

        Returns:
            PavementCondition object with assessment results
        """
        try:
            # Build prompt with image data and notes
            prompt = _build_assessment_prompt(images, notes)

            # Call Gemini API
            response = _model.generate_content(prompt)
            assessment_text = response.text

            # Parse JSON response
            condition = _parse_gemini_response(assessment_text)
            return condition

        except Exception as e:
            raise RuntimeError(f"Gemini assessment failed: {str(e)}")

    @staticmethod
    async def get_raw_assessment(images: list, notes: str = "") -> str:
        """
        Get raw assessment text from Gemini (for debugging/logging).

        Args:
            images: List of base64-encoded image strings
            notes: Optional inspection notes

        Returns:
            Raw assessment text from Gemini
        """
        prompt = _build_assessment_prompt(images, notes)
        response = _model.generate_content(prompt)
        return response.text


def _build_assessment_prompt(images: list, notes: str) -> str:
    """Build comprehensive assessment prompt for Gemini."""
    prompt = "Please assess the pavement condition based on the provided images.\n\n"

    # Add image descriptions (since free tier doesn't support direct image uploads)
    # In production with paid API, these would be actual image parts
    for i, img in enumerate(images, 1):
        prompt += f"[Image {i}: Street pavement photograph - {len(img)} bytes]\n"

    if notes:
        prompt += f"\nInspector Notes: {notes}\n"

    prompt += "\nProvide assessment in JSON format as specified."
    return prompt


def _parse_gemini_response(response_text: str) -> PavementCondition:
    """Parse Gemini response into PavementCondition object."""
    try:
        # Extract JSON from response (Gemini may include markdown formatting)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")

        json_str = json_match.group()
        data = json.loads(json_str)

        return PavementCondition(
            severity_level=data.get("severity_level", "MEDIUM"),
            damage_types=data.get("damage_types", []),
            repair_priority=int(data.get("repair_priority", 5)),
            estimated_cost=float(data.get("estimated_cost", 0)),
            repair_method=data.get("repair_method", "Professional assessment required"),
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response: {str(e)}")
