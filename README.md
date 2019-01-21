# starting kit for the IMaging-PsychiAtry Challenge: predicting autism

[![Build Status](https://travis-ci.org/ramp-kits/autism.svg?branch=master)](https://travis-ci.org/ramp-kits/autism)

## Getting started

This starting kit requires Python and the following dependencies:

* `numpy`
* `scipy`
* `pandas`
* `scikit-learn`
* `matplolib`
* `seaborn`
* `nilearn`
* `jupyter`
* `ramp-workflow`

Therefore, we advise you to install [Anaconda
distribution](https://www.anaconda.com/download/) which include almost all
dependencies.

Only `nilearn` and `ramp-workflow` are not included by default in the Anaconda
distribution. They will be installed from the execution of the notebook.

Execute the jupyter notebook, from the root directory using:

```
jupyter notebook autism_starting_kit.ipynb
```


## Advanced install using `conda` (optional)

We provide both an `environment.yml` file which can be used with `conda` to
create a clean environment and install the necessary dependencies.

```
conda env create -f environment.yml
```

Then, you can activate the environment using:

```
source activate autism
```

for Linux and MacOS. In Windows, use the following command instead:

```
activate autism
```

## Launch on Binder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ramp-kits/autism/best_submissions?filepath=best_submissions.ipynb)
