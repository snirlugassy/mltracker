import os
import time
import sqlite3
import pickle
from typing import List

from mltracker.core.experiment import Experiment
from mltracker.core.run import Run
from mltracker.core.metric import Metric


CREATE_EXPERIMENT_TABLE = """
    CREATE TABLE experiment(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        created_at FLOAT,
        updated_at FLOAT,
        UNIQUE(name)
    )
"""

CREATE_RUN_TABLE = """
    CREATE TABLE run(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        experiment INTEGER,
        created_at FLOAT,
        updated_at FLOAT,
        params BLOB,
        FOREIGN KEY (experiment) REFERENCES experiment(id),
        UNIQUE(experiment, name)
    )
"""

CREATE_METRIC_TABLE = """
    CREATE TABLE metric(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run INTEGER,
        key TEXT,
        value NUMERIC,
        timestamp FLOAT,
        FOREIGN KEY (run) REFERENCES run(id)
    )
"""

PICKLED_FIELDS = ["params"]

def dict_factory(cursor:sqlite3.Cursor, row:tuple):
    fields = [column[0] for column in cursor.description]
    x = dict(zip(fields, row))
    for k,v in x.items():
        if k in PICKLED_FIELDS and isinstance(v, bytes):
            x[k] = pickle.loads(v)
    return x

class TrackingDatabase:
    """
    TODO:
    - delete aggregrate for all dependent rows
    - maybe move all the query functions to staticmethods on class
    """

    def __init__(self, db_path:str) -> None:
        self.db_path = db_path
        self._connection: sqlite3.Connection = None
        self._cursor: sqlite3.Cursor = None

    def _check_db_exists(self) -> bool:
        if os.path.isfile(self.db_path):
            return True
        return False

    def init_db(self) -> bool:
        if self._check_db_exists():
            return False
        self._connection = sqlite3.connect(self.db_path)
        self._cursor = self._connection.cursor()
        self._cursor.execute(CREATE_EXPERIMENT_TABLE)
        self._cursor.execute(CREATE_RUN_TABLE)
        self._cursor.execute(CREATE_METRIC_TABLE)
        self._cursor.close()
        return True

    def connect(self):
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = dict_factory

    def close(self):
        if self._cursor is not None:
            self._cursor.close()

        if self._connection is not None:
            self._connection.close()

    # EXPERIMENTS
    def get_all_experiments(self) -> List[Experiment]:
        q = f"SELECT * FROM {Experiment.__table__}"
        with self._connection:
            cur = self._connection.execute(q)
            return cur.fetchall()

    def get_experiment_by_name(self, experiment_name:str) -> Experiment:
        q = f"SELECT * FROM {Experiment.__table__} WHERE name=?"
        with self._connection:
            cur = self._connection.execute(q, (experiment_name, ))
            e = cur.fetchone()
            if e is not None:
                return Experiment(**e)
        return None

    def get_experiment_by_id(self, experiment_id:int) -> Experiment:
        q = f"SELECT * FROM {Experiment.__table__} WHERE id=?"
        with self._connection:
            cur = self._connection.execute(q, (experiment_id, ))
            e = cur.fetchone()
            if e is not None:
                return Experiment(**e)
        return None

    def insert_experiment(self, experiment_name:str) -> Experiment:
        q = f"INSERT INTO {Experiment.__table__}"
        q += "(name, created_at, updated_at) VALUES (?,?,?)"

        t = time.time()

        with self._connection:
            self._connection.execute(q, (experiment_name, t, t))

        return self.get_experiment_by_name(experiment_name)

    def remove_experiment(self, experiment_id:int) -> bool:
        # TODO: return true or false upon success or fail
        q = f"DELETE FROM {Experiment.__table__} WHERE id=?"

        with self._connection:
            self._connection.execute(q, (experiment_id, ))

    # RUNS
    def get_all_runs(self, experiment_id:int) -> List[Run]:
        q = f"SELECT * FROM {Run.__table__} WHERE experiment=?"
        with self._connection:
            cur = self._connection.execute(q, (experiment_id, ))
            return cur.fetchall()

    def get_run_by_name(self, experiment_id:int, run_name:str) -> Run:
        q = f"SELECT * FROM {Run.__table__} WHERE experiment=? AND name=?"
        with self._connection:
            cur = self._connection.execute(q, (experiment_id, run_name))
            r = cur.fetchone()
            if r is not None:
                return Run(**r)
        return None

    def get_run_by_id(self, run:int) -> Run:
        q = f"SELECT * FROM {Run.__table__} WHERE id=?"
        with self._connection:
            cur = self._connection.execute(q, (run, ))
            r = cur.fetchone()
            if r is not None:
                return Run(**r)
        return None

    def insert_run(self, experiment_id:int, run_name:str, params:dict) -> Run:
        q = f"INSERT INTO {Run.__table__}"
        q += "(experiment, name, params, created_at, updated_at) VALUES (?,?,?,?,?)"

        t = time.time()

        blob = sqlite3.Binary(pickle.dumps(params))

        with self._connection:
            self._connection.execute(q, (experiment_id, run_name, blob, t, t))

        return self.get_run_by_name(experiment_id, run_name)

    def remove_run(self, run_id:int) -> bool:
        q = f"DELETE FROM {Run.__table__}"
        q += "WHERE id=?"

        with self._connection:
            self._connection.execute(q, (run_id, ))

    def update_run_params(self, run_id:int, params:dict):
        assert isinstance(params, dict)
        blob = sqlite3.Binary(pickle.dumps(params))
        q = f"UPDATE {Run.__table__} SET params=? WHERE id=?"
        with self._connection:
            self._connection.execute(q, (blob, run_id))

    # METRICS
    def log_metric(self, run:int, key:str, value:float) -> bool:
        q = f"INSERT INTO {Metric.__table__}"
        q += "(run, key, value, timestamp) VALUES (?,?,?,?)"

        with self._connection:
            self._connection.execute(q, (run, key, value, time.time()))

    def get_all_metrics(self, run:int):
        q = f"SELECT * FROM {Metric.__table__} WHERE run=?"
        with self._connection:
            cur = self._connection.execute(q, (run,))
            return cur.fetchall()
