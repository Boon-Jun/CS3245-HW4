import unittest
import boolean_operations

class TestBooleanOperations(unittest.TestCase):
    # boolean Operations Test
    list1 = [1, 2, 3, 4, 5, 6, 7, 8]
    list2 = [1, 2, 3, (4, 7), 5, 6, 7, 8]
    list3 = [1, 3, 4, (8, 9), 9]
    list4 = []

    def testAndOp(self):
        self.assertEqual(boolean_operations.andOp(self.list1, self.list1), [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(boolean_operations.andOp(self.list2, self.list3), [1, 3, 4, 8])
        self.assertEqual(boolean_operations.andOp(self.list3, self.list4), [])
        self.assertEqual(boolean_operations.andOp(self.list4, self.list3), [])

    def testOrOp(self):
        self.assertEqual(boolean_operations.orOp(self.list1, self.list1), [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(boolean_operations.orOp(self.list2, self.list3), [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(boolean_operations.orOp(self.list3, self.list4), [1, 3, 4, 8, 9])
        self.assertEqual(boolean_operations.orOp(self.list4, self.list3), [1, 3, 4, 8, 9])

    def testNotOp(self):
        self.assertEqual(boolean_operations.notOp(self.list1, self.list1), [])
        self.assertEqual(boolean_operations.notOp(self.list2, self.list3), [2, 5, 6, 7])
        self.assertEqual(boolean_operations.notOp(self.list3, self.list4), [1, 3, 4, 8, 9])
        self.assertEqual(boolean_operations.notOp(self.list4, self.list3), [])

if __name__ == '__main__':
    unittest.main()
