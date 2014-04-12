There are three Python programs here (`-h` for usage):

 - `./decode` a simple non-reordering (monotone) phrase-based decoder
 - `./grade` computes the model score of your output

The commands are designed to work in a pipeline. For instance, this is a valid invocation:

    ./decode | ./grade


The `data/` directory contains the input set to be decoded and the models

 - `data/input` is the input text

 - `data/lm` is the ARPA-format 3-gram language model

 - `data/tm` is the phrase translation model
 - 

The baseline code is in the file 'decode_baseline_cleaner'- It swaps adjacent phrases and looks into the resulting larger search space.

LagrangianRelax.py is the dual decomposition code based upon the work of Yin-Weng Chang et al. This runs fine but the convergence is a huge problem with this method. Only 5 out of 35 sentences converged and hence, the quantitative results are not reported for this approach.

