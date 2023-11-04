import os
import shutil
from typing import Any, Hashable
from uuid import uuid4

from mltracker.core.experiment import Experiment
from mltracker.database import TrackingDatabase


def log(*args):
    print("[DEBUG]", *args)


class Session:
    def __init__(self, experiment:str, data_dir="~/.mltracker/") -> None:
        self.experiment_name = experiment

        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.db_path = os.path.join(data_dir, "mltracker.db")
        self._db = TrackingDatabase(self.db_path)
        self._db.init_db()
        self._db.connect()

        self.experiment_dir = None
        self.run_dir = None

        self._experiment = None
        self._run = None

    def _set_experiment(self):
        assert isinstance(self.experiment_name, str)
        self._experiment = self._db.get_experiment_by_name(self.experiment_name)
        if self._experiment is None:
            log("experiment doesn't exists, inserting new experiment")
            self._experiment = self._db.insert_experiment(self.experiment_name)
        else:
            log("experiment already exists")
        self.experiment_dir = os.path.join(self.data_dir, self.experiment_name)
        os.makedirs(self.experiment_dir, exist_ok=True)

    @staticmethod
    def _random_run_name():
        # TODO: use adjectives and nouns instead of random characters
        return str(uuid4()).replace("-","")[:10]

    def start(self, run_name:str=None, params:dict|None=None):
        # TODO: maybe rename to "start_run"
        # start and stop run seperate from start and stop experiment
        log("starting experiment", self.experiment_name)
        if run_name is None:
            run_name = Session._random_run_name()

        self._set_experiment()

        if params is None:
            params = {}

        self._run = self._db.insert_run(self._experiment.id, run_name, params)

        assert self.experiment_dir is not None
        self.run_dir = os.path.join(self.experiment_dir, run_name)
        os.makedirs(self.run_dir, exist_ok=False)
        return self

    def close(self):
        self._db.close()

    def resume(self, run_name:str):
        self._run = self._db.get_run_by_name(self.experiment_name, run_name)
        self.run_dir = os.path.join(self.experiment_dir, run_name)
        os.makedirs(self.run_dir, exist_ok=True)

    def delete_experiment(self) -> bool:
        success = True
        if os.path.isdir(self.experiment_dir):
            shutil.rmtree(self.experiment_dir)
            log(f"deleted experiment {self.experiment_name} files")
        else:
            log(f"{self.experiment_dir} doesn't exists, cant delete files")
            success = False

        self._db.remove_experiment(self._experiment.id)
        self._experiment = None
        self._run = None
        return success

    def log(self, key, value):
        self._db.log_metric(self._run.id, key, value)

    def get_experiment_id(self):
        if isinstance(self._experiment, Experiment):
            return self._experiment.id
        return None

    def get_all_metrics(self):
        return self._db.get_all_metrics(self._run.id)

    def add_param(self, key:Hashable, value:Any):
        assert self._run is not None and isinstance(self._run.params, dict)
        params = self._run.params
        params[key] = value
        self._db.update_run_params(self._run.id, params)

    def set_params(self, params:dict[Hashable, Any]):
        assert self._run is not None and isinstance(self._run.params, dict)
        self._db.update_run_params(self._run.id, params)
