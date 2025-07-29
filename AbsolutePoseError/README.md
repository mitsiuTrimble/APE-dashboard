# Data Preparation for APE Dashboard
This folder provides the instruction to prepare the data for Absolute Pose Error Dashboard. 

## Capture Ground Truth
In such case, we need to prepare the Ground Truth trajectory, which is currently only available in 3 dataset: `NREL`, `National Western Campus`, and `Trimble ChristChurch`.

Run the script `capture_gt.py` to save the GT file to a place. Check the details of the script to change the folder path. There will be a GT folder created which will be used in the next step
```bash
python capture_gt.py

```

In the GT folder generated, change the data folder `NWC` tp `National Western Campus`

However, due to the problem of `Trimble ChristChurch` dataset, the GT for this dataset has to be manully prepared.

## Generate result json
To get the json for the dashboard, run `run_batch_ape.py`.

```bash
python run_batch_ape.py "/path/to/GT/folder" "/path/to/result/videos" "/path/to/output"

## Example
python run_batch_ape.py "/APE-dashboard/AbsolutePoseError/groundTruth" "/home/tpc/Atlas Results/" "/APE-dashboard"
```
