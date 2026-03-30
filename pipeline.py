"""
Pipeline Core — X (Structure + Pipeline Layer)
Central orchestrator for the structural intelligence system.
"""

from __future__ import annotations

import webbrowser
from pathlib import Path
import json
import time
import hashlib

from loader import load_data
from materials import recommend_material, calculate_risk_score
from explain import explain as generate_explanation
from formatter import print_report, write_json
from render_rooms import render_rooms as render_3d, generate_plotly_json


def generate_report_hash(report: dict) -> str:
    """Generate SHA256 hash of the report dictionary.
    
    Parameters
    ----------
    report : dict
        Structural analysis report dictionary
        
    Returns
    -------
    str
        SHA256 hex digest
    """
    # Use sort_keys for deterministic JSON output
    report_json = json.dumps(report, sort_keys=True, default=str)
    report_hash = hashlib.sha256(report_json.encode()).hexdigest()
    print("Report hash generated:", report_hash)
    return report_hash


def adapt_wall(wall: dict) -> dict:
    """Convert wall from input format to Y's expected format.

    Input:  {"type": "load_bearing", "length": 31}
    Output: {"load_bearing": True, "length": 31}

    Parameters
    ----------
    wall : dict
        Wall with "type" (str) and "length" (num)

    Returns
    -------
    dict
        Wall adapted for Y's functions with boolean load_bearing key
    """
    wall_type = wall.get("type", "")
    is_load_bearing = wall_type == "load_bearing"

    return {
        "load_bearing": is_load_bearing,
        "length": wall.get("length", 0),
    }


def run_pipeline(
    input_path: str | None = None,
    output_path: str = "output.json",
    render: bool = True,
    data_dict: dict | None = None,
) -> dict:
    """Execute the full structural intelligence pipeline.

    Parameters
    ----------
    input_path : str | None
        Path to JSON input file. If None, uses defaults from data.py
    output_path : str
        Path for JSON report output (default: "output.json")
    render : bool
        Whether to render 3D visualization (default: True)
    data_dict : dict | None
        Direct data dictionary (bypasses file loading)

    Returns
    -------
    dict
        The complete report with rooms, walls, and results
    """
    if data_dict is not None:
        data = data_dict
    else:
        data = load_data(input_path)
    rooms = data["rooms"]
    walls = data["walls"]

    results = []
    for wall in walls:
        adapted = adapt_wall(wall)
        
        material_options = recommend_material(adapted)
        
        top_material = material_options[0]["name"] if material_options else "Red Brick"
        
        ai_insight = generate_explanation(adapted, material_options)
        
        risk_score = calculate_risk_score(adapted, top_material)
        
        results.append({
            "wall": wall,
            "material": top_material,
            "material_options": material_options,
            "ai_insight": ai_insight,
            "risk_score": risk_score,
        })
        
    room_scores = {}
    for r in results:
        w = r["wall"]
        rid = w.get("room_id")
        if rid:
            room_scores[rid] = max(room_scores.get(rid, 0), r["risk_score"])
            
    # Generate phased Plotly JSONs
    fig_phase_1 = generate_plotly_json(rooms, results, phase="layout")
    fig_phase_2 = generate_plotly_json(rooms, results, phase="walls")
    fig_phase_3 = generate_plotly_json(rooms, results, phase="analysis")
    fig_phase_4 = generate_plotly_json(rooms, results, phase="materials")
    fig_phase_5 = generate_plotly_json(rooms, results, phase="final")
    
    phases = {
        "phase_1_layout": fig_phase_1,
        "phase_2_walls": fig_phase_2,
        "phase_3_analysis": fig_phase_3,
        "phase_4_materials": fig_phase_4,
        "phase_5_final": fig_phase_5,
    }

    report = {
        "rooms": rooms,
        "walls": walls,
        "results": results,
        "room_scores": room_scores,
        "phases": phases,
        "diagram": fig_phase_5,
    }
    
    report["report_hash"] = generate_report_hash(report)

    print_report(report)
    write_json(report, output_path)

    if render:
        render_3d(rooms)

    return report


if __name__ == "__main__":
    run_pipeline(input_path="input.json")


def generate_phases_stream(data_dict: dict):
    """Generator that yields the 5 analytical phases progressively for real-time frontend streaming."""
    rooms = data_dict.get("rooms", [])
    walls = data_dict.get("walls", [])
    
    # Phase 1: Layout (Only Room Boxes)
    fig_1 = generate_plotly_json(rooms, [], phase="layout")
    yield json.dumps({"phase": "layout", "diagram": fig_1}) + "\n"
    time.sleep(0.5)
    
    # Phase 2: Walls (Generic Walls, mapped by load_bearing)
    pseudo_results = [{"wall": w, "risk_score": 0, "material": "Unknown"} for w in walls]
    fig_2 = generate_plotly_json(rooms, pseudo_results, phase="walls")
    yield json.dumps({"phase": "walls", "diagram": fig_2}) + "\n"
    time.sleep(0.5)
    
    # Begin deep analysis
    results = []
    room_scores = {}
    
    for wall in walls:
        adapted = adapt_wall(wall)
        
        material_options = recommend_material(adapted)
        top_material = material_options[0]["name"] if material_options else "Red Brick"
        ai_insight = generate_explanation(adapted, material_options)
        risk_score = calculate_risk_score(adapted, top_material)
        
        results.append({
            "wall": wall,
            "material": top_material,
            "material_options": material_options,
            "ai_insight": ai_insight,
            "risk_score": risk_score,
        })
        
        rid = wall.get("room_id")
        if rid:
            room_scores[rid] = max(room_scores.get(rid, 0), risk_score)
            
    # Phase 3: Analysis (Apply Risk Score Coloring)
    fig_3 = generate_plotly_json(rooms, results, phase="analysis")
    yield json.dumps({"phase": "analysis", "diagram": fig_3}) + "\n"
    time.sleep(0.5)
    
    # Phase 4: Materials (Apply Material Coloring)
    fig_4 = generate_plotly_json(rooms, results, phase="materials")
    yield json.dumps({"phase": "materials", "diagram": fig_4}) + "\n"
    time.sleep(0.5)
    
    # Phase 5: Final (Full Model + Sidebar JSON Payload)
    fig_5 = generate_plotly_json(rooms, results, phase="final")
    
    report = {
        "phase": "final",
        "diagram": fig_5,
        "rooms": rooms,
        "walls": walls,
        "results": results,
        "room_scores": room_scores
    }
    
    report["report_hash"] = generate_report_hash(report)
    
    yield json.dumps(report) + "\n"
