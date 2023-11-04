# MLTracker

### Example usage

Start `Experiment`

```python
data_dir = "/home/john/experiments/"
exp_name = "MyExperiment"
session = mltracker.Session(exp_name, data_dir)
session.start()
```

Custom `Run` name

```python
session = mltracker.Session(exp_name, data_dir)
session.start(run_name="testing_layer_norm_1")
```

Log metrics

```python
for epoch in range(EPOCHS):
    Loss = 0
    for x,y in train_dataloader:
        ...
        ...
        ...
        Loss += batch_loss

    session.log("Train Loss", loss)

    accuracy = calc_accuracy(model, test_dataloader)
    session.log("Test accuracy", accuracy)
```