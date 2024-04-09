# MiSleep
MiSleep is for EEG/EMG signal processing and visualization

![logo](resources/entire_logo.png)

## Get start
```shell
pip install misleep==0.1.2b
```

## Data save protocol
You need to use matlab for data saving, the final data should be a structure.


If you are using TDT for recording, here is the example script to save the data.
```matlab
tdt_data = ...

data.EEG_F = tdt_data.streams.EEG1.data(1, :);
data.EEG_P = tdt_data.streams.EEG1.data(2, :);
data.EEG_DIFF = data.EEG_F - data.EEG_P
data.EMG_1 = tdt_data.streams.EMG1.data(1, :);
data.EMG_2 = tdt_data.streams.EMG1.data(2, :);
data.EMG_DIFF = data.EMG_1 - data.EMG_2;
data.REF = data.streams.mou1.data(1, :);
data.channels = {'EEG_F' 'EEG_P' 'EEG_DIFF' 'EMG_1' 'EMG_2' 'EMG_DIFF' 'REF'}
data.sf = {305.1758 305.1758 305.1758 305.1758 305.1758 305.1758 305.1758}
data.time = {'20240409-18:00:00'}
```
And an example of result data:

![Alt text](resources/matdata.png)
