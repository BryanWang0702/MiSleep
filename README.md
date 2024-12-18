# MiSleep
MiSleep is for EEG/EMG signal processing and visualization

![logo](resources/entire_logo.png)

The name 'MiSleep' is from '**Mi**ce **Sleep**' and sounds like '**my sleep**'.

---

## Get start
```shell
pip install misleep
```

Find the directory where you installed misleep, run
```shell
python -m misleep
```
If you use the miniconda or anaconda, the path will be like `D:/miniconda3/envs/misleep/Lib/site-packages`.

See [https://bryanwang.cn/MiSleep/](https://bryanwang.cn/MiSleep/) for a simple documentation.

---

## Some features
1. Free self-define data structure

You can organize your data with matlab structure like this:
```matlab
data.EEG = AN_ARRAY_OF_EEG_DATA;
data.EMG_DIFF = AN_ARRAY_OF_EMG_DIFFERENTIAL_DATA;
% Channel name must be the same with you defined above
data.channels = {'EEG' 'EMG_DIFF'};
% Sampling frequency for each channel of data
data.sf = {256 256};
% Acquisition time of your data
data.time = {'20240409-18:00:00'}; 
```
Or if your data format is `.edf`, misleep will also support well.

2. Event Detection

For sleep spindle and sleep slow-wave activities detection, you can check the tools menu for event detection. The auto stage will coming soon.

3. Self-define `config.ini`

There is a config.ini in the root directory of MiSleep source package, multiple parameters can be self define there, check [config.ini](https://bryanwang.cn/MiSleep/#config-file) for detail.

**Future**: Open for suggestions :).

---

## Cite this work

If you use this software, please cite it as below.
Xueqiang Wang. (2024). BryanWang0702/MiSleep. Zenodo. https://doi.org/10.5281/zenodo.14511905

