# QIK
**Q**uerying **I**mages Using Contextual **K**nowledge is a large-scale image retrieval system for complex everyday scenes. It combines advances in deep learning and natural language processing in a novel fashion to capture the relationships between objects in an everyday scenes.

## System Setup

Execute `scripts/deploy_scripts/init.sh`

```
. init.sh [--home Home] [--qik QIK_Home] [--core QIK_Core] [-h | --help]
```
Eg:
```
cd scripts/deploy_scripts && . init.sh --home /mydata --qik /mydata/QIK --core QIK_Core
```

## To start the web engine.
```
cd <QIK_HOME>/QIK_Web && python manage.py runserver <IP>:8000
```

The UI can be accessed at http://<IP>:8000/search/image_search

## To construct the index.
List of images can be added to `MetaDataGenerator/images.txt` or the directory containing the images can be added to `MetaDataGenerator/constants.py`

To start the indexing process:
```
cd MetaDataGenerator && python process_images.py
```

## Initial Evaluation Results
Initial evaluation results reported in the paper can be found [here](Documents/QIK_ICMR_Eval_Final.xlsx).

To reproduces the results, follow the steps in the [README](QIK_Evaluation/README.md).

If you would need assistance in setting up the system or if you have any other concerns, feel free to reach out to.

## Acknowledgements
This work was supported by the National Science Foundation under Grant No. 1747751.

## To Cite
If you find the code useful in your research, please consider citing:
```
@InProceedings{QIK_2020_ICMR,
author = {Zachariah, Arun and Gharibi, Mohamed and Rao, Praveen},
title = {QIK: A System for Large-Scale Image Retrieval on Everyday Scenes With Common Objects},
publisher = {Association for Computing Machinery},
booktitle = {Proceedings of the 2020 on International Conference on Multimedia Retrieval}, 
month = {June},
year = {2020}
location = {Dublin, Ireland}
}
```
