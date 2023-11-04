# %%
import sqlite3
import random

import mltracker
import pandas as pd


# %%

import os
os.system(f"rm -rf .experiments/*")

# %%

session = mltracker.Session(experiment="experiment 1", data_dir="./.experiments")
session.start(params={"a":1, "b":4})
print("session experiment", session._experiment)

# %%

session._db.get_all_runs(session._experiment.id)

# %%

session._db.get_all_experiments()

# %%

for metric in ['accuracy', 'loss']:
    for i in range(30):
        session.log(metric, random.random() + i - 0.5)
    
# %%

logged_metrics = session.get_all_metrics()
logged_metrics

# %%

len(logged_metrics)