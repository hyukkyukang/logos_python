from typing import List

from src.query_graph.koutrika_query_graph import Query_graph


class StringBuilder():
    def __init__(self, is_nested=False):
        self.is_nested: bool = is_nested
        self.projection: List[Query_graph] = []
        self.selection: List[Query_graph] = []
        self.grouping: List[Query_graph] = []
        self.having: List[Query_graph] = []
        self.ordering: List[Query_graph] = []
    
    @property
    def text(self):
        pass
    
    def to_text(self):
        pass
    
    # Converting to text
    def projection_to_text(self) -> str:
        pass

    def selection_to_text(self) -> str:
        pass

    def grouping_to_text(self) -> str:
        pass

    def having_to_text(self) -> str:
        pass
    
    def ordering_to_text(self) -> str:
        pass

    # Add sub-graphs
    def add_projection(self, sub_graph: Query_graph) -> None:
        pass
    
    def add_selection(self, sub_graph: Query_graph) -> None:
        pass
    
    def add_grouping(self, sub_graph: Query_graph) -> None:
        pass
    
    def add_having(self, sub_graph: Query_graph) -> None:
        pass
    
    def add_ordering(self, sub_graph: Query_graph) -> None:
        pass

    # others
    def set_nested(self, sub_graph: Query_graph) -> None:
        pass
    
