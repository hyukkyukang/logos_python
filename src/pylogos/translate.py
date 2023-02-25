from typing import Any, Dict, Tuple

from pylogos.algorithm.MRP import MRP
from pylogos.query_graph.koutrika_query_graph import Query_graph


def translate(query_graph: Query_graph) -> Tuple[str, Dict[str, Any]]:
    return MRP()(query_graph.query_subjects[0], None, None, query_graph)

if __name__ == "__main__":
    pass