from typing import List, Tuple

from src.query_graph.koutrika_query_graph import Query_graph


class StringBuilder():
    def __init__(self, is_nested=False):
        self.is_nested: bool = is_nested
        self.projection: List[Tuple(str,str, str)] = []
        self.selection: List[Tuple(str, str, str, str, str)] = []
        self.grouping: List[str] = []
        self.having: List[str] = []
        self.ordering: List[str] = []
        self.sentences: List[str] = []
        self.join_conditions: List[Tuple(str, str, str, str, bool)] = []
    
    @property
    def text(self):
        pass

    def to_text(self):
        text = ""
        target_relation = None
        while self.projection or self.selection:
            # Get target relation
            if self.projection:
                target_relation = self.projection[0][0]
            else:
                target_relation = self.selection[0][0]

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
                ttmp = ""
                for i, t in enumerate(texts):
                    if i == 0:
                        ttmp += f"{t}"
                    # If item more than two
                    elif len(texts) > 1:
                        # If last item
                        if i == len(texts) - 1:
                            # If has two items
                            if len(texts) == 2:
                                ttmp += f" and {t}"
                            # If item more than three
                            else:
                                ttmp += f", and {t}"
                        # Use commna
                        else:
                            ttmp += f", {t}"
                if ttmp:
                    text = ", ".join(_ for _ in [text, f"{ttmp} of {target_relation}"] if _)
                self.projection = tmp

            # Get join_conditions for target relation
            if self.join_conditions:
                # Begin sentence
                if not text:
                    text = f"{target_relation}"
                tmp = []
                texts = []
                for reference_point, rel1, edge, rel2, has_incoming_edge in self.join_conditions:
                    # Append to the string of reference point if it has no incoming edge
                    if not has_incoming_edge and reference_point == target_relation:
                        texts.append(" ".join(_ for _ in [edge, rel2] if _))
                    # Append to the string of rel1 if it has incoming edge
                    elif has_incoming_edge and rel1 == target_relation:
                        texts.append(" ".join(_ for _ in [edge, rel2] if _))
                    else:
                        tmp.append((reference_point, rel1, edge, rel2, has_incoming_edge))
                if texts:
                    join_flag = True
                    text += f" in which {target_relation} "
                text += " ".join(texts)
                self.join_conditions = tmp

            # Get selection for target relation
            if self.selection:
                # Begin sentence
                if not text:
                    text = f"{target_relation}"
                
                tmp = []
                texts = []
                # Handle selection for join relations first
                for rp, rel, att, op, val in self.selection:
                    if rp != rel and rp == target_relation:
                        if rel == "":
                            texts.append(f"{att} {op} {val}")
                        else:
                            texts.append(f"{att} of {rel} {op} {val}")
                    else:
                        tmp.append((rp, rel, att, op, val))
                if texts:
                    if join_flag:
                        text += " and "
                    else:
                        text += " where "
                    text += " and ".join(texts)
                    join_flag = True
                self.selection = tmp                
                
                tmp = []
                texts = []
                for rp, rel, att, op, val in self.selection:
                    if rp == target_relation:
                        # use {att} of {rel} if there is rel, otherwise use {att}
                        if rel == "":
                            texts.append(f"{att} {op} {val}")
                        else:
                            texts.append(f"{att} of {rel} {op} {val}")
                    else:
                        tmp.append((rp, rel, att, op, val))
                if texts:
                    if join_flag:
                        text += " and "
                    else:
                        text += " where "
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
    
    def add_selection(self, reference_point: str, relation: str, attribute: str, op: str, operand: str) -> None:
        self.selection.append((reference_point, relation, attribute, op, operand))

    def add_join_conditions(self, reference_point: str, relation1: str, edge: str, relation2: str, has_incoming_edge: bool) -> None:
        self.join_conditions.append((reference_point, relation1, edge, relation2, has_incoming_edge))

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

    def add(self, string_builder) -> None:
        self.projection.extend(string_builder.projection)
        self.selection.extend(string_builder.selection)
        self.join_conditions.extend(string_builder.join_conditions)
        return self