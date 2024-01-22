# starting kit for the IMaging-PsychiAtry Challenge: predicting autism

## Getting started

This starting kit requires Python 3.9 and the following dependencies:

* `numpy==1.19.5`
* `scipy==1.8.0`
* `pandas==1.3.4`
* `cython==0.29.28`
* `scikit-learn==0.21.3`
* `nilearn==0.7.1`
* `matplolib==3.5.1`
* `seaborn==0.10.0`
* `jupyter==1.0.0`
* `ramp-workflow==0.2.1`


Firstlly make new virtual enviroment with
```
python3.9 -m venv VENV_NAME
```

After that activate the created with 
```
source /VENV_NAME/bin/activate
```
Upon activating virtual enviroment install modules with:

```
pip install -r requirements.txt
```
Also install ramp-workflow with 
```
pip install https://api.github.com/repos/paris-saclay-cds/ramp-workflow/zipball/0.2.1
```

Execute the jupyter notebook, from the root directory using:

```
jupyter notebook autism_starting_kit.ipynb
```



