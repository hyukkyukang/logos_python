import unittest
from src.algorithm.MRP import MRP
from tests.test_koutrika_et_al_2010.utils import SPJ_query, GroupBy_query, Nested_query, Nested_query2, Nested_query3


class Test_MRP(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_MRP, self).__init__(*args, **kwargs)
        self.algorithm = MRP()

    def _test_query(self, query, test_name):
        query_graph = query.simplified_graph
        gold = query.MRP_nl.lower()
        query_graph.draw()
        #TODO: need to give reference point and parent node for the initial call
        reference_point, parent_node = None, query_graph.query_subjects[0]
        composed_nl = self.algorithm(query_graph.query_subjects[0], reference_point, parent_node, query_graph).lower()
        self.assertTrue(gold == composed_nl, f"MRP: Incorrect translation of {test_name} query!\nGOLD:{gold}\nResult:{composed_nl}")

    def test_spj(self):
        self._test_query(SPJ_query(), "SPJ")

    def test_group(self):
        query = GroupBy_query()
        query_graph = query.simplified_graph
        query_graph.draw()
        reference_point, parent_node = None, query_graph.query_subjects[0]
        composed_nl = self.algorithm(query_graph.query_subjects[0], reference_point, parent_node, query_graph).lower()
        print(f"Composed NL: {composed_nl}")
        self.assertTrue(composed_nl)

    def test_nested1(self):
        query = Nested_query()
        query_graph = query.simplified_graph
        query_graph.draw()
        reference_point, parent_node = None, query_graph.query_subjects[0]
        composed_nl = self.algorithm(query_graph.query_subjects[0], reference_point, parent_node, query_graph).lower()
        print(f"Composed NL: {composed_nl}")
        self.assertTrue(composed_nl)

    def test_nested2(self):
        query = Nested_query2()
        query_graph = query.simplified_graph
        query_graph.draw()
        reference_point, parent_node = None, query_graph.query_subjects[0]
        composed_nl = self.algorithm(query_graph.query_subjects[0], reference_point, parent_node, query_graph).lower()
        print(f"Composed NL: {composed_nl}")
        self.assertTrue(composed_nl)

    def test_nested3(self):
        query = Nested_query3()
        query_graph = query.simplified_graph
        query_graph.draw()
        reference_point, parent_node = None, query_graph.query_subjects[0]
        composed_nl = self.algorithm(query_graph.query_subjects[0], reference_point, parent_node, query_graph).lower()
        print(f"Composed NL: {composed_nl}")
        self.assertTrue(composed_nl)


if __name__ == "__main__":
     unittest.main()
