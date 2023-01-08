import networkx as nx
from src.query_graph.koutrika_query_graph import Node, Value, Selection, Membership, Having, Predicate, Grouping, Order, Relation, Attribute, Transformation, Function

IS_DEBUG = True


def debug_print(msg):
    if not IS_DEBUG:
        return None
    print(msg)


class MRP():
    """
        MULTIPLE_REFERENCE_POINTS algorithm
        Input:
            - current_node: node (the node being processed in each call)
            - rp: node (reference point for v)
            - parent_node: node (the parent node of v)
            - query_graph: graph 
            - open: list (nodes to be visited)
            - close: list (nodes already visited)
            - path: list (storing the edges between rp and v)
            - cStr: clause
        Output:
            - cStr (clause)
    """
    def __init__(self):
        self.close = []
        self.path = []
        self.group_by_nodes = []
        self.order_by_nodes = []
        self.having_clause = []

    @property
    def has_group_by(self):
        return len(self.group_by_nodes) > 0
    
    @property
    def has_having(self):
        return len(self.having_clause) > 0
    
    @property
    def has_order_by(self):
        return len(self.order_by_nodes) > 0

    def __call__(self, *args, **kwargs) -> str:
        cStr = self._call(*args, **kwargs)

        # My logic
        # Add string for group by
        if self.has_group_by:
            # Return nodes for group by and the reference point is the same
            cStr += f", grouped by {' and '.join([node.label for node in self.group_by_nodes])}"
        # Add string for having by
        if self.has_having:
            # Return nodes for group by and the reference point is the same
            cStr += f". Consider only groups whose  {' and '.join(self.having_clause)}"
        # Add string for order by
        if self.has_order_by:
            cStr += f" order by {' and '.join([node.label for node in self.order_by_nodes])}"

        return f"Find {cStr}."

    def _call(self, current_node, rp, parent_node, query_graph, opened=[], cStr=""):
        def has_path(src: Node, dst: Node) -> bool:
            return src is not None and src != dst and nx.has_path(query_graph, src, dst)
        def has_incoming_edge(node: Node) -> bool:
            return any([type(query_graph.edges[src, dst]['data']) == Membership for src, dst in query_graph.in_edges(node)])
        def is_forward(node1: Node, node2: Node) -> bool:
            # TODO: Need to implement this
            """Return whether the edge of node1 to node2 is a forward edge"""
            assert nx.has_path(query_graph, node1, node2) or nx.has_path(query_graph, node2, node1)
            return nx.has_path(query_graph, node1, node2)
        def is_edge_to_mute(node1: Node, node2: Node) -> bool:
            # TODO: Need to implement this. (All edge should have pre-defined attribute describing whether it is to be muted or not)
            """Return whether the edge is to be muted"""
            return None
        def is_edge_for_having_clause(node1: Node, node2: Node) -> bool:
            """Return whetther the edge is constructed for having clause"""
            return type(query_graph.edges[node1, node2]['data']) == Having
        def is_edge_for_group_by_clause(node1: Node, node2: Node) -> bool:
            """Return whetther the edge is constructed for group by clause"""
            return type(query_graph.edges[node1, node2]['data']) == Grouping
        def is_edge_for_order_by_clause(node1: Node, node2: Node) -> bool:
            """Return whetther the edge is constructed for order by clause"""
            return type(query_graph.edges[node1, node2]['data']) == Order
        
        def is_node_to_mute(node: Node) -> bool:
            # TODO: Need to implement this.
            """Return whetther the node is to be muted"""
            return None
        
        debug_print(f"Entering node: {current_node.name}")
        self.close.append(current_node)

        if has_path(parent_node, current_node):
            self.path.append([parent_node, current_node])
            # path.append(nx.shortest_path(g, parent_node, current_node))
            ## if the edge is a join predicate or a join selection
            ## Then, check if path is complete (?) and start a new path

        # If current node is a reference point, construct cStr        
        if current_node in query_graph.reference_points:
            pr = rp
            rp = current_node

            # Check incoming edges of v
            if has_incoming_edge(current_node):
                # Get string for membership edge
                # label_mv should change is visited nodes
                cStr += self.label_mv(rp, query_graph) # TODO: Check MultiReferencePointsAlgorithm.class > traversePathBetweenReferencePoints(Node, Node, Node)
            while self.path:
                x, y = self.path.pop(-1)
                src_node, dst_node = (x, y) if is_forward(x, y) else (y, x)
                assert has_path(src_node, dst_node), f"Path does not exist between {src_node.name} and {dst_node.name}"
                if not is_edge_to_mute(src_node, dst_node):
                    if not has_incoming_edge(dst_node) or dst_node != pr:
                        # label_mv should change is visited nodes
                        s_tmp = self.label_v(query_graph, dst_node)
                        if s_tmp:
                            cStr += f" whose {s_tmp}"
                else:
                    raise NotImplementedError("Need to check what to do in this case")

        # Propagate recursive call to next nodes
        for src, dst in query_graph.out_edges(current_node):
            # Append to group by list
            if is_edge_for_group_by_clause(src, dst):
                self.group_by_nodes.append(dst)
            
            elif is_edge_for_order_by_clause(src, dst):
                self.order_by_nodes.append(dst)
                
            elif is_edge_for_having_clause(src, dst):
                self.having_clause.append(self.label_having(query_graph, dst))
                
            if all([dst not in self.close,
                    not is_edge_to_mute(parent_node, current_node),
                    not is_node_to_mute(dst)]):
                opened.append((dst, rp, current_node))

        debug_print(f"\nOpen list: {[(node[0].name, node[-1].name) for node in opened]}")
        debug_print(f"path: {[(n[0].name, n[1].name) for n in self.path]}")
        debug_print(f"str: {cStr}\n")

        r_cStr_list = [cStr] if cStr else []
        while opened:
            current_node, rp, parent_node = opened.pop(-1)
            r_cStr = self._call(current_node, rp, parent_node, query_graph, [], "")
            if r_cStr:
                r_cStr_list.append(r_cStr)
        cStr = ", and also, ".join(r_cStr_list)

        debug_print(f"\nExiting node: {current_node.name} with cStr:{cStr}")
        return cStr

    def get_grouping_attributes(self, graph, node):
        attributes = [dst for src, dst in graph.out_edges(node) if type(graph.edges[src, dst]['data']) == Grouping]
        
        more_than_one_hop_attributes = []
        for att in attributes:
            more_than_one_hop_attributes.extend(self.get_grouping_attributes(graph, att))
        
        return attributes + more_than_one_hop_attributes


    def label_mv(self, node, graph):
        """This function returns text description of the projected attributes of a relation
        :param node: node of a query graph
        :type node: Node
        :param graph: query graph
        :type graph: Graph
        :return: description of the projected attribute of the relation
        :rtype: str
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
            self.close.append(att)
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
        return f"the {atts_str} of {node}"

    def label_v(self, graph, node):
        """Return text description of node's where conditions
        :param graph: query graph
        :type graph: Graph
        :param node: node of a query graph
        :type node: Node
        :return: description of the where conditions of the node
        :rtype: str
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
    
    def label_having(self, graph, node):
        """Return text description of node's having conditions
        :param graph: query graph
        :type graph: Graph
        :param node: node of a query graph
        :type node: Node
        :return: description of the where conditions of the node
        :rtype: str
        """
        conditions = []
        for src, dst in graph.out_edges(node):
            edge = graph.edges[src, dst]['data']
            if type(edge) == Transformation and type(dst) == Function and type(src) == Attribute:
                for dst, dst2 in graph.out_edges(dst):
                    edge2 = graph.edges[dst, dst2]['data']
                    if type(edge2) == Predicate and type(dst2) == Value:
                        conditions.append(f"{dst.label} {src.label} {edge2.label} {dst2.label}")

        # Check if current node has attributes and values
        return f"{' and '.join(conditions)}"