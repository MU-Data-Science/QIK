# [Deep Image Retrieval](https://github.com/almazan/deep-image-retrieval.git)

## Set up
With conda you can run the following commands:

```
conda install numpy matplotlib tqdm scikit-learn
conda install pytorch torchvision cudatoolkit=10.0 -c pytorch
```

Download and extract the following to ```QIK_Data``` folder.

[MSCOCO Dataset](https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/EU5h_fnPLJhBvevls58-EjgBkOvbZYG19DwKlXmfH1eDHg?e=0UhHqj) 

[Model](https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/EU5h_fnPLJhBvevls58-EjgBkOvbZYG19DwKlXmfH1eDHg?e=0UhHqj)

[Image List](https://mailmissouri-my.sharepoint.com/:t:/g/personal/az2z7_mail_umkc_edu/ERNqvx8GrEBImp-aVYm_DZYBlwsEn_Z3v0r8aVIsWu2drA?e=XKFImH)

[Extracted Features](https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/Ed3wDCZXiBBHre6lQHZx3xgBV693ywEMI769lhVglZclsQ?e=lcEIRc)

Add  ```DB_ROOT``` and ```DIR_ROOT``` to the path.
```
export DB_ROOT=''
export DIR_ROOT=$PWD
```

## To extract features for MSCOCO
``` 
python -m dirtorch.extract_features 
	--dataset 'ImageList("QIK_Data/MSCOCO.txt")'
	--checkpoint QIK_Data/Resnet-101-AP-GeM.pt 
	--output QIK_Data/QIK_DIR_Features --gpu 0
```
