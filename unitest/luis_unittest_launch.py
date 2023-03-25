import unittest
import luis_unittest
suite = unittest.TestLoader().loadTestsFromModule(luis_unittest)
unittest.TextTestRunner().run(suite)