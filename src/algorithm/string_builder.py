from typing import List, Tuple

from src.query_graph.koutrika_query_graph import Query_graph


class StringBuilder():
    def __init__(self, is_nested=False):
        self.is_nested: bool = is_nested
        self.projection: List[Tuple(str,str, str)] = []
        self.selection: List[Tuple(str, str, str, str)] = []
        self.grouping: List[str] = []
        self.having: List[str] = []
        self.ordering: List[str] = []
        self.sentences: List[str] = []
        self.join_conditions: List[Tuple(str, str, str)] = []
    
    @property
    def text(self):
        pass
    
    def to_text(self):
        text = ""
        target_relation = None
        while self.projection:
            # Get target relation
            if not target_relation:
                relation, att, agg = self.projection[0]
                target_relation = relation
        
            # Flags
            join_flag = False
        
            # Get projections for target relation
            if self.projection:
                tmp = []
                texts = []
                for rel, att, agg in self.projection:
                    if rel == target_relation:
                        # To string
                        if agg:
                            texts.append(f"{agg} {att}")
                        else:
                            texts.append(f"{att}")
                    else:
                        tmp.append((rel, att, agg))
                
                # Natural join
                for i, t in enumerate(texts):
                    if i == 0:
                        text += f"{t}"
                    # If item more than two
                    elif len(texts) > 1:
                        # If last item
                        if i == len(texts) - 1:
                            # If has two items
                            if len(texts) == 2:
                                text += f" and {t}"
                            # If item more than three
                            else:
                                text += f", and {t}"
                        # Use commna
                        else:
                            text += f", {t}"
                        
                if texts:
                    text += f" of {target_relation}"
                self.projection = tmp
            
            # Get join_conditions for target relation
            if self.join_conditions:
                tmp = []
                texts = []
                for rel1, edge, rel2 in self.join_conditions:
                    if rel1 == target_relation:
                        texts.append(" ".join(_ for _ in [edge, rel2] if _))
                    else:
                        tmp.append((rel1, edge, rel2))
                if texts:
                    join_flag = True
                    text += f" in which {target_relation} "
                text += " ".join(texts)
                self.join_conditions = tmp
        
            # Get selection for target relation
            if self.selection:
                tmp = []
                if join_flag:
                    text += " and "
                else:
                    text += " where "
                texts = []
                for rel, att, op, val in self.selection:
                    if rel == target_relation:
                        texts.append(f"{att} of {rel} {op} {val}")
                    else:
                        tmp.append((rel, att, op, val))
                text += " and ".join(texts)
                self.selection = tmp

        if self.sentences:
            text = ", and ".join(_ for _ in [text] + self.sentences if _)
        return text

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
    def add_projection(self, relation: str, attribute: str, agg_func: str) -> None:
        self.projection.append((relation, attribute, agg_func))
    
    def add_selection(self, relation: str, attribute: str, op: str, operand: str) -> None:
        self.selection.append((relation, attribute, op, operand))
    
    def add_join_conditions(self, relation1: str, edge: str, relation2: str) -> None:
        self.join_conditions.append((relation1, edge, relation2))
    
    def add_grouping(self, phrase: str) -> None:
        pass
    
    def add_having(self, phrase: str) -> None:
        pass
    
    def add_ordering(self, phrase: str) -> None:
        pass

    # others
    def set_nested(self, phrase: str) -> None:
        pass

    def add_sentence(self, sentence: str) -> str:
        self.sentences.append(sentence)

    def combine(self, string_builder) -> None:
        self.projection.extend(string_builder.projection)
        self.selection.extend(string_builder.selection)
        return self