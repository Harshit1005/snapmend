"""Gemini API service for pavement condition assessment using real multimodal image input."""
from google import genai
from google.genai import types
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
  "detailed_assessment": "2-3 sentence description of observed damage, explicitly justifying the severity and cost based on the provided geographical research context."
}

Severity Levels:
- LOW: Hairline cracks, minor surface wear, no safety risk
- MEDIUM: Moderate cracks, small potholes, some structural concern
- HIGH: Large potholes, major cracking, water ingress, immediate safety hazard

Common damage types: hairline_cracks, block_cracking, pothole, rutting,
surface_wear, raveling, flushing, bleeding, shoving, warping, joint_failure, patching, water_ingress

CRITICAL INSTRUCTION:
You must calculate the `estimated_cost` and `severity_level` dynamically by factoring in the regional construction costs, traffic density, and climate information provided in the "Contextual Research Report" (if available).
Do NOT use generic flat rates if the report indicates high material costs or extreme weather conditions that demand specialized repair.

Always base your assessment on what you actually see in the image combined with the research report context."""

# Initialize new google-genai client
_client = genai.Client(api_key=settings.gemini_api_key)
_MODEL = "gemini-3.1-flash-lite"


class GeminiAssessmentService:
    """Service for pavement condition assessment using Gemini multimodal API with fallback and caching."""

    # Simple cache to prevent calling Gemini API twice for the same request
    _last_request_key = None
    _last_response_text = None
    _last_parsed_condition = None

    @staticmethod
    def _get_cache_key(images: list, notes: str, lat: float = None, lon: float = None) -> str:
        """Generate a SHA-256 hash of images, notes, and coordinates as cache key."""
        import hashlib
        h = hashlib.sha256()
        for img in images:
            h.update(img.encode("utf-8"))
        h.update(notes.encode("utf-8"))
        if lat is not None and lon is not None:
            h.update(str(lat).encode("utf-8"))
            h.update(str(lon).encode("utf-8"))
        return h.hexdigest()

    @staticmethod
    async def _run_research_step(lat: float, lon: float) -> str:
        """Use Google Search Grounding to research the location's climate, traffic, and repair costs."""
        if lat is None or lon is None:
            return ""
        try:
            google_search_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            config = types.GenerateContentConfig(
                tools=[google_search_tool],
                temperature=0.2,
            )
            prompt = (
                f"Act as a civil engineering researcher. I am assessing pavement damage at GPS coordinates: {lat}, {lon}. "
                "Search the web to determine the geographical region. Then, provide a brief research report including: "
                "1. The local climate and weather patterns (e.g., heavy rain, freeze-thaw cycles) that affect road degradation. "
                "2. Typical traffic density or road usage in this general area. "
                "3. Any historical road damage patterns common in this region. "
                "4. An estimate of local construction material and labor costs compared to national averages."
            )
            
            print("\n" + "="*60)
            print(">>> [GEMINI STEP 1: RESEARCH REQUEST] >>>")
            print(prompt)
            
            # Run synchronously since the python sdk may block, or use a thread pool. For now, it's fine.
            response = _client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=config,
            )
            
            print("<<< [GEMINI STEP 1: RESEARCH RESPONSE] <<<")
            print(response.text)
            print("="*60 + "\n")
            
            return response.text
        except Exception as e:
            print(f"Warning: Research step failed ({str(e)}). Proceeding without research context.")
            return ""

    @staticmethod
    def _generate_fallback_assessment(notes: str = "") -> tuple[PavementCondition, str]:
        """Generate a high-quality simulated assessment when the Gemini API is unavailable or fails."""
        notes_lower = notes.lower() if notes else ""
        
        # Heuristic determination based on inspector notes
        if any(w in notes_lower for w in ["pothole", "severe", "worst", "danger", "hazard", "high", "critical", "water", "ingress", "failure", "collapsed"]):
            severity = "HIGH"
            damage_types = ["pothole", "water_ingress", "block_cracking"]
            repair_priority = 9
            estimated_cost = 4500.0
            repair_method = "Immediate pothole excavation, base repair, and hot-mix asphalt patching."
            detailed_assessment = "[Simulated Fallback] Visual inspection indicates severe structural degradation with active potholing and water pooling. Immediate excavation and resurfacing required to prevent further subgrade damage."
        elif any(w in notes_lower for w in ["crack", "medium", "moderate", "rutting", "raveling", "wear", "bleeding", "patching"]):
            severity = "MEDIUM"
            damage_types = ["hairline_cracks", "block_cracking", "surface_wear"]
            repair_priority = 5
            estimated_cost = 1200.0
            repair_method = "Crack sealing and localized skin patching."
            detailed_assessment = "[Simulated Fallback] Pavement shows moderate cracking and early signs of surface wear. Recommend sealing active cracks to prevent water penetration and pavement shifting."
        else:
            # Default fallback (e.g. unknown)
            severity = "MEDIUM"
            damage_types = ["pothole", "surface_wear"]
            repair_priority = 5
            estimated_cost = 800.0
            repair_method = "Localized pothole patching."
            detailed_assessment = "[Simulated Fallback] Visual inspection indicates potholing and surface wear. Recommend localized patching."

        condition = PavementCondition(
            severity_level=severity,
            damage_types=damage_types,
            repair_priority=repair_priority,
            estimated_cost=estimated_cost,
            estimated_cost_inr=round(estimated_cost * 83.5, 2),
            repair_method=repair_method,
            detailed_assessment=detailed_assessment,
        )
        
        raw_dict = {
            "severity_level": severity,
            "damage_types": damage_types,
            "repair_priority": repair_priority,
            "estimated_cost": estimated_cost,
            "repair_method": repair_method,
            "detailed_assessment": detailed_assessment
        }
        raw_json = json.dumps(raw_dict, indent=2)
        
        return condition, raw_json

    @staticmethod
    async def assess_pavement(images: list, notes: str = "", lat: float = None, lon: float = None) -> PavementCondition:
        """
        Assess pavement condition from base64 images using Gemini Vision API.
        Falls back to a simulated assessment if the Gemini API call fails.

        Args:
            images: List of base64-encoded image strings
            notes: Optional inspection notes from inspector
            lat: Optional GPS latitude
            lon: Optional GPS longitude

        Returns:
            PavementCondition object with AI assessment results
        """
        cache_key = GeminiAssessmentService._get_cache_key(images, notes, lat, lon)
        if (GeminiAssessmentService._last_request_key == cache_key and 
                GeminiAssessmentService._last_parsed_condition is not None):
            return GeminiAssessmentService._last_parsed_condition

        try:
            # Step 1: Research Phase
            research_report = await GeminiAssessmentService._run_research_step(lat, lon)
            
            # Step 2: Assessment Phase
            contents = _build_contents(images, notes, research_report)
            
            print("\n" + "="*60)
            print(">>> [GEMINI STEP 2: ASSESSMENT REQUEST] >>>")
            print("SYSTEM_INSTRUCTION:\n" + SYSTEM_INSTRUCTION)
            print("\nPROMPT:\n" + str(contents[0]))
            
            response = _client.models.generate_content(
                model=_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
            
            print("\n<<< [GEMINI STEP 2: ASSESSMENT RESPONSE] <<<")
            print(response.text)
            print("="*60 + "\n")
            
            condition = _parse_response(response.text)
            
            # Cache the successful result
            GeminiAssessmentService._last_request_key = cache_key
            GeminiAssessmentService._last_response_text = response.text
            GeminiAssessmentService._last_parsed_condition = condition
            
            return condition
        except Exception as e:
            # Print warning/error to logs
            print(f"Warning: Gemini API call failed ({str(e)}). Falling back to simulated assessment.")
            
            # Generate fallback assessment
            condition, raw_json = GeminiAssessmentService._generate_fallback_assessment(notes)
            
            # Cache the fallback result
            GeminiAssessmentService._last_request_key = cache_key
            GeminiAssessmentService._last_response_text = raw_json
            GeminiAssessmentService._last_parsed_condition = condition
            
            return condition

    @staticmethod
    async def get_raw_assessment(images: list, notes: str = "", lat: float = None, lon: float = None) -> str:
        """Get raw JSON assessment text from Gemini for logging/storage."""
        cache_key = GeminiAssessmentService._get_cache_key(images, notes, lat, lon)
        if (GeminiAssessmentService._last_request_key == cache_key and 
                GeminiAssessmentService._last_response_text is not None):
            return GeminiAssessmentService._last_response_text

        try:
            research_report = await GeminiAssessmentService._run_research_step(lat, lon)
            contents = _build_contents(images, notes, research_report)
            response = _client.models.generate_content(
                model=_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
            
            # Cache the successful result
            GeminiAssessmentService._last_request_key = cache_key
            GeminiAssessmentService._last_response_text = response.text
            
            # Try parsing to also cache parsed condition
            try:
                condition = _parse_response(response.text)
                GeminiAssessmentService._last_parsed_condition = condition
            except Exception:
                pass
                
            return response.text
        except Exception as e:
            print(f"Warning: Gemini API call for raw assessment failed ({str(e)}). Falling back to simulated JSON.")
            
            # Generate fallback assessment
            condition, raw_json = GeminiAssessmentService._generate_fallback_assessment(notes)
            
            # Cache the fallback result
            GeminiAssessmentService._last_request_key = cache_key
            GeminiAssessmentService._last_response_text = raw_json
            GeminiAssessmentService._last_parsed_condition = condition
            
            return raw_json


def _build_contents(images: list, notes: str, research_report: str = "") -> list:
    """
    Build multimodal content list for Gemini — sends actual image data.
    Each base64 image is sent as an inline image part.
    """
    parts = []

    prompt_text = "Please assess the pavement condition in the following image(s)."
    if notes:
        prompt_text += f'\n\nInspector field notes: "{notes}"'
    if research_report:
        prompt_text += f'\n\nContextual Research Report (Factor this into your severity and cost calculation):\n{research_report}'
        
    prompt_text += "\n\nProvide your assessment as JSON."
    parts.append(prompt_text)

    for img_b64 in images:
        # Detect MIME type from base64 header
        mime_type = "image/jpeg"
        if img_b64.startswith("iVBOR"):
            mime_type = "image/png"
        elif img_b64.startswith("R0lGOD"):
            mime_type = "image/gif"
        elif img_b64.startswith("UklGR"):
            mime_type = "image/webp"

        parts.append(
            types.Part.from_bytes(
                data=base64.b64decode(img_b64),
                mime_type=mime_type,
            )
        )

    return parts


def _parse_response(response_text: str) -> PavementCondition:
    """Parse Gemini JSON response into a PavementCondition object."""
    try:
        cleaned = response_text.strip()
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned).strip()

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
        return PavementCondition(
            severity_level="MEDIUM",
            damage_types=["surface_wear"],
            repair_priority=5,
            estimated_cost=500.0,
            repair_method="Unable to parse AI response. Manual inspection required.",
            detailed_assessment=f"Parse error: {str(e)[:100]}",
        )
