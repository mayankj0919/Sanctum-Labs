"""
Engineering Reasoning Engine — Y (Intelligence Layer)
Part of the AI-based Structural Intelligence System.

LLM-powered dynamic explanations with cost-strength tradeoff analysis.
"""

import os
import json
import random

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.genai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


SYSTEM_PROMPT = """You are a senior structural engineer providing AI-powered insights for a construction project.
For each wall, you must provide a structured analysis containing:
1. BEST OPTION: A clear recommendation of the top material and why it's the optimal choice.
2. FUTURE PROBLEMS: Predicted long-term risks (e.g., moisture, settlement, thermal expansion).
3. SOLUTIONS: Maintenance steps or structural enhancements to mitigate those problems.

Your response must be in valid JSON format only."""


def explain(wall: dict, materials: list) -> dict:
    """Generate structured AI insights for material recommendations.

    Returns
    -------
    dict
        A dictionary with 'recommendation', 'future_risks', and 'solutions'.
    """
    wall_type = "load-bearing" if wall.get("load_bearing", False) else "partition"
    length = wall.get("length", 0)
    
    if not materials or len(materials) == 0:
        return get_fallback_explanation(wall, "Red Brick")
    
    top_material = materials[0]["name"]
    
    try:
        return generate_llm_explanation(wall, materials)
    except Exception as e:
        print(f"AI Insight generation failed: {e}")
        return get_fallback_explanation(wall, top_material)


def generate_llm_explanation(wall: dict, materials: list) -> dict:
    """Use LLM to generate structured AI insights."""
    wall_type = "load-bearing" if wall.get("load_bearing", False) else "partition"
    length = wall.get("length", 0)
    
    materials_info = "\n".join([
        f"{m['name']} (Tradeoff Score: {m['tradeoff_score']})"
        for m in materials[:3]
    ])
    
    user_prompt = f"""Generate structural insights for a {wall_type} wall (Span: {length}m).
Materials: {materials_info}

Respond with a JSON object:
{{
  "recommendation": "Explain the best choice and why...",
  "future_risks": "Predict 1-2 long-term issues...",
  "solutions": "Provide maintenance or engineering fixes..."
}}"""
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=user_prompt,
                config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"Gemini API error: {e}")
    
    if OPENAI_AVAILABLE:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
    
    raise ValueError("No LLM API key available")


def get_fallback_explanation(wall: dict, material: str) -> dict:
    """Generate dynamic, randomized structural insights without LLM."""
    wall_type = "load-bearing" if wall.get("load_bearing", False) else "partition"
    length = wall.get("length", 0)
    
    # 1. RECOMMENDATION POOL
    recs = {
        "RCC": [
            f"RCC is designated for this {wall_type} wall to handle compressive stress across its {length}m span.",
            f"Given the load requirements, RCC provides the necessary structural rigidity to prevent axial failure.",
            f"High-density RCC ensures stability and load transfer for this primary {wall_type} element."
        ],
        "Steel Frame": [
            f"Steel framing offers the required lateral stability for this {length}m span.",
            "A structural steel frame allows for rapid construction without compromising structural integrity.",
            f"Lightweight but high-strength steel is optimal for this custom {wall_type} configuration."
        ],
        "DEFAULT": [
            f"{material} is the most balanced choice for this {wall_type} wall.",
            f"Standard {material} masonry is cost-effective for this span length.",
            f"Selected {material} provides adequate durability for this interior {wall_type} segment."
        ]
    }
    
    # 2. FUTURE RISKS POOL
    risks = {
        "RCC": [
            "Micro-cracking due to long-term concrete shrinkage.",
            "Potential carbonation of concrete reducing rebar protection.",
            "Seismic shear stress at the wall-to-ceiling interface."
        ],
        "Steel Frame": [
            "Oxidation of fasteners in high-humidity conditions.",
            "Localized thermal bridging causing surface condensation.",
            "Minor vibration transmission across the large span."
        ],
        "DEFAULT": [
            "Hairline cracks in plaster due to seasonal thermal expansion.",
            "Moisture ingress if the damp-proof course is compromised.",
            "Erosion of mortar joints over a 15-20 year period."
        ]
    }
    
    # 3. SOLUTIONS POOL
    solns = {
        "RCC": [
            "Apply high-grade waterproof coatings and monitor for settlement.",
            "Inject epoxy resin into any visible hairline cracks annually.",
            "Add fiber-reinforced plaster to improve surface tensile strength."
        ],
        "Steel Frame": [
            "Regular inspection of anti-rust coatings and joint integrity.",
            "Install high-density acoustic insulation within the frame cavity.",
            "Apply intumescent fire-redundant paint for enhanced safety."
        ],
        "DEFAULT": [
            "Use breathable masonry primer before final painting.",
            "Ensure expansion joints are placed every 6 meters to prevent cracking.",
            "Perform periodic repointing of masonry joints every decade."
        ]
    }
    
    # Dynamic Selection
    mat_key = material if material in recs else "DEFAULT"
    
    return {
        "recommendation": random.choice(recs[mat_key]),
        "future_risks": random.choice(risks[mat_key]),
        "solutions": random.choice(solns[mat_key])
    }


def explain_single(wall: dict, material: str) -> str:
    """Backward-compatible single material explanation."""
    return explain(wall, [{"name": material, "cost": 0, "strength": 0, "durability": 0, "tradeoff_score": 0}])


if __name__ == "__main__":
    test_cases = [
        ({"load_bearing": True, "length": 8}, [
            {"name": "RCC", "cost": 95, "strength": 100, "durability": 90, "tradeoff_score": 85.5},
            {"name": "Steel Frame", "cost": 100, "strength": 95, "durability": 85, "tradeoff_score": 72.0},
            {"name": "Precast Concrete Panel", "cost": 90, "strength": 85, "durability": 80, "tradeoff_score": 68.9}
        ]),
        ({"load_bearing": False, "length": 3}, [
            {"name": "Red Brick", "cost": 60, "strength": 50, "durability": 70, "tradeoff_score": 55.0},
            {"name": "Fly Ash Brick", "cost": 55, "strength": 55, "durability": 60, "tradeoff_score": 54.5},
            {"name": "Hollow Concrete Block", "cost": 70, "strength": 60, "durability": 65, "tradeoff_score": 47.8}
        ]),
    ]
    
    for wall, materials in test_cases:
        print(f"Wall: {wall}")
        print(f"Explanation: {explain(wall, materials)}\n")
