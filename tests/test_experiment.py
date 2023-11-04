import os
import unittest

import mltracker
from tests.config import TEST_OUTPUT_DIR

class ExperimentTest(unittest.TestCase):
    def test_create_experiment(self):
        exp_name = "TEST_CREATE_EXPERIMENT"
        expected_exp_dir = os.path.join(TEST_OUTPUT_DIR, exp_name)

        session = mltracker.Session(exp_name, data_dir=TEST_OUTPUT_DIR)
        session.start()
        db = session._db
        exp_id = session.get_experiment_id()
        self.assertIsInstance(exp_id, int)

        self.assertEqual(expected_exp_dir, session.experiment_dir)
        self.assertTrue(os.path.isdir(session.experiment_dir))

        self.assertIsInstance(session._experiment, mltracker.Experiment)
        self.assertEqual(exp_name, session._experiment.name)

        db_exp = db.get_experiment_by_id(exp_id)
        self.assertIsInstance(db_exp, mltracker.Experiment)
        self.assertEqual(exp_name, db_exp.name)

        db_exp = db.get_experiment_by_name(exp_name)
        self.assertIsInstance(db_exp, mltracker.Experiment)
        self.assertEqual(exp_name, db_exp.name)
        session.close()

    def test_delete_experiment(self):
        exp_name = "TEST_DELETE_EXPERIMENT"
        expected_exp_dir = os.path.join(TEST_OUTPUT_DIR, exp_name)

        session = mltracker.Session(exp_name, data_dir=TEST_OUTPUT_DIR)
        session.start()
        db = session._db
        exp_id = session.get_experiment_id()
        session.delete_experiment()

        self.assertIsNone(db.get_experiment_by_name(exp_name))
        self.assertIsNone(db.get_experiment_by_id(exp_id))
        self.assertFalse(os.path.isdir(session.experiment_dir))

        session.close()


if __name__ == "__main__":
    unittest.main()