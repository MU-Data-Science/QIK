# Evaluation
Here, we describe the steps to evaliate and compare image retrieval performance of QIK and its competitors in terms of mAP. 

## Setup
### Pre-requisites:
* [Ananconda](https://docs.anaconda.com/anaconda/install/)
* [Python](https://www.python.org/downloads/release/python-360/)
* [Java](https://www.java.com/en/download/)
* [Apache Ant](https://ant.apache.org/bindownload.cgi)
* [Apache Tomcat](https://tomcat.apache.org/download-90.cgi)
* [Bazel](https://docs.bazel.build/versions/master/install-ubuntu.html)

We have a create setup script `setup_scripts/setup_prereq.sh` to install these pre-requisites at one go and setup the conda environment.
```
. setup_prereq.sh && conda activate qik_env
```

### CBIR systems setup 
* QIK
    ```
    ./setup_qik.sh 
    ```
* CroW
    ```
    ./setup_crow.sh
    ```
* FR-CNN
    ```
    ./setup_frcnn.sh 
    ```
* DIR
    ```
    ./setup_dir.sh
    ```
## To Evaluate.
1. We use a random set of 15k images from the [MSCOCO](https://cocodataset.org/#home) dataset available at `data/15K_Dataset.txt`. Load these images with:  
    ```
    python create_dataset_pickle.py -data <DATASET> -out <DATASET_PICKLE> 
    ```
   eg: 
   ```
    python create_dataset_pickle.py -data data/15K_Dataset.txt -out data/15K_Dataset.pkl 
    ```
2. We use a [Universal Sentence Encoder](https://tfhub.dev/google/universal-sentence-encoder/1) to compute the similarity among human annotated captions of images against human annotated captions of the query image. A similarity threshold τ (of 0.6 or 0.7) is used to determine if an image is a true match. To construct the ground truth use:
    ```
    python create_ground_truth.py -data <DATASET_PICKLE> -threshold <0.6|0.7> -out <GROUND_TRUTH> 
    ```
   eg: To create the ground truth with τ=0.6
   ```
    python create_ground_truth.py -data data/15K_Dataset.pkl -threshold 0.6 -out data/Ground_Truth_6.pkl
    ```
   **Note** Since creating the ground truth takes time, we have make available the ground truth for τ=0.6 at `data/Ground_Truth_6.pkl` and τ=0.7 at `data/Ground_Truth_7.pkl`.
3. Consolidate query results from all the CBIR systems using:
    ```
    python create_results_pickle.py -qik <QIK_CAPTIONS_RESULTS> -qik_objects_8 <QIK_OBJECTS(0.9)_RESULTS> -qik_objects_9 <QIK_OBJECTS(0.8)_RESULTS> -frcnn <FR-CNN RESULTS> -dir <DIR_RESULTS> -delf <DELF_RESULTS> -lire <LIRE RESULTS> -crow <CroW_RESULTS> -out <CONSOLIDATED_QUERY_RESULTS> 
    ```
   **Note** Pre-constructed results are available at `pre_constructed_data`. To create a consolidated query results pickle:
    ```
    python create_results_pickle.py -qik pre_constructed_data/QIK_Captions_Pre_Results_Dict.txt -qik_objects_8 pre_constructed_data/QIK_Objects_8_Pre_Results_Dict.txt -qik_objects_9 pre_constructed_data/QIK_Objects_9_Pre_Results_Dict.txt -frcnn pre_constructed_data/Deep_Vision_Pre_Results_Dict.txt -dir pre_constructed_data/DIR_Pre_Results_Dict.txt -delf pre_constructed_data/DELF_Pre_Results_Dict.txt -lire pre_constructed_data/LIRE_Pre_Results_Dict.txt -crow pre_constructed_data/Crow_Pre_Results_Dict.txt -out pre_constructed_data/15K_Results.pkl
    ```
4. To get mAP Results:
    ```
    python get_mAP.py -image_data <DATASET_PICKLE> -threshold <.70|.60> -pre_computed_results <CONSOLIDATED_QUERY_RESULTS> -ground_truth <GROUND_TRUTH> -categories <CATEGORY_COMBINATIONS> -outfile <RESULT_LOGS> 
    ```
    eg: To compute the mAP for 2 category combination with ground truth threshold τ as 0.6:
    ```
    python get_mAP.py -image_data data/15K_Dataset.pkl -threshold 0.6 -pre_computed_results pre_constructed_data/15K_Results.pkl -ground_truth data/Ground_Truth_6.pkl -categories data/2_cat_comb.txt -outfile data/2_cat_6_results.txt
    ```

## Results
* Table 1:  QIKc vs QIKo : two-object combinations (avg. mAP)
    <table>
        <tr>
            <td rowspan="2"></td>
            <td align="center" colspan="4">τ=0.6</td>
            <td align="center" colspan="4">τ=0.7</td>
        </tr>
        <tr>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
        </tr>
        <tr>
            <td align="center">QIKc</td>
            <td align="center">0.97</td>
            <td align="center">0.96</td>
            <td align="center">0.96</td>
            <td align="center">0.96</td>
            <td align="center">0.88</td>
            <td align="center">0.87</td>
            <td align="center">0.87</td>
            <td align="center">0.87</td>
        </tr>
        <tr>
            <td align="center">QIKo (0.9)</td>
            <td align="center">0.91</td>
            <td align="center">0.91</td>
            <td align="center">0.9</td>
            <td align="center">0.89</td>
            <td align="center">0.73</td>
            <td align="center">0.73</td>
            <td align="center">0.72</td>
            <td align="center">0.71</td>
        </tr>
        <tr>
            <td align="center">QIKo (0.8)</td>
            <td align="center">0.85</td>
            <td align="center">0.86</td>
            <td align="center">0.85</td>
            <td align="center">0.84</td>
            <td align="center">0.66</td>
            <td align="center">0.68</td>
            <td align="center">0.68</td>
            <td align="center">0.67</td>
        </tr>
    </table>

* Table 2:  QIKc vs QIKo : three-object combinations (avg. mAP)
    <table>
        <tr>
            <td rowspan="2"></td>
            <td align="center" colspan="4">τ=0.6</td>
            <td align="center" colspan="4">τ=0.7</td>
        </tr>
        <tr>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
        </tr>
        <tr>
            <td align="center">QIKc</td>
            <td align="center">0.98</td>
            <td align="center">0.97</td>
            <td align="center">0.96</td>
            <td align="center">0.97</td>
            <td align="center">0.89</td>
            <td align="center">0.88</td>
            <td align="center">0.86</td>
            <td align="center">0.85</td>
        </tr>
        <tr>
            <td align="center">QIKo (0.9)</td>
            <td align="center">0.9</td>
            <td align="center">0.9</td>
            <td align="center">0.88</td>
            <td align="center">0.86</td>
            <td align="center">0.68</td>
            <td align="center">0.7</td>
            <td align="center">0.68</td>
            <td align="center">0.66</td>
        </tr>
        <tr>
            <td align="center">QIKo (0.8)</td>
            <td align="center">0.8</td>
            <td align="center">0.81</td>
            <td align="center">0.8</td>
            <td align="center">0.79</td>
            <td align="center">0.59</td>
            <td align="center">0.61</td>
            <td align="center">0.61</td>
            <td align="center">0.6</td>
        </tr>
    </table>

* Table 3:  QIKc vs QIKo : three-object combinations (avg. mAP)
    <table>
        <tr>
            <td rowspan="2"></td>
            <td align="center" colspan="4">τ=0.6</td>
            <td align="center" colspan="4">τ=0.7</td>
        </tr>
        <tr>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
        </tr>
        <tr>
            <td align="center">QIKc</td>
            <td align="center">0.99</td>
            <td align="center">0.96</td>
            <td align="center">0.97</td>
            <td align="center">0.97</td>
            <td align="center">0.92</td>
            <td align="center">0.89</td>
            <td align="center">0.86</td>
            <td align="center">0.86</td>
        </tr>
        <tr>
            <td align="center">QIKo (0.9)</td>
            <td align="center">0.84</td>
            <td align="center">0.86</td>
            <td align="center">0.85</td>
            <td align="center">0.84</td>
            <td align="center">0.62</td>
            <td align="center">0.65</td>
            <td align="center">0.64</td>
            <td align="center">0.62</td>
        </tr>
        <tr>
            <td align="center">QIKo (0.8)</td>
            <td align="center">0.76</td>
            <td align="center">0.76</td>
            <td align="center">0.73</td>
            <td align="center">0.73</td>
            <td align="center">0.53</td>
            <td align="center">0.54</td>
            <td align="center">0.54</td>
            <td align="center">0.53</td>
        </tr>
    </table>

*  Table 4: Results for two-object combinations (avg. of mAP)
    <table>
        <tr>
            <td rowspan="2"></td>
            <td align="center" colspan="4">τ=0.6</td>
            <td align="center" colspan="4">τ=0.7</td>
        </tr>
        <tr>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
        </tr>
        <tr>
            <td align="center">QIK</td>
            <td align="center">0.97</td>
            <td align="center">0.97</td>
            <td align="center">0.97</td>
            <td align="center">0.97</td>
            <td align="center">0.89</td>
            <td align="center">0.89</td>
            <td align="center">0.88</td>
            <td align="center">0.88</td>
        </tr>
        <tr>
            <td align="center">CroW</td>
            <td align="center">0.92</td>
            <td align="center">0.91</td>
            <td align="center">0.90</td>
            <td align="center">0.88</td>
            <td align="center">0.77</td>
            <td align="center">0.78</td>
            <td align="center">0.74</td>
            <td align="center">0.71</td>
        </tr>
        <tr>
            <td align="center">FR-CNN</td>
            <td align="center">0.87</td>
            <td align="center">0.87</td>
            <td align="center">0.86</td>
            <td align="center">0.83</td>
            <td align="center">0.72</td>
            <td align="center">0.73</td>
            <td align="center">0.7</td>
            <td align="center">0.66</td>
        </tr>
        <tr>
            <td align="center">DIR</td>
            <td align="center">0.86</td>
            <td align="center">0.86</td>
            <td align="center">0.84</td>
            <td align="center">0.81</td>
            <td align="center">0.66</td>
            <td align="center">0.68</td>
            <td align="center">0.66</td>
            <td align="center">0.61</td>
        </tr>
        <tr>
            <td align="center">DELF</td>
            <td align="center">0.64</td>
            <td align="center">0.66</td>
            <td align="center">0.63</td>
            <td align="center">0.59</td>
            <td align="center">0.46</td>
            <td align="center">0.48</td>
            <td align="center">0.46</td>
            <td align="center">0.43</td>
        </tr>
        <tr>
            <td align="center">LIRE</td>
            <td align="center">0.54</td>
            <td align="center">0.57</td>
            <td align="center">0.54</td>
            <td align="center">0.5</td>
            <td align="center">0.28</td>
            <td align="center">0.32</td>
            <td align="center">0.32</td>
            <td align="center">0.3</td>
        </tr>
    </table>

*  Table 5: Results for three-object combinations (avg. of mAP)
    <table>
        <tr>
            <td rowspan="2"></td>
            <td align="center" colspan="4">τ=0.6</td>
            <td align="center" colspan="4">τ=0.7</td>
        </tr>
        <tr>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
        </tr>
        <tr>
            <td align="center">QIK</td>
            <td align="center">0.97</td>
            <td align="center">0.96</td>
            <td align="center">0.96</td>
            <td align="center">0.96</td>
            <td align="center">0.9</td>
            <td align="center">0.89</td>
            <td align="center">0.88</td>
            <td align="center">0.87</td>
        </tr>
        <tr>
            <td align="center">CroW</td>
            <td align="center">0.88</td>
            <td align="center">0.89</td>
            <td align="center">0.88</td>
            <td align="center">0.85</td>
            <td align="center">0.72</td>
            <td align="center">0.73</td>
            <td align="center">0.7</td>
            <td align="center">0.67</td>
        </tr>
        <tr>
            <td align="center">FR-CNN</td>
            <td align="center">0.83</td>
            <td align="center">0.84</td>
            <td align="center">0.83</td>
            <td align="center">0.81</td>
            <td align="center">0.61</td>
            <td align="center">0.66</td>
            <td align="center">0.65</td>
            <td align="center">0.61</td>
        </tr>
        <tr>
            <td align="center">DIR</td>
            <td align="center">0.82</td>
            <td align="center">0.83</td>
            <td align="center">0.8</td>
            <td align="center">0.77</td>
            <td align="center">0.6</td>
            <td align="center">0.61</td>
            <td align="center">0.59</td>
            <td align="center">0.55</td>
        </tr>
        <tr>
            <td align="center">DELF</td>
            <td align="center">0.62</td>
            <td align="center">0.63</td>
            <td align="center">0.6</td>
            <td align="center">0.56</td>
            <td align="center">0.43</td>
            <td align="center">0.45</td>
            <td align="center">0.42</td>
            <td align="center">0.39</td>
        </tr>
        <tr>
            <td align="center">LIRE</td>
            <td align="center">0.48</td>
            <td align="center">0.52</td>
            <td align="center">0.51</td>
            <td align="center">0.48</td>
            <td align="center">0.21</td>
            <td align="center">0.25</td>
            <td align="center">0.26</td>
            <td align="center">0.26</td>
        </tr>
    </table>

*  Table 6: Results for four-object combinations (avg. of mAP)
    <table>
        <tr>
            <td rowspan="2"></td>
            <td align="center" colspan="4">τ=0.6</td>
            <td align="center" colspan="4">τ=0.7</td>
        </tr>
        <tr>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
            <td align="center">k=2</td>
            <td align="center">k=4</td>
            <td align="center">k=8</td>
            <td align="center">k=16</td>
        </tr>
        <tr>
            <td align="center">QIK</td>
            <td align="center">0.97</td>
            <td align="center">0.95</td>
            <td align="center">0.95</td>
            <td align="center">0.95</td>
            <td align="center">0.92</td>
            <td align="center">0.88</td>
            <td align="center">0.85</td>
            <td align="center">0.84</td>
        </tr>
        <tr>
            <td align="center">CroW</td>
            <td align="center">0.96</td>
            <td align="center">0.93</td>
            <td align="center">0.91</td>
            <td align="center">0.89</td>
            <td align="center">0.7</td>
            <td align="center">0.72</td>
            <td align="center">0.71</td>
            <td align="center">0.68</td>
        </tr>
        <tr>
            <td align="center">FR-CNN</td>
            <td align="center">0.93</td>
            <td align="center">0.92</td>
            <td align="center">0.9</td>
            <td align="center">0.87</td>
            <td align="center">0.64</td>
            <td align="center">0.71</td>
            <td align="center">0.69</td>
            <td align="center">0.67</td>
        </tr>
        <tr>
            <td align="center">DIR</td>
            <td align="center">0.89</td>
            <td align="center">0.89</td>
            <td align="center">0.86</td>
            <td align="center">0.81</td>
            <td align="center">0.65</td>
            <td align="center">0.67</td>
            <td align="center">0.65</td>
            <td align="center">0.61</td>
        </tr>
        <tr>
            <td align="center">DELF</td>
            <td align="center">0.72</td>
            <td align="center">0.72</td>
            <td align="center">0.69</td>
            <td align="center">0.65</td>
            <td align="center">0.52</td>
            <td align="center">0.52</td>
            <td align="center">0.51</td>
            <td align="center">0.47</td>
        </tr>
        <tr>
            <td align="center">LIRE</td>
            <td align="center">0.54</td>
            <td align="center">0.57</td>
            <td align="center">0.56</td>
            <td align="center">0.54</td>
            <td align="center">0.19</td>
            <td align="center">0.27</td>
            <td align="center">0.28</td>
            <td align="center">0.28</td>
        </tr>
    </table>
