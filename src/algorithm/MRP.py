import copy
import networkx as nx
from src.query_graph.koutrika_query_graph import Node, Value, Selection, Membership, Predicate, Relation, Attribute, Transformation

IS_DEBUG = True

def label_mv(node, graph):
    """
        My assumption:
            - This function returns text to describe the projected attribute of the relation
    """
    assert(type(node) == Relation, "The input node should be a relation")
    # Get all projected values of relation
    attributes = [src for src, dst in graph.in_edges(node) if type(graph.edges[src, dst]['data']) == Membership]
    assert all([type(att) == Attribute for att in attributes]), "nodes connected to relation through membership edges should all be attributes"
    
    # Check if aggregation function is applied
    atts_labels = []
    for att in attributes:
        # Check if any incoming edges of type transformation
        agg_func = [src for src, dst in graph.in_edges(att) if type(graph.edges[src, dst]['data']) == Transformation]
        assert len(agg_func) in [0, 1], "Unexpected number of agg func to one attribute"
        att_label = f"{agg_func[0].label} {att.label}" if agg_func else att.label
        atts_labels.append(att_label)

    atts_str = ""
    if len(atts_labels) == 1:
        atts_str = atts_labels[0]
    elif len(atts_labels) == 2:
        atts_str = ' and '.join(atts_labels)
    elif len(atts_labels) > 2:
        for idx in range(len(atts_labels)):
            if idx == 0:
                atts_str += atts_labels[idx]
            elif idx + 1 < len(atts_labels):
                atts_str += f", {atts_labels[idx]}"
            else:
                atts_str += f", and {atts_labels[idx]}"
    return f"the {atts_str} of"

def label_v(graph, node):
    """
        Return text description of node's where conditions
    """
    if type(node) != Relation:
        return ""

    conditions = []
    for src, dst in graph.out_edges(node):
        edge = graph.edges[src, dst]['data']
        if type(edge) == Selection:
            for dst, dst2 in graph.out_edges(dst):
                edge2 = graph.edges[dst, dst2]['data']
                if type(edge2) == Predicate and type(dst2) == Value:
                    conditions.append(f"{dst.label} {edge2.label} {dst2.label}")

    # Check if current node has attributes and values
    return f"{' and '.join(conditions)}"


def label(graph, n1, n2=None):
    text = f" {n1.label}" if n1.label else ""
    if n2 and n1 != n2:
        # If edge (i.e. 1-hop path)
        edge = graph.edges[n1, n2]['data']

        # Add description for condition
        condition_text = label_v(graph, n1)
        if condition_text:
            if n1.label:
                text += f" for {n1.label} whose {condition_text}"
            else:
                text += f" whose {condition_text}"

        # has path label
        if edge.label:
            noun_clause_conjunction = " and that" if condition_text else " that"
            coordinating_conj = f" these" if condition_text else f""
            text += f"{noun_clause_conjunction} {edge.label}{coordinating_conj}"

    return text

def debug_print(msg):
    if not IS_DEBUG:
        return None
    print(msg)


class MRP():
    """
        Input:
            - v: node (the node being processed in each call)
            - rp: node (reference point for v)
            - u: node (the parent node of v)
            - G: graph 
            - open: list (nodes to be visited)
            - close: list (nodes already visited)
            - path: list (storing the edges between rp and v)
            - cStr: clause
        Output:
            - cStr (clause)
    """
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs) -> str:
        cStr = self._call(*args, **kwargs)
        return f"Find {cStr}."

    def _call(self, v, rp, u, g, open=[], close=[], path=[], cStr=""):
        debug_print(f"Entering node: {v.name}")
        close.append(v)

        # Save path from u (i.e. parent) to v (i.e. child)
        if u is not None and nx.has_path(g, u, v):
            path.append([u, v])
            # path.append(nx.shortest_path(g, u, v))

        # If current node is a reference point, construct cStr        
        if v in g.reference_points:
            pr = rp
            rp = v

            # Check incoming edges of v
            if any([type(g.edges[src, dst]['data']) == Membership for src, dst in g.in_edges(v)]):
                cStr += label_mv(rp, g)
                while path:
                    x, y = path.pop(-1)

                    cStr += label(g, y, x)
                    if (x == pr):
                        cStr += label(g, x)
                    # else:
                    #     cStr += ""
                
                # sStr_list = []
                # # RP has information of interest (i.e. projected attribute) and we can ask for this information and then link back to pr
                # while path:
                #     x, y = path.pop(-1)

                #     # Get edge label and add conjunction if necessary
                #     edge_label = label(g, y, x)

                #     # If x is pr, additional append label(g, x)
                #     if x == pr:
                #         cStr += edge_label + label(g, x)
                #     else:
                #         cStr += edge_label
                #     # Add description for selection (i.e. where condition) for all cases (regardless of x == pr or x != pr)
                #     sStr = label_v(g, y)
                #     if sStr: 
                #         sStr_list.append(sStr)
                # # Add conditions
                # if sStr_list:
                #     if label_v(g, v):
                #         cStr += f" for{label(g, v)} whose {' and '.join(sStr_list)}"
                #     else:    
                #         cStr += f" whose {' and '.join(sStr_list)}"
            else:
                # RP has no information of interest (i.e. projected attribute) and hence it cannot stand by itself.
                # We make the previous reference point pr to textually connect to rp
                cStr += f" for{label(g, pr)} "
                while path:
                    x, y = path.pop(0)
                    edge = g.edges[x,y]['data']
                    cStr += label(g, x, y) + label_v(g, y)

            # Clear path
            path.clear()

        # Propagate recursive call to next nodes
        for src, dst in g.out_edges(v):
            if dst not in close:
                open.append((dst, rp, v))
        
        debug_print(f"\nOpen list: {[(node[0].name, node[-1].name) for node in open]}")
        debug_print(f"path: {[(n[0].name, n[1].name) for n in path]}")
        debug_print(f"str: {cStr}\n")

        r_cStr_list = [cStr] if cStr else []
        while open:
            v, rp, u = open.pop(-1)
            r_cStr = self._call(v, rp, u, g, [], close, [n for n in path], "")
            if r_cStr:
                r_cStr_list.append(r_cStr)
        cStr = ", and also, ".join(r_cStr_list)

        debug_print(f"\nExiting node: {v.name} with cStr:{cStr}")
        return cStr

