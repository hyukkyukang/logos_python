import networkx as nx

from src.algorithm.string_builder import StringBuilder
from src.query_graph.koutrika_query_graph import (Attribute, Function,
                                                  Grouping, Having, Membership,
                                                  Node, Order, Predicate,
                                                  Query_graph, Relation,
                                                  Selection, Transformation,
                                                  Value)

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
        self.visited_nodes = set()
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
        string_builder = self._call(*args, **kwargs)
        cStr = f"{string_builder.to_text()}"

        # My logic
        # Add string for group by
        if self.has_group_by:
            # Return nodes for group by and the reference point is the same
            cStr += f". Create group according to {' and '.join(self.group_by_nodes)}"
        # Add string for having by
        if self.has_having:
            # Return nodes for group by and the reference point is the same
            cStr += f". Consider only groups whose  {' and '.join(self.having_clause)}"
        # Add string for order by
        if self.has_order_by:
            cStr += f" order by {' and '.join([node.label for node in self.order_by_nodes])}"

        return f"Find {cStr}."

    def _call(self, current_node, current_reference_point, parent_node, query_graph, opened=[], cStr=""):
        def has_path(src: Node, dst: Node) -> bool:
            return nx.has_path(query_graph, src, dst)
        def has_incoming_edge(node: Node) -> bool:
            return any([type(query_graph.edges[src, dst]['data']) == Membership for src, dst in query_graph.in_edges(node)])
        def is_edge_for_having_clause(node1: Node, node2: Node) -> bool:
            """Return whetther the edge is constructed for having clause"""
            return type(query_graph.edges[node1, node2]['data']) == Having
        def is_edge_for_group_by_clause(node1: Node, node2: Node) -> bool:
            """Return whetther the edge is constructed for group by clause"""
            return type(query_graph.edges[node1, node2]['data']) == Grouping
        def is_edge_for_order_by_clause(node1: Node, node2: Node) -> bool:
            """Return whetther the edge is constructed for order by clause"""
            return type(query_graph.edges[node1, node2]['data']) == Order
        def get_non_visited_outgoing_nodes(node: Node):
            return [dst for _, dst in query_graph.out_edges(node) if dst not in self.visited_nodes]
        def get_next_non_visited_relation(node: Node):
            dst_nodes = get_non_visited_outgoing_nodes(node)
            assert len(dst_nodes) < 2, f"there should be only one out going node, but found {len(dst_nodes)}"
            dst_node = dst_nodes[0] if dst_nodes else None
            # Return relation node
            if type(dst_node) == Relation or dst_node is None:
                return dst_node
            return get_next_non_visited_relation(dst_node)

        # Check if input node is valid
        # assert type(current_node) == Relation, f"Input node should be a relation, not {type(current_node)}"
        if parent_node:
            assert has_path(parent_node, current_node), f"Current node {current_node} is not reachable from Parent node {parent_node}"

        debug_print(f"Entering node: {current_node.name}")
        return_info = {
            "projection": False,
            "condition": False
        } 
        # Set visited 
        self.visited_nodes.add(current_node)
        string_builder = StringBuilder()
        
        # Save into the path
        if parent_node:
            self.path.append([parent_node, current_node])

        # Construct a description if the current node is a reference point
        if current_node in query_graph.reference_points:
            # Create description for projection if there is a incoming edges
            if has_incoming_edge(current_node):
                string_builder.combine(self.label_mv(current_node, current_node, query_graph))

            while self.path:
                # Pop two nodes from the path.
                #   If the current node has incoming edges, we generate the string from the current node to the reference point
                #   If the current node has no incoming edges, we generate the string from the reference point to the current node
                if has_incoming_edge(current_node):
                    dst_node, src_node = self.path.pop(-1)
                else:
                    src_node, dst_node = self.path.pop(0)
                assert has_path(src_node, dst_node) or has_path(dst_node, src_node), f"Path does not exist between {src_node.name} and {dst_node.name}"
                # Get the edge description
                edge_desc = self.label_edge(src_node, dst_node, query_graph)
                # Get the node description.
                #   If the node is the visited reference point, don't generate the predicate description
                #   Else generate the description with the predicate
                if dst_node != current_reference_point:
                    dst_string_builder = self.label_v(query_graph, current_node if has_incoming_edge(current_node) else current_reference_point, dst_node)
                    string_builder.combine(dst_string_builder)
                    
                dst_desc = self.label_node(dst_node)
                # if has_incoming_edge(current_node) and dst_node == current_reference_point:
                #     dst_desc = self.label_node(dst_node)
                # else:
                #     dst_string_builder = self.label_v(query_graph, dst_node)
                #     dst_desc = dst_desc.to_text()

                # Concatenate the description
                string_builder.add_join_conditions(current_reference_point.label, current_node.label, edge_desc, dst_desc, has_incoming_edge(current_node))

        # State change for reference point
        next_referece_point = current_node if current_node in query_graph.reference_points else current_reference_point

        # Propagate recursive call to next nodes
        for dst in get_non_visited_outgoing_nodes(current_node):
            # Append to group by list
            if is_edge_for_group_by_clause(current_node, dst):
                self.visited_nodes.add(dst)
                self.group_by_nodes.append(f"{dst.label} of {current_node.label}")

            elif is_edge_for_order_by_clause(current_node, dst):
                self.visited_nodes.add(dst)
                self.order_by_nodes.append(f"{dst.label} of {current_node.label}")

            elif is_edge_for_having_clause(current_node, dst):
                self.visited_nodes.add(dst)
                self.having_clause.append(self.label_having(query_graph, dst))
                
            if dst not in self.visited_nodes:
                opened.append((dst, next_referece_point, current_node))
            
            # Is selection and non visited relation
            elif type(query_graph.get_edge(current_node, dst)) == Selection:
                next_relation_node = get_next_non_visited_relation(dst)
                if next_relation_node:
                    opened.append((next_relation_node, next_referece_point, current_node))

        while opened:
            pop_current_node, pop_referece_point, pop_parent_node = opened.pop(-1)
            # returned_string = self._call(pop_current_node, pop_referece_point, pop_parent_node, query_graph, [], "")
            tmp = self._call(pop_current_node, pop_referece_point, pop_parent_node, query_graph, [], "")
            string_builder.combine(tmp)
            # if returned_string:
            #     string_builder.add_sentence(returned_string)

        debug_print(f"\nExiting node: {current_node.name} with cStr:{cStr}")
        return string_builder
        # return string_builder.to_text()


    def get_grouping_attributes(self, graph, node):
        attributes = [dst for src, dst in graph.out_edges(node) if type(graph.edges[src, dst]['data']) == Grouping]
        
        more_than_one_hop_attributes = []
        for att in attributes:
            more_than_one_hop_attributes.extend(self.get_grouping_attributes(graph, att))
        
        return attributes + more_than_one_hop_attributes

    def label_node(self, node) -> str:
        return node.label
    
    def label_edge(self, src_node: Node, dst_node: Node, query_graph: Query_graph) -> str:
        """Get the description of the edge between two nodes

        :param src_node: source node of the edge
        :type src_node: Node
        :param dst_node: destination node of the edge
        :type dst_node: Node
        :param query_graph: query graph
        :type query_graph: Query_graph
        :return: description of the edge
        :rtype: str
        """
        edge = query_graph.get_edge(src_node, dst_node)
        return edge.label
    
    def label_mv(self, node: Node, reference_point: Node, graph: Query_graph) -> str:
        """This function returns text description of the projected and selection attributes of a relation
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

        string_builder = StringBuilder()

        # Check if aggregation function is applied
        for att in attributes:
            # Check if any incoming edges of type transformation and get agg function
            incoming_nodes = [src for src, dst in graph.in_edges(att) if type(graph.edges[src, dst]['data']) == Transformation]
            assert len(incoming_nodes) in [0, 1], "Unexpected number of agg func to one attribute"
            agg_func_label = incoming_nodes[0].label if incoming_nodes else None
            # Add projection info
            string_builder.add_projection(node.label, att.label, agg_func_label)
            self.visited_nodes.add(att)

        # Check if there is any selection
        string_builder.combine(self.label_v(graph, reference_point, node))

        return string_builder

    def label_v(self, graph, reference_point, node):
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

        string_builder = StringBuilder()

        conditions = []
        for src, dst in graph.out_edges(node):
            edge = graph.edges[src, dst]['data']
            if type(edge) == Selection:
                for dst, dst2 in graph.out_edges(dst):
                    edge2 = graph.edges[dst, dst2]['data']
                    if type(edge2) == Predicate:
                        if type(dst2) == Value:
                            self.visited_nodes.add(dst)
                            self.visited_nodes.add(dst2)
                            string_builder.add_selection(reference_point.label, node.label, dst.label, edge2.label, dst2.label)
                        elif type(dst2) == Attribute:
                            # Get parent relations
                            self.visited_nodes.add(dst)
                            self.visited_nodes.add(dst2)
                            parent_relations = []
                            for _, node_tmp in graph.out_edges(dst2):
                                if type(node_tmp) == Relation:
                                    parent_relations.append(node_tmp)
                            assert len(parent_relations) == 1, f"Unexpected number of parent relations, {len(parent_relations)} "
                            parent_relation = parent_relations[0]
                            # If parent relation is visited, create a string for nested query. Else pass  
                            raise NotImplementedError("Nested query not implemented yet")
                            if node_tmp in self.visited_nodes:
                                # Must be correlation
                                assert edge2.label == "is", f"Bad assumption. Value is {edge2.label}"
                                assert dst.label == dst2.label, f"Bad assumption. Values are {dst.label} and {dst2.label}"
                                string_builder.add_selection(dst.label, edge2.label, dst.label)
                                # conditions.append(f"{dst.label} {edge2.label} {dst2.label} of {parent_relation.label} ({parent_relation.alias})")
                            else:
                                value_str, meta_info = self._call(parent_relation, parent_relation, parent_relation, graph, [], "")
                                conditions.append(f"{dst.label} {edge2.label} {value_str}")
                                string_builder.add_selection(dst.label, edge2.label, value_str)
                        elif type(dst2) == Function:
                            self.visited_nodes.add(dst)
                            self.visited_nodes.add(dst2)
                            # Get attribute
                            dst_lists = [n for _, n in graph.out_edges(dst2) if type(n) == Attribute]
                            assert len(dst_lists) == 1, f"Unexpected number of attirbute, {len(dst_lists)} "
                            dst3 = dst_lists[0]
                            # Get parent relations
                            parent_relations = []
                            for _, node_tmp in graph.out_edges(dst3):
                                if type(node_tmp) == Relation:
                                    parent_relations.append(node_tmp)
                            assert len(parent_relations) == 1, f"Unexpected number of parent relations, {len(parent_relations)} "
                            parent_relation = parent_relations[0]
                            raise NotImplementedError("Nested query not implemented yet")
                            # # If parent relation is visited, create a string for nested query. Else pass  
                            # if node_tmp in self.visited_nodes:
                            #     conditions.append(f"{dst.label} {edge2.label} {dst2.label} ({parent_relation.alias})")
                            # else:
                            #     value_str, meta_info = self._call(parent_relation, parent_relation, parent_relation, graph, [], "")
                                # conditions.append(f"{dst.label} {edge2.label} {value_str}")

        # Check if current node has attributes and values
        return string_builder
    
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