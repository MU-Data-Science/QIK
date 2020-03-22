# QIK Evaluation
We compute the results using MAP.

## Environment Setup
* QIK can be deployed using `scripts/deploy_scripts/init.sh`

    `. init.sh [--home Home] [--qik QIK_Home] [--core QIK_Core] [-h | --help]`

* COCO API can Setup `scripts/deploy_scripts/eval_setup.sh`
    
    `bash eval_setup.sh`
    
## To Reproduce the Results.
* To reproduce the results from scratch.
    * Construct the index.
        * QIK: [README](../README.md)
        * DIR: [README](../ML_Models/DeepImageRetrieval/README.md)
        * DeepVision: [README](../ML_Models/DeepVision/README.md)
        * For the other systems, indexes would be constructed while execution the evaluation scripts.
    
* To reproduce the results from a pre-generated index.
    * Download the index to `BaseX/data`
        * [Object Detection Threshold 0.9](https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/ER_2hDjEm-hPgFo6WnwmUCcBqd-UlvgLGlzrqYtrp8dRyA?e=eBYFWl)
        * [Object Detection Threshold 0.8](https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/EZedBIRgYntGpc9h_hsFezcBups95AkJgeR2TwyoFxW8tA?e=D2VDB6)
    * Compute the query results across systems.
        * QIK: `python qik_pre_eval.py`
        * QIK Objects: `python qik_objects_pre_eval.py`
        * LIRE: `python lire_pre_eval.py`
        * DIR: `python dir_pre_eval.py`
        * DELF: `python delf_pre_eval.py`
        * Deep Vision: Evaluation scripts can be found [here](../ML_Models/DeepVision/README.md)
    * Combine all generated results.
        
        `python comb_pre_eval_res.py` 
        
* We have pre-computed query results for all the images extracted from an random subset of 15k images present at `data/MSCOCO_Subset_2`.

To generate the MAP results:
```
python post_eval.py -threshold <THRESHOLD_SCORE> -categories <CATEGROY_COMBINATION_FILE> -preresults <PRE-COMPUTED_RESULTS_FILE> -outfile <OUTPUT_FILE>
```

Eg: To compute the results for the 2 category combination with the threshold 0.6.
```
python post_eval.py -threshold .6 -categories data/2_cat_comb.txt -preresults data/MSCOCO_Subset_2/MSCOCO_Subset_2_Results.pkl -outfile data/QIK_Output_Combined.txt
```

