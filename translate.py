from src.algorithm.MRP import MRP
from src.query_graph.koutrika_query_graph import Query_graph


def translate(query_graph: Query_graph) -> str:
    mrp = MRP
    translated_nl = mrp(query_graph.query_subjects[0], None, None, query_graph.simplified_graph)
    return translated_nl

if __name__ == "__main__":
    pass