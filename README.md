Affective Computing with AMIGOS Dataset
===

## Reference
Please read the following papers and documents first

[1] [Entropy-Assisted Multi-Modal Emotion Recognition Framework Based on Physiological Signals](https://arxiv.org/pdf/1809.08410.pdf) 

(This repo forks from the repo of this paper's authors)

[2] [Entropy-Assisted Emotion Recognition of Valence and Arousal Using XGBoost Classifier](http://access.ee.ntu.edu.tw/Publications/Conference/CA04_2018.pdf)

[3] [Feature Introduction and Performance](https://github.com/ChingYenShih/AMIGOS/blob/master/slide/FeatureIntro.pptx), [Paper Slide](https://github.com/ChingYenShih/AMIGOS/blob/master/slide/PaperSlide.pptx)

[4] [AMIGOS: A Dataset for Affect, Personality and Mood Research on Individuals and Groups](https://arxiv.org/pdf/1702.02510.pdf)

[5] [AMIGOS Dataset Website](http://www.eecs.qmul.ac.uk/mmv/datasets/amigos/index.html)



## Environment Setting
1. Clone this repo
2. put **amigos_data/** under **data/**
3. python version: 3.6.5
4. pip3 install -r requirements.txt

## File Description
```
config.py        - parameters used in other files
main.py          - read the features from features.csv, train the classifier, do the cross-validation
mde.py           - util of extracting Dispersion Entropy (DE)
mmse.py          - util of extracting Multivariate Multi-Scale Entropy (MMSE)
mpe.py           - util of extracting Multivariate Permutation Entropy (MPE)
mse.py           - util of extracting Multi-Scale Entropy (MSE)
preprocess.py    - extract basic features from EEG, ECG, GSR
sep.py           - concatenate two features file into one files (have to modify manually to meet your purpose)
utils.py         - several functions using in other files
tune.py          - used to find the best parameters
requirements.txt - the required packages
```


## Preprocessed Data Description
We preprocess downloaded AMIGOS matlab data to csv (subjectID_videoNumber.csv) format in **amigos_data/**, you have to clone the repo first and save **amigos_data/** under the **data/** of this repo. The following is the example layout.

```
AMIGOS
├── data
|   ├── amigos_data
|   |   ├── 1_1.csv    
|   |   ├── 1_2.csv                                               
|   |   └── ...                                                  
|   |   ├── label.csv                                            

```

In each csv file, the row corresponds to the time stamp (fs = 128 Hz), and the column corresponds to the physiological signal's channel (14 EEG + 2 ECG + 1 GSR)

In 1_1.csv, the data format will be like

|TIMESTAMP|EEG1|EEG2|...|EEG14|ECG1|ECG2|GSR|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| time stamp 1|...|...|...|...|...|...|...|
| time stamp 2|...|...|...|...|...|...|...|
| time stamp 3|...|...|...|...|...|...|...|

In label.csv, the data format will be like

|subID_videoNum|Arousal|Valence|Dominance|Liking|Familiarity|Neutral|Disgust|Happiness|Surprise|Anger|Fear|Sadness|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
|1_1|...|...|...|...|...|...|...|...|...|...|...|...|
|1_2|...|...|...|...|...|...|...|...|...|...|...|...|
|...|...|...|...|...|...|...|...|...|...|...|...|...|
|1_16|...|...|...|...|...|...|...|...|...|...|...|...|
|2_1|...|...|...|...|...|...|...|...|...|...|...|...|
|...|...|...|...|...|...|...|...|...|...|...|...|...|
|40_16|...|...|...|...|...|...|...|...|...|...|...|...|

## Usage

### Basic Feature Extraction

Extract 287 basic features and store features to data/features.csv (if didn't assign the output path (recommended))
```
python3 preprocess.py -i </path/to/amigos_data> -o </path/to/features.csv>
  -i <data directory>
    path of downloaded preprocessed amigos data (default: data/amigos_data)
  -o <output features path>
    path of output feature (default: data/features.csv)
```
#### EEG feature extraction (175)
Extract power, spectral and relative power of theta, slow alpha, alpha, beta, gamma bands
#### ECG feature extraction (81)
Extract rms(IBI), mean(IBI), 60 spectral power in the bands from [0-6] Hz component of the ECG signal, VLF, LF, HF, TF band power of ECG signal, LF/HF, LF/TF, HF/TF, normalized LF, normalized HF, mean(HR), std(HR), skew(HR), kurt(HR), percentage of high HR, percentage of low HR
#### GSR feature extraction (31)
Extract mean(GSR), mean(first diff of GSR), mean differential for negative values only (mean decrease rate during
decay time), proportion of negative derivative samples, number of local minima in the GSR signal, average rising time of
the GSR signal, spectral power in the [0-2.4] Hz band, zero crossing rate of skin conductance slow response (SCSR) [0-0.2] Hz, zero crossing rate of skin conductance very slow response (SCVSR) [0-0.08] Hz, mean SCSR and SCVSR peak magnitude.


In features.csv, the data format is like below. Note that in the column of subID_videoNum, we will remove the subID_videoNum which consists incomplete data. Therefore, the length of the row is 528 rather than 640

|subID_videoNum|feature 1|feature 2|...|...|feature 286|feature 287|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
|1_1|...|...|...|...|...|...|
|1_2|...|...|...|...|...|...|
|...|...|...|...|...|...|...|
|1_16|...|...|...|...|...|...|
|2_1|...|...|...|...|...|...|
|...|...|...|...|...|...|...|
|40_16|...|...|...|...|...|...|


###  Entropy Feature Extraction
mpe.py, mde.py, mmse.py, mse.py define the utils of entropy domain feature extraction, you have to extract the features and assign the parameters manually using these files. The usage of this file is the same as preprocess.py, after you extract extropy features, you can concatenate features using sep.py




### Training and Cross-Validation
* Load features.csv and label.csv as the input and output of the classifier.
* Binary split the arousal and valence, if arousal > mean arousal of that subject -> arousal = 1, and vice versa
* Feature selection
* Leave-one-subject-out cross validation (print accuracy of each subject)
* Print mean accuracy of cross validation

```
python3 main.py -i </directory/of/features.csv> -i_label </directory/of/label.csv> 
                -f <modality> -c <classifier> 
                -norm <normalization method> -sel <feature selection method> 
                -num <number of features used after feature selection>
  -i <data directory> (default: ./data)
    directory of features.csv
  -i_label <data directory> (default: ./data/amigos_data)
    directory of label.csv
  -f <modality> (default: all)
    choices: [eeg, ecg, gsr, all]
  -c <classifier> (default: xgb)
    choices: [gnb, svm, xgb]
  -norm <normalization method> (default: mean)
    choices: [mean (zero mean), one (map to [-1, 1])]
  -sel <feature selection method> (default: fisher)
    choices: fisher, rfe, no (without selection)]
  -num <number of features used after feature selection> (default: 20)
    assign the number of features

```

### Result
If only use basic features and use the default setting as following
```
python3 preprocess.py
python3 main.py
```
|Training Result | Accuracy|F1 Score|
|:---:|:---:|:---:|
|Arousal|75.56%|0.7517|
|Valence|79.77%|0.7960|

|Testing Result | Accuracy|F1 Score|
|:---:|:---:|:---:|
|Arousal|56.82%|0.5580|
|Valence|75.00%|0.7453|



