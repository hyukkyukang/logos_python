import abc
import copy
import hashlib
from enum import IntEnum

import networkx as nx

# Type definition
class OrderingType(IntEnum):
    Ascending = 0
    Descending = 1


class OperatorType(IntEnum):
    Greaterthan = 0
    Lessthan = 1
    Equal = 2
    GEq = 3
    LEq = 4
    In = 5
    NotIn = 6
    Exists = 7
    NotExists = 8
    Like = 9
    NotLike = 10
    NotEqual = 11
OperatorNames = [">", "<", "=", ">=", "<=", "In", "Not In", "Exists", "Not Exists", "Like", "Not Like", "!="]
OperatorLabels = ["is greater than", "is less than", "is", "is equal to or greater than", 
                "is equal to or less than", "not in", "exists", "not exists", "like", "not like", "not equal to"]

class FunctionType(IntEnum):
    Min =0 
    Max = 1
    Sum = 2
    Avg = 3
    Count = 4
FunctionNames = ["Min", "Max", "Sum", "Avg", "Cnt"]
FunctionLabels = ["minimum", "maximum", "sum of", "average", "number of"]


# Node
class Node(metaclass=abc.ABCMeta):
    def __init__(self, name, label=None):
        self.name = name
        self.label = name if label is None else label

    def __str__(self):
        return self.label

    def __hash__(self):
        return int(hashlib.sha256(self.signature.encode('utf-8')).hexdigest(), 16) % 10**8

    def __eq__(self, other):
        if not isinstance(other, self.__class__): 
            return False
        return self.signature == other.signature

    @property
    def signature(self):
        return self.name.lower()

class Relation(Node):
    def __init__(self, name, label=None, alias=None):
        super().__init__(name, label)
        self.alias = alias

class Attribute(Node):
    def __init__(self, name, label=None):
        super().__init__(name, label)

class Function(Node):
    """used for representing a function, an expression or a renaming operation that is applied on an attribute A or a set of attributes"""
    def __init__(self, function_type, label=None):
        super().__init__(FunctionNames[function_type], label if label else FunctionLabels[function_type])

class Value(Node):
    def __init__(self, name, label=None):
        super().__init__(name, label)

    def __hash__(self):
        return int(hashlib.sha256(self.name.lower().encode('utf-8')).hexdigest(), 16) % 10**8

    def __eq__(self, other):
        if isinstance(other, self.__class__) and (self.name == "" or other.name == ""):
            return True
        return super().__eq__(other)
    
    @property
    def signature(self):
        return "Value"

# Edge
class Edge(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    def __str__(self):
        return type(self).__name__

    def __hash__(self):
        return int(hashlib.sha256(self.signature.encode('utf-8')).hexdigest(), 16) % 10**8
        # return self.signature
        # return id(self)

    def __eq__(self, other):
        if isinstance(other, Dummy_edge):
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.signature == other.signature

    @property
    def signature(self):
        return str(self).lower()
    
    @abc.abstractmethod
    def one_hop_path_description(self, src_label, dst_label):
        pass

class Membership(Edge):
    def __init__(self, label="of"):
        super().__init__()
        self.label = label

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Join(Edge):
    """ For simplified version of query graph (with label of join conditions) """
    def __init__(self, label):
        super().__init__()
        self.label = label

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Predicate(Edge):
    """used for predicate: attribute to a single value or a set of values or an attribute
        - Selection predicate edge: if dst is a single value or a set of values
        - Join predicate edge: if dst is an attribute """
    def __init__(self, operator_id=OperatorType.Equal):
        super().__init__()
        self.op = operator_id
        self.label = OperatorLabels[self.op]

    def __str__(self):
        return OperatorNames[self.op]

    @property
    def signature(self):
        return f"{str(super().signature)}_{str(self)}".lower()

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Selection(Edge):
    """edge for relation to attribute when there is a predicate"""
    def __init__(self, label="whose"):
        super().__init__()
        self.label = label

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Transformation(Edge):
    """used for connecting an attribute A with a function f that is applied to A"""
    def __init__(self):
        super().__init__()

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Order(Edge):
    def __init__(self, label="order by"):
        super().__init__()
        self.label = label

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Grouping(Edge):
    def __init__(self, label="group by"):
        super().__init__()
        self.label = label

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Having(Edge):
    def __init__(self, label="having"):
        super().__init__()
        self.label = label

    def one_hop_path_description(self, src_label, dst_label):
        return f"{src_label} {self.label} {dst_label}"

class Dummy_edge(Edge):
    def __init__(self, label="Dummy Edge"):
        super().__init__()
        self.label = label

    def __eq__(self, other):
        return issubclass(type(other), Edge)

    def one_hop_path_description(self, src_label, dst_label):
        return ""

# Query Graph
class Query_graph(nx.DiGraph):
    def __init__(self, name="", rp_dist_threshold=4):
        super().__init__()
        self.name = name
        self._query_subjects = None
        self.reference_point_distance_threshold = rp_dist_threshold

    @property
    def leaf_relations(self):
        """ Relations that has no outgoging path to other relations """
        return [src_r for src_r in self.relations if all([not nx.has_path(self, src_r, dst_r) for dst_r in self.relations if src_r != dst_r])]

    @property
    def reference_points(self):
        """ 
        output: 
            - list of Relations
        details:
            Any relation that satisfies at least one of four conditions:
                1. RP is a primary relation with membership edges
                2. RP is a branching point, i.e., a relation that connects to more than one relation through paths directed from this relation to the other relations
                3. RP is a leaf relation, i.e., a relation with no outgoing paths to other relations on the query graph (This is for query with nesting)
                4. the minimum distance of RP from the closest reference point is greater than a pre-defined threshold
        """
        # condition 1
        reference_points = [p_relations for p_relations in self.primary_relations if self._get_number_of_projecting_attributes(p_relations)]

        # condition 2
        for r1 in self.relations:
            # Pass if already a reference point
            if r1 in reference_points:
                continue

            # Accumulate starting edges to other relations
            start_list = set()
            relations_except_r1 = [r2 for r2 in self.relations if r1 != r2]
            for r2 in relations_except_r1:
                # Get all simple paths
                simple_path_starts = [simple_path[0] for simple_path in nx.all_simple_edge_paths(self, r1, r2)]
                start_list.union(set(simple_path_starts))
            
            # Branching point if there is more than one starting points to other relations && 
            #   there are more than one relations (because there could be different paths to a single relation)
            if len(start_list) > 1 and len(relations_except_r1) > 1:
                # Add this relation as a reference point
                reference_points.append(r1)

        # condition 3
        for r1 in self.relations:
            # Pass if already a reference point
            if r1 in reference_points:
                continue
            # Add relation as a reference point, if leaft relation if there is not path to any other relation
            assert (r1 in self.leaf_relations) == all([not nx.has_path(self, r1, r2) for r2 in self.relations if r1 != r2]), "Need debugging on leaf relation"
            if r1 in self.leaf_relations:
            # if all([not nx.has_path(self, r1, r2) for r2 in self.relations if r1 != r2]):
                reference_points.append(r1)

        # condition 4
        for r1 in self.relations:
            # Pass if already a reference point
            if r1 in reference_points:
                continue
            # Get minimum distance to other reference points
            shortest_path_lengths = [nx.shortest_path_length(self, r1, rp) for rp in reference_points]
            min_distance = min(shortest_path_lengths) if shortest_path_lengths else float('inf')
            # If minimum distance greater than the threshold
            if min_distance > self.reference_point_distance_threshold:
                # Add this relation as a reference point
                reference_points.append(r1)                

        return reference_points


    @property
    def primary_relations(self):
        """TODO: Annotation for primary relation should be given from the datase graph.
                But, for now, we determine it by whether the relation contains any projection attribute"""
        return list(filter(lambda r: self._get_number_of_projecting_attributes(r), self.relations))

    @property
    def secondary_relations(self):
        """ TODO: Annotation for secondary relation should be given from the database graph.
                 But, for now, we determine it by whether the relation contains only selection edges for join
        """
        def is_predicate_for_join(src, edge, dst):
            return type(src) == Attribute and type(edge) == Predicate and type(dst) == Attribute

        def is_selection_for_join(src, edge, dst):
            # False if edge is not selection
            if not type(edge) == Selection:
                return False
            # Check if next edge is predicate for join
            if type(src) == Attribute and type(dst) == Relation:
                return all(is_predicate_for_join(next_src, self.edges[next_src, next_dst]['data'], next_dst) for next_src, next_dst in self.edges(src) if next_dst != dst)
            elif type(src) == Relation and type(dst) == Attribute:
                return all(is_predicate_for_join(next_src, self.edges[next_src, next_dst]['data'], next_dst) for next_src, next_dst in self.edges(dst) if next_dst != src)
            else:
                return False

        # Return secondary relations
        return list(filter(lambda relation: all([is_selection_for_join(src, self.edges[src, dst]['data'], dst) for src, dst in self.all_edges_of(relation)]), self.relations))

    @property
    def relations(self):
        return list(filter(lambda n: type(n) == Relation, self.nodes))

    @property
    def query_subjects(self):
        """primary relations that has the mininum distance to its farthest relations. (When more than one is found, we return those with the most number of projecting attributes)
        """
        def get_shortest_distance(src_node, dst_node):
            return nx.shortest_path_length(self, src_node, dst_node)
        def get_max_distance_with_other_relations(src_relation):
            # We assume that all relations are connected and distance(r1,r2) > 0 for all r1 in R and r2 in R.
            shortest_distances = [get_shortest_distance(src_relation, dst_relation) for dst_relation in self.relations if src_relation != dst_relation]
            return float('inf') if len(shortest_distances) == 0 else max(shortest_distances)

        # Find relations 
        primary_relations_with_distance_scores = [(pr, get_max_distance_with_other_relations(pr)) for pr in self.primary_relations]
        min_distance = min(distance for pr, distance in primary_relations_with_distance_scores)
        tied_primary_releations = [pr for pr, distance in primary_relations_with_distance_scores if distance == min_distance]
        # Resolve tie with the numer of attributes to project
        max_projecting_attributes = max(self._get_number_of_projecting_attributes(r) for r in tied_primary_releations)
        # Final candidate relations for query subjects
        query_subjects = list(filter(lambda r: self._get_number_of_projecting_attributes(r) == max_projecting_attributes, tied_primary_releations))
        # Randomly return one relation from possible candidates
        return query_subjects

    def _get_number_of_projecting_attributes(self, relation):
        assert type(relation) == Relation
        return len([1 for src, dst in self.all_edges_of(relation) if type(self.edges[src, dst]['data']) == Membership])

    ### Utils for graph construction
    def add_node_if_not_exist(self, node):
        if node not in self: self.add_node(node, data=node)

    def bidirectional_connect(self, node1, edge, node2):
        self.unidirectional_connect(node1, edge, node2)
        self.unidirectional_connect(node2, copy.deepcopy(edge), node1)

    def unidirectional_connect(self, node1, edge, node2):
        # Add node if not exist
        self.add_node_if_not_exist(node1)
        self.add_node_if_not_exist(node2)

        # Add edge if not exist
        if (node1, node2) not in self.edges:
            self.add_edge(node1, node2, data=edge)

    def connect_membership(self, relation, attribute):
        self.unidirectional_connect(attribute, Membership(), relation)

    def connect_selection(self, src_node, dst_node):
        """ Ususally relation-to-attribute
            But, attribute-to-relation when correlation
        """
        self.unidirectional_connect(src_node, Selection(), dst_node)

    def connect_predicate(self, src_attribute, dst_node, operator=OperatorType.Equal):
        """
        dst node: 
            - attribute if join predicate. 
            - value or a set of values if selection predicate 
        """
        self.unidirectional_connect(src_attribute, Predicate(operator), dst_node)

    def connect_transformation(self, src_node, dst_node):
        """NEEDCHECK: function_node to attribute or vice versa"""
        self.unidirectional_connect(src_node, Transformation(), dst_node)

    def connect_order(self, src_node, dst_attribute):
        """relation-to-attribute or attribute-to-attribute if multiple order by columns"""    
        self.unidirectional_connect(src_node, Order(), dst_attribute)

    def connect_grouping(self, src_node, dst_attribute):
        """ src_node: relation or attribute """
        self.unidirectional_connect(src_node, Grouping(), dst_attribute)

    def connect_having(self, relation, attribute):
        self.unidirectional_connect(relation, Having(), attribute)

    def connect_join(self, relation1, r1_attribute, r2_attribute, relation2):
        self.bidirectional_connect(relation1, Selection(), r1_attribute)
        self.bidirectional_connect(r1_attribute, Predicate(), r2_attribute)
        self.bidirectional_connect(relation2, Selection(), r2_attribute)

    def connect_simplified_join(self, relation1, relation2, label1="", label2=""):
        self.unidirectional_connect(relation1, Join(label1), relation2)
        self.unidirectional_connect(relation2, Join(label2), relation1)

    def connect(self, node1, node2):
        self.unidirectional_connect(node1, Dummy_edge(), node2)

    def draw(self):
        labels = {key: f"{value.name}" for key, value in nx.get_node_attributes(self, 'data').items()}
        node_color_list = []
        node_color_map = {
            Relation: "red",
            Attribute: "green",
            Value: "blue",
            Function: "pink",
        }
        node_color_list = [node_color_map.get(type(node), "black") for node in self]
        nx.draw(self, nx.spring_layout(self), labels=labels, node_color=node_color_list)

    ### Utils for traversal
    def all_edges_of(self, node):
        return [(src, dst) for src, dst in self.out_edges(node)] + [(src, dst) for src, dst in self.in_edges(node)]

    def get_one_hop_path_of(self, node):
        return [(src, self.edges[src, dst]['data'], dst) for src, dst in self.edges(node)]
