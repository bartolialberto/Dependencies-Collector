import unittest
from persistence.BaseModel import db


class ResettingDatabaseTest(unittest.TestCase):
    def test_reset(self):
        tables = db.get_tables()
        db.drop_tables(tables)


if __name__ == '__main__':
    unittest.main()
