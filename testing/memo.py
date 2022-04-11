import unittest


class BasicsOfPythonUnitTesting(unittest.TestCase):
    # All methods inherited: https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug
    @classmethod
    def setUpClass(cls) -> None:
        # Executed at the start of ALL tests
        cls.result = ['test', 'a']
        pass

    def setUp(self) -> None:
        # Executed at the beginning of EACH test
        pass

    # Tests method signature need to start with "test_"
    def test_something(self):
        # Actual test method.
        # Assertions are accessed from self object
        self.assertEqual(True, False)
        self.assertListEqual(self.result, list())
        # 1
        self.assertRaises(ValueError, function, arg1, arg2)
        # or
        # 2
        with self.assertRaises(ValueError):
            function(arg1, arg2)

    def tearDown(self) -> None:
        # Executed at the end of EACH test
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        # Executed at the end of ALL tests
        pass

    # MOCKING... ???


if __name__ == '__main__':
    unittest.main()
