# model/views.py  (replace safe_route function with this)
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils.crime_loader import load_crime_data
from .utils.crime_scoring import summarize_crime_for_segment
from .utils.osrm_client import get_osrm_edges
from .utils.safety_astar import safe_a_star
from .utils.safety_graph import RoadGraph, haversine


@api_view(["GET"])
def safe_route(request):
    start_lat = float(request.GET.get("start_lat"))
    start_lon = float(request.GET.get("start_lon"))
    end_lat = float(request.GET.get("end_lat"))
    end_lon = float(request.GET.get("end_lon"))

    crime_df = load_crime_data()

    start_node, goal_node, edges = get_osrm_edges(
        start_lat, start_lon, end_lat, end_lon
    )

    original_coords = []
    for a, b in edges:
        if not original_coords:
            original_coords.append([a[0], a[1]])
        original_coords.append([b[0], b[1]])

    graph = RoadGraph()
    for a, b in edges:
        graph.add_edge(a, b)

    segment_risks = []
    total_distance = 0.0

    for a, b in edges:
        r, exp = summarize_crime_for_segment(a, b, crime_df)
        graph.set_risk(a, b, r)

        segment_risks.append({
            "segment": [[a[0], a[1]], [b[0], b[1]]],
            "risk": r,
            "explanation": exp,
        })

        total_distance += haversine(a[0], a[1], b[0], b[1])

    safe_path_nodes = safe_a_star(graph, start_node, goal_node)
    safe_path = [[p[0], p[1]] for p in safe_path_nodes]

    avg_risk = (
        float(sum(item["risk"] for item in segment_risks) / len(segment_risks))
        if segment_risks else 0.0
    )

    return Response({
        "original_route": original_coords,
        "segment_risks": segment_risks,
        "safe_path": safe_path,
        "distance_meters": total_distance,
        "avg_risk": avg_risk,
        "nodes": len(graph.edges),
        "segments": len(edges),
    })

