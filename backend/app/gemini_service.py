"""Gemini API service for pavement condition assessment using real multimodal image input."""
import google.generativeai as genai
from app.config import settings
from app.models import PavementCondition
import json
import re
import base64

# System instruction for consistent structured assessment
SYSTEM_INSTRUCTION = """You are an expert pavement condition assessment AI for municipal infrastructure. 
Analyze street/road pavement images provided and return a structured JSON assessment.

You MUST respond with ONLY valid JSON (no markdown, no backticks, no explanation) in this exact format:
{
  "severity_level": "LOW|MEDIUM|HIGH",
  "damage_types": ["list", "of", "damage", "types"],
  "repair_priority": <integer 1-10>,
  "estimated_cost": <float in USD>,
  "repair_method": "specific recommended repair action",
  "detailed_assessment": "2-3 sentence description of observed damage"
}

Severity Levels:
- LOW: Hairline cracks, minor surface wear, no safety risk
- MEDIUM: Moderate cracks, small potholes, some structural concern  
- HIGH: Large potholes, major cracking, water ingress, immediate safety hazard

Common damage types to use: hairline_cracks, block_cracking, pothole, rutting, 
surface_wear, raveling, flushing, bleeding, shoving, warping, joint_failure, patching, water_ingress

Repair cost guide (USD):
- LOW severity: $200-$800
- MEDIUM severity: $800-$2500  
- HIGH severity: $2500-$8000

Always base your assessment on what you actually see in the image."""

# Initialize Gemini with multimodal model (supports images on free tier)
genai.configure(api_key=settings.gemini_api_key)
_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config=genai.types.GenerationConfig(
        temperature=0.1,  # Low temperature for consistent structured output
        response_mime_type="application/json",
    )
)


class GeminiAssessmentService:
    """Service for pavement condition assessment using Gemini multimodal API."""

    @staticmethod
    async def assess_pavement(images: list, notes: str = "") -> PavementCondition:
        """
        Assess pavement condition from real base64 images using Gemini Vision API.

        Args:
            images: List of base64-encoded image strings
            notes: Optional inspection notes from inspector

        Returns:
            PavementCondition object with AI assessment results
        """
        try:
            content_parts = _build_content_parts(images, notes)
            response = _model.generate_content(content_parts)
            assessment_text = response.text
            condition = _parse_gemini_response(assessment_text)
            return condition
        except Exception as e:
            raise RuntimeError(f"Gemini assessment failed: {str(e)}")

    @staticmethod
    async def get_raw_assessment(images: list, notes: str = "") -> str:
        """Get raw JSON assessment text from Gemini for logging/storage."""
        try:
            content_parts = _build_content_parts(images, notes)
            response = _model.generate_content(content_parts)
            return response.text
        except Exception as e:
            return f"Raw assessment unavailable: {str(e)}"


def _build_content_parts(images: list, notes: str) -> list:
    """
    Build multimodal content parts for Gemini — sends actual image data.
    Each base64 image is sent as an inline image part.
    """
    parts = []

    # Add prompt text first
    prompt_text = "Please assess the pavement condition in the following image(s)."
    if notes:
        prompt_text += f"\n\nInspector field notes: \"{notes}\""
    prompt_text += "\n\nProvide your assessment as JSON."
    parts.append(prompt_text)

    # Add each image as a real inline image part (Gemini multimodal)
    for img_b64 in images:
        # Detect image type from base64 header, default to jpeg
        mime_type = "image/jpeg"
        if img_b64.startswith("/9j/"):
            mime_type = "image/jpeg"
        elif img_b64.startswith("iVBOR"):
            mime_type = "image/png"
        elif img_b64.startswith("R0lGOD"):
            mime_type = "image/gif"
        elif img_b64.startswith("UklGR"):
            mime_type = "image/webp"

        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": img_b64
            }
        })

    return parts


def _parse_gemini_response(response_text: str) -> PavementCondition:
    """Parse Gemini JSON response into a PavementCondition object."""
    try:
        # Strip any accidental markdown fences
        cleaned = response_text.strip()
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()

        # Extract JSON object
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON object found in response: {cleaned[:200]}")

        data = json.loads(json_match.group())

        return PavementCondition(
            severity_level=data.get("severity_level", "MEDIUM").upper(),
            damage_types=data.get("damage_types", ["surface_wear"]),
            repair_priority=int(data.get("repair_priority", 5)),
            estimated_cost=float(data.get("estimated_cost", 500.0)),
            repair_method=data.get("repair_method", "Schedule professional assessment"),
            detailed_assessment=data.get("detailed_assessment", ""),
        )
    except (json.JSONDecodeError, ValueError) as e:
        # Fallback — don't crash the whole request
        return PavementCondition(
            severity_level="MEDIUM",
            damage_types=["surface_wear"],
            repair_priority=5,
            estimated_cost=500.0,
            repair_method="Unable to parse AI response. Manual inspection required.",
            detailed_assessment=f"Parse error: {str(e)[:100]}",
        )
