HOST_IP="localhost"
TOMCAT_IP_ADDR = "http://localhost:8080"
TOMCAT_LOC = "/mydata/apache-tomcat/webapps"
AUTO_ENC_CHECKPOINT_PATH = "../ML_Models/AutoEncoder/checkpoints/model.h5"
QIK_WEBAPP_PATH="/mydata/apache-tomcat/webapps/QIK/"
QIK_TOMCAT_URL="http://localhost:8080/QIK/"
QUERY_IMAGE_PATH = QIK_WEBAPP_PATH + "image.jpg"
KNN_INDEX="/mydata/KNN_Index/knn.index"
KNN_DICT="/mydata/KNN_Index/files.txt"
LIRE_QUERY="http://localhost:8080/IndexEngine/queryLire?query="
THREAD_COUNT = 10
SOLR_QUERY_URL = "http://localhost:8080/IndexEngine/query?query="
IS_TF_RANKING_ENABLED = False;
TOMCAT_OLD_IP_ADDR = "http://128.105.144.88:8080"
IMAGE_DATA_DIR= "/QIK_Image_Data/"
LIRE_INDEX_URL="http://localhost:8080/IndexEngine/indexLire?dir="
INDEX_ENGINE_URL = "http://localhost:8080/IndexEngine/postData?data="
ALT_LOC = "/dev/data/apache-tomcat-9.0.19/webapps"
QUERY_IMG_PATH = QIK_WEBAPP_PATH + "image.jpg"
QUERY_IMAGE_DIR = QIK_WEBAPP_PATH

# QIK Object Detection Constants
OBJECT_DETECTED_THRESHOLD = .90
DETECT_OBJECTS_URL = "http://localhost:8080/IndexEngine/queryObjects?data="

# DIR Constants.
DIR_QUERY_FILE_PATH="../ML_Models/DeepImageRetrieval/QIK_Data/query.txt"
DIR_MODEL_PATH="../ML_Models/DeepImageRetrieval/QIK_Data/Resnet-101-AP-GeM.pt"
DIR_QUERY_FEATURES_FILE="../ML_Models/DeepImageRetrieval/QIK_Data/query"
DIR_CANDIDATES_FEATURES_FILE="../ML_Models/DeepImageRetrieval/QIK_Data/QIK_DIR_Features"
DIR_CANDIDATE_IMAGE_DATA="../ML_Models/DeepImageRetrieval/QIK_Data/DIR_Candidates.txt"
DIR_FETCH_LIMIT=20

# DELF constants
DELF_DB_PATH = '../QIK_Web/data/DELF.db'
DB_IMAGE_DIR = TOMCAT_LOC + IMAGE_DATA_DIR
RESIZED_IMAGE_DIR = '../QIK_Web/data/DELF_Data_Resized'
DELF_MODULE_URL = 'https://tfhub.dev/google/delf/1'
DELF_QUERY_TEMP_FOLDER = '../QIK_Web/data/'
DISTANCE_THRESHOLD = 0.8
DELF_INDEX_PATH = '../QIK_Web/data/DELF.index'
DELF_FETCH_LIMIT = 20

# DeepVision constants
DEEPVISION_SERVER_IP = "128.105.144.55"
DEEPVISION_URL = 'http://' + DEEPVISION_SERVER_IP + ":5000/deepvision"
DEEPVISION_FETCH_LIMIT = 20

# Sentence Similarity Search Constants
SENT_SIM_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder/2"
FAISS_INDEX_PATH = "../ML_Models/SentenceSimilarity/sent_sim.index"
FAISS_FILE_LST_PATH = "../ML_Models/SentenceSimilarity/files.pkl"
FAISS_FETCH_LIMIT = 20