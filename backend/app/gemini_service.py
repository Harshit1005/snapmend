"""Gemini API service for pavement condition assessment using real multimodal image input."""
import asyncio
import base64
import json
import re
from google import genai
from google.genai import types
from app.config import settings
from app.models import PavementCondition

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
  "detailed_assessment": "2-3 sentence description of observed damage, explicitly justifying the severity and cost based on the provided geographical research context.",
  "detected_distresses": [
    {
      "type": "pothole|cracking|rutting|raveling|etc",
      "severity": "LOW|MEDIUM|HIGH",
      "box_2d": [ymin, xmin, ymax, xmax],
      "confidence": <float 0-1>,
      "estimated_dimensions": {
        "length_m": <float>,
        "width_m": <float>,
        "depth_cm": <float>
      }
    }
  ],
  "cost_breakdown": {
    "materials": <float in USD>,
    "labor": <float in USD>,
    "machinery": <float in USD>,
    "total": <float in USD>
  },
  "engineering_justification": {
    "observed_defects": "engineering analysis of visual defects",
    "base_failure_risk": "detailed base failure risk assessment",
    "traffic_impact": "detailed traffic and safety impact assessment"
  },
  "step_by_step_plan": [
    "Step 1: Description",
    "Step 2: Description"
  ]
}

CRITICAL BOX DRAWING INSTRUCTION:
For "box_2d", you MUST detect the bounding boxes of the visible road distresses (especially potholes, cracking, and depressions). 
The coordinates [ymin, xmin, ymax, xmax] MUST be integer values normalized to the range [0, 1000] relative to the image borders (where [0, 0] is the top-left and [1000, 1000] is the bottom-right). 
For example, a pothole spanning the center-bottom of the image could have the box: [550, 250, 900, 750].
Do not output bounding boxes that are [0, 0, 1000, 1000] unless the damage literally covers the entire image. Be as precise as possible.

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
_MODEL = "gemini-2.5-flash"


class GeminiAssessmentService:
    """Service for pavement condition assessment using Gemini multimodal API."""

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
            
            # Wrap blocking sync call in asyncio.to_thread
            response = await asyncio.to_thread(
                _client.models.generate_content,
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
        
        # Parse depth from notes if available
        import re
        depth_cm = 5.0
        inch_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|inches|in)\b', notes_lower)
        cm_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:cm|centimeter|centimeters)\b', notes_lower)
        
        if inch_match:
            depth_cm = round(float(inch_match.group(1)) * 2.54, 1)
        elif cm_match:
            depth_cm = float(cm_match.group(1))
            
        # Determine if it is a severe condition
        # If user specified depth >= 8cm (~3 inches), or mentioned critical words
        is_severe = (depth_cm >= 8.0) or any(w in notes_lower for w in [
            "severe", "worst", "danger", "hazard", "high", "critical", 
            "water", "ingress", "failure", "collapsed", "deep", "crater", "flooded"
        ])
        
        if is_severe:
            severity = "HIGH"
            damage_types = ["pothole", "water_ingress", "block_cracking"]
            repair_priority = 9
            estimated_cost = 4500.0
            repair_method = "Immediate pothole excavation, base repair, and hot-mix asphalt patching."
            detailed_assessment = f"[Simulated Fallback] Visual inspection indicates severe structural degradation with active potholing and water pooling (measured depth: {depth_cm} cm). Immediate excavation and resurfacing required to prevent further subgrade damage."
            
            detected_distresses = [
                {
                    "type": "pothole",
                    "severity": "HIGH",
                    "box_2d": [150.0, 100.0, 850.0, 900.0],
                    "confidence": 0.95,
                    "estimated_dimensions": {
                        "length_m": 1.5,
                        "width_m": 1.2,
                        "depth_cm": depth_cm
                    }
                }
            ]
            cost_breakdown = {
                "materials": 2000.0,
                "labor": 1500.0,
                "machinery": 1000.0,
                "total": 4500.0
            }
            engineering_justification = {
                "observed_defects": f"Large structural pothole with deep base deformation, active water pooling, and measured depth of {depth_cm} cm.",
                "base_failure_risk": "High base failure risk due to moisture infiltration and repeated traffic load.",
                "traffic_impact": "Immediate danger to vehicle suspensions and potential motorcycle crash hazard."
            }
            step_by_step_plan = [
                "Step 1: Secure site and set up traffic safety barriers.",
                "Step 2: Drain water and excavate the pothole down to the stable sub-grade.",
                "Step 3: Compact sub-grade and apply aggregate base layer.",
                "Step 4: Pour and compact hot-mix asphalt binder and wearing courses.",
                "Step 5: Seal joints and reopen lane to traffic."
            ]
        elif any(w in notes_lower for w in ["crack", "medium", "moderate", "rutting", "raveling", "wear", "bleeding", "patching"]):
            severity = "MEDIUM"
            damage_types = ["hairline_cracks", "block_cracking", "surface_wear"]
            repair_priority = 5
            estimated_cost = 1200.0
            repair_method = "Crack sealing and localized skin patching."
            detailed_assessment = f"[Simulated Fallback] Pavement shows moderate cracking and early signs of surface wear (depth: {depth_cm} cm). Recommend sealing active cracks to prevent water penetration and pavement shifting."
            
            detected_distresses = [
                {
                    "type": "cracking",
                    "severity": "MEDIUM",
                    "box_2d": [200.0, 150.0, 600.0, 850.0],
                    "confidence": 0.88,
                    "estimated_dimensions": {
                        "length_m": 3.0,
                        "width_m": 0.05,
                        "depth_cm": depth_cm
                    }
                }
            ]
            cost_breakdown = {
                "materials": 500.0,
                "labor": 500.0,
                "machinery": 200.0,
                "total": 1200.0
            }
            engineering_justification = {
                "observed_defects": "Moderate block and alligator cracking across the wheel path.",
                "base_failure_risk": "Medium base failure risk if cracks are left unsealed before winter freeze cycles.",
                "traffic_impact": "Minor ride quality disruption; potential to develop into potholes."
            }
            step_by_step_plan = [
                "Step 1: Clean cracks using compressed air to remove debris.",
                "Step 2: Apply hot-pour rubberized asphalt crack sealant.",
                "Step 3: Overlay with localized skin patching where needed."
            ]
        else:
            # Default fallback (e.g. unknown)
            severity = "MEDIUM"
            damage_types = ["pothole", "surface_wear"]
            repair_priority = 5
            estimated_cost = 800.0
            repair_method = "Localized pothole patching."
            detailed_assessment = f"[Simulated Fallback] Visual inspection indicates potholing and surface wear (depth: {depth_cm} cm). Recommend localized patching."
            
            detected_distresses = [
                {
                    "type": "pothole",
                    "severity": "MEDIUM",
                    "box_2d": [100.0, 100.0, 900.0, 900.0],
                    "confidence": 0.80,
                    "estimated_dimensions": {
                        "length_m": 0.5,
                        "width_m": 0.5,
                        "depth_cm": depth_cm
                    }
                }
            ]
            cost_breakdown = {
                "materials": 300.0,
                "labor": 400.0,
                "machinery": 100.0,
                "total": 800.0
            }
            engineering_justification = {
                "observed_defects": "Minor surface wearing, raveling, and loss of fine aggregates.",
                "base_failure_risk": "Low risk; road base is structurally sound.",
                "traffic_impact": "No immediate traffic or safety hazard."
            }
            step_by_step_plan = [
                "Step 1: Sweep pavement clean of loose gravel.",
                "Step 2: Apply localized slurry seal coat to restore surface texture."
            ]

        condition = PavementCondition(
            severity_level=severity,
            damage_types=damage_types,
            repair_priority=repair_priority,
            estimated_cost=estimated_cost,
            estimated_cost_inr=round(estimated_cost * 83.5, 2),
            repair_method=repair_method,
            detailed_assessment=detailed_assessment,
            detected_distresses=detected_distresses,
            cost_breakdown=cost_breakdown,
            engineering_justification=engineering_justification,
            step_by_step_plan=step_by_step_plan
        )
        
        raw_dict = {
            "severity_level": severity,
            "damage_types": damage_types,
            "repair_priority": repair_priority,
            "estimated_cost": estimated_cost,
            "repair_method": repair_method,
            "detailed_assessment": detailed_assessment,
            "detected_distresses": detected_distresses,
            "cost_breakdown": cost_breakdown,
            "engineering_justification": engineering_justification,
            "step_by_step_plan": step_by_step_plan
        }
        raw_json = json.dumps(raw_dict, indent=2)
        
        return condition, raw_json

    @staticmethod
    async def assess_pavement(images: list, notes: str = "", research_report: str = "") -> PavementCondition:
        """
        Assess pavement condition from base64 images using Gemini Vision API.
        Falls back to a simulated assessment if the Gemini API call fails.

        Args:
            images: List of base64-encoded image strings
            notes: Optional inspection notes from inspector
            research_report: Optional research text from search grounding step

        Returns:
            PavementCondition object with AI assessment results
        """
        try:
            contents = _build_contents(images, notes, research_report)
            
            print("\n" + "="*60)
            print(">>> [GEMINI STEP 2: ASSESSMENT REQUEST] >>>")
            print("SYSTEM_INSTRUCTION:\n" + SYSTEM_INSTRUCTION)
            print("\nPROMPT:\n" + str(contents[0]))
            
            # Wrap blocking sync call in asyncio.to_thread
            # Enforce structured output via response_schema and limit output tokens to prevent truncate
            response = await asyncio.to_thread(
                _client.models.generate_content,
                model=_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=PavementCondition,
                    max_output_tokens=2048,
                ),
            )
            
            print("\n<<< [GEMINI STEP 2: ASSESSMENT RESPONSE] <<<")
            print(response.text)
            print("="*60 + "\n")
            
            condition = _parse_response(response.text)
            return condition
        except Exception as e:
            print(f"Warning: Gemini API call failed ({str(e)}). Falling back to simulated assessment.")
            condition, raw_json = GeminiAssessmentService._generate_fallback_assessment(notes)
            return condition

    @staticmethod
    async def get_raw_assessment(images: list, notes: str = "", research_report: str = "") -> str:
        """Get raw JSON assessment text from Gemini for logging/storage."""
        try:
            contents = _build_contents(images, notes, research_report)
            response = await asyncio.to_thread(
                _client.models.generate_content,
                model=_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=PavementCondition,
                    max_output_tokens=2048,
                ),
            )
            return response.text
        except Exception as e:
            print(f"Warning: Gemini API call for raw assessment failed ({str(e)}). Falling back to simulated JSON.")
            condition, raw_json = GeminiAssessmentService._generate_fallback_assessment(notes)
            return raw_json


def _sanitize_research_report(report: str) -> str:
    """Sanitize the research report content to mitigate indirect prompt injection."""
    if not report:
        return ""
    # Strip markdown code blocks, HTML tags, and common hijacking phrases
    sanitized = report
    sanitized = re.sub(r'```.*?```', '', sanitized, flags=re.DOTALL)
    sanitized = re.sub(r'<[^>]*>', '', sanitized)
    
    injection_phrases = [
        "ignore previous instructions",
        "ignore the above instructions",
        "ignore all instructions",
        "override all instructions",
        "you must instead",
        "instead, perform",
        "instead, print",
        "system prompt",
        "system instruction",
    ]
    for phrase in injection_phrases:
        sanitized = re.sub(re.escape(phrase), "[redacted injection hazard]", sanitized, flags=re.IGNORECASE)
    return sanitized.strip()


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
        sanitized = _sanitize_research_report(research_report)
        prompt_text += f'\n\nContextual Research Report (Factor this into your severity and cost calculation):\n{sanitized}'
        
    prompt_text += "\n\nProvide your assessment as JSON."
    parts.append(prompt_text)

    for img_b64 in images:
        # Safe MIME sniffing
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
            damage_types=data.get("damage_types", []),
            repair_priority=int(data.get("repair_priority", 5)),
            estimated_cost=float(data.get("estimated_cost", 500.0)) if data.get("estimated_cost") is not None else 500.0,
            repair_method=data.get("repair_method", "Schedule professional assessment"),
            detailed_assessment=data.get("detailed_assessment", ""),
            detected_distresses=data.get("detected_distresses", []),
            cost_breakdown=data.get("cost_breakdown"),
            engineering_justification=data.get("engineering_justification"),
            step_by_step_plan=data.get("step_by_step_plan", []),
        )
    except Exception as e:
        print(f"Warning: Failed to parse Gemini response ({str(e)}). Returning safe placeholder PavementCondition.")
        return PavementCondition(
            severity_level="MEDIUM",
            damage_types=["surface_wear"],
            repair_priority=5,
            estimated_cost=500.0,
            repair_method="Unable to parse AI response. Manual inspection required.",
            detailed_assessment=f"Parse error: {str(e)[:100]}",
            detected_distresses=[],
            step_by_step_plan=[],
        )
