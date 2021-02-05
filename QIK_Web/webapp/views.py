from sys import path
path.append("../APTED/apted")
from django.shortcuts import render
from .forms import TextSearchForm, ImageSearchForm, IndexForm, ExplainForm
from util import parse_show_tree
from util import caption_generator
from util import constants
from util import index_qik
from util import explain
import requests
import json
import datetime
from datetime import timedelta
from apted import APTED, PerEditOperationConfig
import apted.helpers as apth
import numpy as np
import time
from util import qik_search
import subprocess
import shlex

queryParseTree = ''
queryDepTree = ''
query_image_vec = np.empty(0)

def text_search(request):
    if request.method == 'POST' :
        form = TextSearchForm(request.POST)

        if form.is_valid():
            captionRanksDict = {}
            sortedCaptionRanksDict = {}
            global queryParseTree
            global queryDepTree
            global query_image_vec

            # Fetching the checkbox selections.
            ranking_func = form.cleaned_data['ranking_function']

            # QIK Search -- Start ##
            # Noting the time taken for further auditing.
            time = datetime.datetime.now()

            # Getting the captions.
            query = form.cleaned_data['query']
            print("Caption :: ", query)

            # Querying the backend to fetch the list of images and captions.
            req = constants.SOLR_QUERY_URL + query
            res = json.loads(requests.get(req).text)
            print("Response :: ", res)
            print("QIK Fetch Execution time :: ", (datetime.datetime.now() - time))

            # Forming the return image set.
            if res is not None:
                # Generating the parse tree for the input query.
                queryParseTree = parse_show_tree.parseSentence(query)

                # Generating the dependency tree for the input query.
                queryDepTree = parse_show_tree.dependencyParser(query)

                # Performing TED based Ranking on the parse tree.
                if ranking_func == 'Parse Tree':
                    for resMap in res:
                        # for Auditing TED Time
                        ted_time = datetime.datetime.now()

                        image = resMap['fileURL']
                        caption = resMap['caption']
                        captionParseTree = resMap['parseTree']

                        parseTED = APTED(apth.Tree.from_text(queryParseTree), apth.Tree.from_text(captionParseTree),
                                         PerEditOperationConfig(1, 1, 1)).compute_edit_distance()
                        print("Caption ::", caption, " :: TED :: ", parseTED)
                        print("Time taken to compute Parse Tree TED :: ", (datetime.datetime.now() - ted_time))

                        # Temp Fix done to replace Tomcat IP. Needs to be handled in the IndexEngine.
                        image_path = image.replace(constants.TOMCAT_OLD_IP_ADDR, constants.TOMCAT_IP_ADDR)

                        captionRanksDict[image_path + ":: " + caption] = parseTED

                    # Sorting the results based on the Parse TED.
                    sortedCaptionRanksDict = sorted(captionRanksDict.items(), key=lambda kv: kv[1], reverse=False)
                    print(sortedCaptionRanksDict)

                elif ranking_func == 'Dependency Tree':
                    for resMap in res:
                        # for Auditing TED Time
                        ted_time = datetime.datetime.now()

                        image = resMap['fileURL']
                        caption = resMap['caption']
                        depTree = resMap['depTree']

                        parseTED = APTED(apth.Tree.from_text(queryDepTree), apth.Tree.from_text(depTree),
                                         PerEditOperationConfig(1, 1, 1)).compute_edit_distance()
                        print("Caption ::", caption, " :: TED :: ", parseTED)
                        print("Time taken to compute Dependency Tree TED :: ", (datetime.datetime.now() - ted_time))

                        # Temp Fix done to replace Tomcat IP. Needs to be handled in the IndexEngine.
                        image_path = image.replace(constants.TOMCAT_OLD_IP_ADDR, constants.TOMCAT_IP_ADDR)

                        captionRanksDict[image_path + ":: " + caption] = parseTED

                    # Sorting the results based on the Parse TED.
                    sortedCaptionRanksDict = sorted(captionRanksDict.items(), key=lambda kv: kv[1], reverse=False)
                    print(sortedCaptionRanksDict)

                else:
                    # Forming the return image set (Without ranking)
                    for resMap in res:
                        caption = resMap['caption']
                        image = resMap['fileURL']

                        # Temp Fix done to replace Tomcat IP. Needs to be handled in the IndexEngine.
                        image_path = image.replace(constants.TOMCAT_OLD_IP_ADDR, constants.TOMCAT_IP_ADDR)

                        captionRanksDict[image_path + ":: " + caption] = 1
                    print(captionRanksDict)

                    # Formating done for Ranking
                    sortedCaptionRanksDict = sorted(captionRanksDict.items(), key=lambda kv: kv[1], reverse=True)
                    print("sortedCaptionRanksDict :: ", sortedCaptionRanksDict)

            # Auditing the QIK execution time.
            print("QIK Execution time :: ", (datetime.datetime.now() - time))
            ## QIK Search -- End ##

            # Returning the fetched images.
            return render(request, 'webapp/results.html', {'form': form, 'images': sortedCaptionRanksDict})

    else:
    	# Initial loading
        caption_generator.init()

    form = TextSearchForm();
    return render(request, 'webapp/home.html', {'form':form})

def image_search(request):

    if request.method == 'POST' :
        form = ImageSearchForm(request.POST, request.FILES)

        if form.is_valid():
            global queryParseTree
            global queryDepTree
            global query_image_vec

            # Setting the QUERY_IMAGE_PATH
            constants.QUERY_IMAGE_PATH = constants.QUERY_IMG_PATH

            # Saving the file locally.
            try:
                handleUploadedFile(request.FILES['imageFile'])
            except:
                # Considering the default files provided
                constants.QUERY_IMAGE_PATH = request.POST.get("images", "")
                print("query_image :: " , constants.QUERY_IMAGE_PATH)

            # Fetching the form selections.
            ranking_func = form.cleaned_data['ranking_function']
            k = form.cleaned_data['k_value']
            search_model = form.cleaned_data['search_models']

            # Defining the model to be used.
            obj_det_enabled = False
            pure_objects_search = False

            if search_model == 'Objects Model':
                obj_det_enabled = True
                pure_objects_search = True
            elif search_model == 'Hybrid Model':
                obj_det_enabled = True

            # QIK Search -- Start ##
            # Noting the time taken for further auditing.
            time = datetime.datetime.now()

            # Query QIK
            query, sortedCaptionRanksDict, similar_images = qik_search.qik_search(constants.QUERY_IMAGE_PATH, ranking_func, obj_det_enabled=obj_det_enabled, pure_objects_search=pure_objects_search,fetch_count=k)

            # Auditing the QIK execution time.
            print("QIK Execution time :: ", (datetime.datetime.now() - time))
            ## QIK Search -- End ##

            # Returning the fetched images.
            return render(request, 'webapp/imageResults.html', {'form': form, 'images': sortedCaptionRanksDict, 'imgSrc': constants.QUERY_IMAGE_PATH.replace(constants.QIK_WEBAPP_PATH, constants.QIK_TOMCAT_URL), 'similarImages':similar_images, 'rankingFunc':ranking_func, 'caption':query, 'kValue':k, 'searchModel':search_model})
    elif request.method == 'GET' :
        if 'query_image_path' in request.GET and 'ranking_function' in request.GET:
            form = ImageSearchForm();

            # Fetching the form selections.
            query_image_path = request.GET.get('query_image_path')
            ranking_func = request.GET.get('ranking_function')
            k = request.GET.get('k_value')
            search_model = request.GET.get('search_models')

            # Copying the query image to the default location.
            subprocess.call(shlex.split("cp " + query_image_path + " " + constants.QUERY_IMAGE_PATH))

            # Defining the model to be used.
            obj_det_enabled = False
            pure_objects_search = False

            if search_model == 'Objects Model':
                obj_det_enabled = True
                pure_objects_search = True
            elif search_model == 'Hybrid Model':
                obj_det_enabled = True

            # QIK Search -- Start ##
            # Noting the time taken for further auditing.
            time = datetime.datetime.now()

            # Query QIK
            query, sortedCaptionRanksDict, similar_images = qik_search.qik_search(query_image_path, ranking_func, obj_det_enabled=obj_det_enabled, pure_objects_search=pure_objects_search,fetch_count=int(k))

            # Auditing the QIK execution time.
            print("QIK Execution time :: ", (datetime.datetime.now() - time))
            ## QIK Search -- End ##

            # Returning the fetched images.
            return render(request, 'webapp/imageResults.html', {'form': form, 'images': sortedCaptionRanksDict, 'imgSrc': query_image_path.replace(constants.QIK_WEBAPP_PATH, constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR), 'similarImages': similar_images, 'rankingFunc':ranking_func, 'caption':query, 'caption':query, 'kValue':k, 'searchModel':search_model})

        else:
            caption_generator.init()

    form = ImageSearchForm();
    return render(request, 'webapp/imageSearch.html', {'form':form})

def handleUploadedFile(f) :
    print("Uploading file upload")

    with open(constants.QUERY_IMAGE_PATH, 'wb+') as dest :
        for chunk in f.chunks() :
            dest.write(chunk)

def add_index(request):
    if request.method == 'POST' :
        form = IndexForm(request.POST, request.FILES)

        if form.is_valid():
            # Reading the files.
            files = request.FILES.getlist('image_files')
            for f in files:
                with open(constants.QUERY_IMAGE_DIR + f.name, 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)

                # Instantiating a thread with the file name as the thread name for creating the captions and adding to index.
                process = index_qik.Process(name=f.name)
                process.start()
                time.sleep(1)

        # Returning the index form.
        form = IndexForm();
        return render(request, 'webapp/index.html', {'form': form, 'index_alert': True})
    else:
        caption_generator.init()

    # Returning the index form.
    form = IndexForm();
    return render(request, 'webapp/index.html', {'form': form})

def explain_query(request):
    if request.method == 'POST' :
        form = ExplainForm(request.POST)

        if form.is_valid():
            query = form.cleaned_data['query']
            print("Caption :: ", query)

            return render(request, 'webapp/results.html', {'form': form})
    elif request.method == 'GET':
        form = ExplainForm();

        # Fetching the form selections.
        query_image_path = request.GET.get('query_image_path')
        print("views.py :: explain_query :: query_image_path :: ", query_image_path)

        if query_image_path is None:
            print("views.py :: explain_query :: Query image not present in the request. Using the default image.")
            query_image_path = constants.QUERY_IMAGE_PATH

        # Contructing the explain plan.
        img_caption, parse_tree, parse_tree_img, xml_representation, min_xml_representation, xpath, optimized_xPath, query_exec_time, similar_exec_time, similar_xpath = explain.explain(query_image_path)

        # Fetching the form selections.
        ranking_func = request.GET.get('ranking_function')
        k = request.GET.get('k_value')
        search_model = request.GET.get('search_models')

        # Defining the model to be used.
        obj_det_enabled = False
        pure_objects_search = False

        if search_model == 'Objects Model':
            obj_det_enabled = True
            pure_objects_search = True
        elif search_model == 'Hybrid Model':
            obj_det_enabled = True

        # Noting the time taken for further auditing.
        time = datetime.datetime.now()

        # Obtain the search times.
        qik_search.qik_search(constants.QUERY_IMAGE_PATH, ranking_func, obj_det_enabled=obj_det_enabled,
                              pure_objects_search=pure_objects_search, fetch_count=k)

        # Auditing the QIK execution time.
        qik_exec_time = datetime.datetime.now() - time
        ranking_time = qik_exec_time - timedelta(milliseconds=int(query_exec_time))
        print("views.py :: explain_query :: ranking_time :: ", ranking_time)

        return render(request, 'webapp/explain.html', {'form': form, 'query_image_path': query_image_path.replace(constants.QIK_WEBAPP_PATH, constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR), 'img_caption': img_caption, 'parse_tree': parse_tree, 'parse_tree_img': parse_tree_img.replace(constants.QIK_WEBAPP_PATH, constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR), 'xml_representation': xml_representation, 'min_xml_representation': min_xml_representation, 'xpath': xpath, 'optimized_xPath': optimized_xPath, 'query_exec_time': query_exec_time, 'ranking_time': ranking_time.total_seconds(), 'qik_exec_time': qik_exec_time.total_seconds(), 'similar_exec_time': similar_exec_time, 'similar_xpath': similar_xpath})
        # return render(request, 'webapp/explain.html', {'form': form, 'query_image_path': query_image_path.replace(constants.QIK_WEBAPP_PATH, constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR)})
    else:
        caption_generator.init()

    form = ExplainForm();
    return render(request, 'webapp/explain.html', {'form':form})

def about(request):
    print("views.py :: explain_query :: Rendering about QIK.")
    return render(request, 'webapp/about.html')