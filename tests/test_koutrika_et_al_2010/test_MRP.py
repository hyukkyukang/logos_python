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
        # query_graph.draw()
        #TODO: need to give reference point and parent node for the initial call
        reference_point, parent_node = None, None
        composed_nl = self.algorithm(query_graph.query_subjects[0], parent_node, reference_point, query_graph).lower()
        self.assertTrue(gold == composed_nl, f"MRP: Incorrect translation of {test_name} query!\nGOLD:{gold}\nResult:{composed_nl}")

    def test_spj(self):
        self._test_query(SPJ_query(), "SPJ")

    def test_group(self):
        self._test_query(GroupBy_query(), "GroupBy")

    def test_nested1(self):
        self._test_query(Nested_query(), "Nested1")

    def test_nested2(self):
        self._test_query(Nested_query2(), "Nested2")

    def test_nested3(self):
        self._test_query(Nested_query3(), "Nested3")


if __name__ == "__main__":
     unittest.main()
