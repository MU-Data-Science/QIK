# Deep Vision 
An image retrieval system forked from [Faster R-CNN Features for Instance Search](https://github.com/imatge-upc/retrieval-2016-deepvision)

## Set Up (Needs to be done on a system with GPU)
Execute ```setup.sh```

## Extract Database Image Features
Execute ```read_data.py``` with ```params['database_images']``` set to the database image folder.

Execute ```features.py``` to extract Fast R-CNN features for all images in a dataset and store them to disk.

## Deploy the App 
Execute ```qik_search.py```

## Query Deep Vision
```http://<HOST_IP>:5000/deepvision?query=<IMAGE_FILE>&lim=<FETCH_COUNT>```

## Pre-Compute Search Results.
`python deepvision_eval.py`