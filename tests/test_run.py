import os
import unittest
import random

import mltracker
from tests.config import TEST_OUTPUT_DIR


def rand_run_name(length=8):
    if length > 12:
        length = 12
    
    x = [str(random.randint(0,9)) for _ in range(length)]
    x = str.join("", x)
    return x

class ExperimentRunTest(unittest.TestCase):
    def test_create_run(self):
        exp_name = "TEST_RUN"
        run_name = rand_run_name() # random since it must be unique
        expected_run_dir = os.path.join(TEST_OUTPUT_DIR, exp_name, run_name)

        session = mltracker.Session(exp_name, data_dir=TEST_OUTPUT_DIR)
        session.start(run_name=run_name)
        self.assertEqual(expected_run_dir, session.run_dir)
        self.assertTrue(os.path.isdir(session.run_dir))

        exp_id = session._experiment.id
        db_run:mltracker.Run = session._db.get_run_by_name(exp_id, run_name)
        self.assertIsInstance(db_run, mltracker.Run)
        self.assertEqual(run_name, db_run.name)

        db_exp = session._db.get_experiment_by_id(db_run.experiment)
        self.assertIsInstance(db_exp, mltracker.Experiment)
        self.assertEqual(exp_name, db_exp.name)
        session.close()


if __name__ == "__main__":
    unittest.main()