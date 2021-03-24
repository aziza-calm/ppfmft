# ppfmft

**P**yMOL **p**lugin that runs **fmft**.

## Content

* Before starting
* What it does
* In action (plugin run example)
* Issues list

## Before starting
To run this plugin you need:

* [Fast Manifold Fourier Transform suite](https://bitbucket.org/abc-group/fmft_suite/src/669742fae4d05cc662300aae318bd1ec8876d378/)
* [sb-lab-utils](https://bitbucket.org/bu-structure/sb-lab-utils/src/master/)
* and of course [PyMOL](https://pymol.org/2/)

Note that plugin was written on python 2 and works only with PyMOL 1.7.x.

To install a plugin, open PyMOL and then go to `Plugin > Plugin Manager > Install new plugin`. Then press button `Choose file` and browse for `ppfmft.py`.

## What it does

This plugin allows you to run fmft directly from PyMOL. You pick the molecules to dock, adjust the settings and run it. Molecules are preprocessed by default. Upon completion of the process, the plugin clusters the results and loads them as a pymol object with a certain number of states (this number corresponds to the number of results that you select earlier).

## Run example

*This block is not ready yet.*

## Issues list

- [ ] fix settings for the first run.

During the first run in the settings window when specifying the paths to fmft, the path to the sblu also changes. And visa versa, when specifying the path to sblu, the path to fmft changes. 
But these "extra" changes occur only visually, and in the config file itself all paths are saved correctly. Also, as was already mentioned, it behaves like this only on the first run.
Anyway, this bug should be fixed as it confuses the user.

- [ ] complete README
- [ ] compatibility with PyMOL2 (and Python3)
