#!/usr/bin/env bash

METADATA_DIR="/mydata/HMDB51_Metadata"
TRAIN_DIR="/mydata/HMDB51_Train"
TEST_DIR="/mydata/HMDB51_Test"
DATA_DIR="/mydata/HMDB51"

# Creating the directories
mkdir -p ${TRAIN_DIR}
mkdir -p ${TEST_DIR}

for filename in ${METADATA_DIR}/*.txt; do
  while read line; do
      read file set <<<$(IFS=" "; echo ${line})
      if [ ${set} -eq 1 ]; then
        cp ${DATA_DIR}/${file} ${TRAIN_DIR}
      elif [ ${set} -eq 2 ]; then
        cp ${DATA_DIR}/${file} ${TEST_DIR}
      fi
  done <${filename}
done

#Errors Encountered
#cp: cannot stat '/mydata/HMDB51/Brushing_Her_Hair__[_NEW_AUDIO_]_UPDATED!!!!_brush_hair_h_cm_np1_fr_goo_0.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Brushing_Her_Hair__[_NEW_AUDIO_]_UPDATED!!!!_brush_hair_h_cm_np1_le_goo_1.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Brushing_Her_Hair__[_NEW_AUDIO_]_UPDATED!!!!_brush_hair_h_cm_np1_le_goo_2.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Die_Another_Day_-_Fencing_Scene_Part_1_[HD]_avi_fencing_f_cm_np2_le_goo_0.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Die_Another_Day_-_Fencing_Scene_Part_1_[HD]_avi_fencing_u_cm_np2_ba_goo_1.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Die_Another_Day_-_Fencing_Scene_Part_1_[HD]_avi_fencing_u_cm_np2_fr_goo_2.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Die_Another_Day_-_Fencing_Scene_Part_1_[HD]_fencing_f_cm_np2_le_goo_0.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Die_Another_Day_-_Fencing_Scene_Part_1_[HD]_fencing_u_cm_np2_ba_goo_1.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Die_Another_Day_-_Fencing_Scene_Part_1_[HD]_fencing_u_cm_np2_fr_goo_2.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Die_Another_Day_-_Fencing_Scene_Part_1_[HD]_fencing_u_cm_np2_fr_goo_3.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/BHS___FlickFlack_[Tutorial]_flic_flac_f_cm_np1_le_med_0.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Ab_Workout__(_6_pack_abs_)_[_ab_exercises_for_ripped_abs_]_situp_f_nm_np1_le_goo_0.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Ab_Workout__(_6_pack_abs_)_[_ab_exercises_for_ripped_abs_]_situp_f_nm_np1_le_goo_1.avi': No such file or directory
#cp: cannot stat '/mydata/HMDB51/Ab_Workout__(_6_pack_abs_)_[_ab_exercises_for_ripped_abs_]_situp_f_nm_np1_le_goo_2.avi': No such file or directory