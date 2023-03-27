import unittest
import bot_unittest_3b

'''
suite = unittest.TestLoader().loadTestsFromModule(bot_unittest_3b)
unittest.TextTestRunner().run(suite)
'''

from bot_unittest_3b import Test_Bot_Activities_Test1, Test_Bot_Activities_Test2, Test_Bot_Activities_Test3, Test_Bot_Activities_Test4

def run_some_tests():
    # Run only the tests in the specified classes

    test_classes_to_run = [Test_Bot_Activities_Test4]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)
        
    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(big_suite)
    
if __name__ == '__main__':
    run_some_tests()

