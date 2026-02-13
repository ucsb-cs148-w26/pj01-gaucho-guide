import re
import json


# -------------------------------------------------------------------------
# 1. API Interaction Layer
# -------------------------------------------------------------------------
def fetch_course_info(dept, course_num, api_key="YOUR_API_KEY"):
    """
    Mock function to simulate fetching from UCSB Curriculum API.
    In production, replace this with a real requests.get() call to:
    https://api.ucsb.edu/academics/curriculums/v3/classes/search
    """
    # SIMULATED RESPONSE for demonstration
    # Real UCSB API returns prerequisites often as unstructured text strings.
    mock_db = {
        "CMPSC 130A": "CMPSC 40 and CMPSC 32",
        "CMPSC 130B": "CMPSC 130A",
        "CMPSC 40": "MATH 4A and (CMPSC 16 or CMPSC 24)",
        "CMPSC 32": "CMPSC 24",
        "CMPSC 24": "CMPSC 16",
        "CMPSC 16": "MATH 3A or MATH 34A",
        "MATH 4A": "MATH 3B",
        "MATH 3B": "MATH 3A",
        "MATH 3A": "",
        "MATH 34A": ""
    }

    course_id = f"{dept} {course_num}"
    prereq_str = mock_db.get(course_id, "")

    return {
        "courseId": course_id,
        "title": "Data Structures and Algorithms",
        "prerequisites": prereq_str
    }


# -------------------------------------------------------------------------
# 2. Parsing Logic (The "Hard" Part)
# -------------------------------------------------------------------------
def parse_prerequisites(prereq_text):
    """
    Parses UCSB's complex prerequisite strings into a list of dependencies.
    Handles basic 'AND' logic and simplified 'OR' logic.
    """
    if not prereq_text:
        return []

    # clean up the text: remove parenthesis for simpler parsing in this basic version
    # (A robust version would build an Abstract Syntax Tree for nested logic)
    clean_text = prereq_text.replace("(", "").replace(")", "")

    # Split by AND to get required groups
    # We treat 'OR' as valid alternate paths, but for a dependency graph,
    # we usually want to show ALL possible predecessors.
    # Splitting by 'and' separates distinct requirements.
    requirements = re.split(r'\s+and\s+', clean_text, flags=re.IGNORECASE)

    dependencies = []

    for req in requirements:
        # If there is an OR, it means any of these satisfy the req.
        # We will add them all as edges but maybe mark them differently in a V2.
        options = re.split(r'\s+or\s+', req, flags=re.IGNORECASE)
        for opt in options:
            opt = opt.strip()
            # extract Course Dept and Number (e.g., "CMPSC 16")
            match = re.search(r'([A-Z]+)\s+(\d+[A-Z]?)', opt)
            if match:
                dependencies.append(f"{match.group(1)} {match.group(2)}")

    return dependencies


# -------------------------------------------------------------------------
# 3. Graph Builder
# -------------------------------------------------------------------------
def build_dependency_graph(target_dept, target_num, depth=3):
    """
    Recursively builds a graph dictionary starting from a target course.
    """
    graph = {}  # Format: { "Course": ["Prereq1", "Prereq2"] }
    visited = set()

    def traverse(dept, num, current_depth):
        course_id = f"{dept} {num}"

        if current_depth == 0 or course_id in visited:
            return
        visited.add(course_id)

        data = fetch_course_info(dept, num)
        prereqs = parse_prerequisites(data['prerequisites'])

        graph[course_id] = prereqs

        for p in prereqs:
            try:
                p_dept, p_num = p.split(" ")
                traverse(p_dept, p_num, current_depth - 1)
            except ValueError:
                continue  # Skip malformed course codes

    traverse(target_dept, target_num, depth)
    return graph


# -------------------------------------------------------------------------
# 4. Mermaid Generator
# -------------------------------------------------------------------------
def generate_mermaid_script(graph, direction="BT"):
    """
    Generates Mermaid syntax.
    direction: BT (Bottom-Top) usually looks best for prereq trees.
    """
    lines = [f"graph {direction}"]

    # Define styles
    lines.append("    classDef course fill:#f9f,stroke:#333,stroke-width:2px;")
    lines.append("    classDef target fill:#bbf,stroke:#333,stroke-width:4px;")

    for course, prereqs in graph.items():
        # Sanitize IDs for Mermaid (remove spaces)
        node_id = course.replace(" ", "")

        lines.append(f'    {node_id}["{course}"]')

        if not prereqs:
            # It's a leaf node (base course)
            pass

        for p in prereqs:
            p_id = p.replace(" ", "")
            # Edge: Prereq --> Course
            lines.append(f"    {p_id} --> {node_id}")

    return "\n".join(lines)


# -------------------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # Example: Generate graph for CMPSC 130A
    target_dept = "CMPSC"
    target_num = "130A"

    print(f"Fetching prerequisite graph for {target_dept} {target_num}...\n")

    course_graph = build_dependency_graph(target_dept, target_num)
    mermaid_output = generate_mermaid_script(course_graph)

    print("--- Mermaid Output ---")
    print(mermaid_output)
    print("----------------------")
    print("\nCopy the output above and paste it into https://mermaid.live")