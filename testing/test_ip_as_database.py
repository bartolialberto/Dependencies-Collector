import unittest

from old_thesis_work.ROVScrape import ROVScraper


class IpAsDatabaseTest(unittest.TestCase):
    # All methods inherited: https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug
    @classmethod
    def setUpClass(cls) -> None:
        # eseguito all'inizio di tutti i test UNA volta
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        # eseguito alla fine di tutti i test UNA volta
        pass

    def setUp(self) -> None:
        # eseguito prima di OGNI metodo
        pass

    def test_something(self):
        #self.assertEqual(True, False)  # add assertion here
        # 1
        #self.assertRaises(ValueError, funzione, arg1, arg2)
        # or
        # 2
        #with self.assertRaises(ValueError):
            #funzione(arg1, arg2)
        pass

    def tearDown(self) -> None:
        # se ci sono file/db da testare e che uitilizzano una directory temporanea, qui alla fine si cancella tutto
        # per avere directory pulite per il prossimo test. Eseguito per ultimo PER OGNI test.
        pass
    # MOCKING...


if __name__ == '__main__':
    unittest.main()
