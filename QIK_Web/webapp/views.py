from sys import path
path.append("../APTED/apted")
from django.shortcuts import render
from .forms import TextSearchForm, ImageSearchForm, IndexForm
from util import parse_show_tree
from util import caption_generator
from util import constants
from util import autoencoder
from util import index_qik
import requests
import json
import datetime
from apted import APTED, PerEditOperationConfig
import apted.helpers as apth
import numpy as np
import time
from util import qik_search

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
        autoencoder.init()

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

            # Fetching the checkbox selections.
            ranking_func = form.cleaned_data['ranking_function']

            # QIK Search -- Start ##
            # Noting the time taken for further auditing.
            time = datetime.datetime.now()

            # Query QIK
            sortedCaptionRanksDict = qik_search.qik_search(constants.QUERY_IMAGE_PATH, ranking_func)

            # Auditing the QIK execution time.
            print("QIK Execution time :: ", (datetime.datetime.now() - time))
            ## QIK Search -- End ##

            # Returning the fetched images.
            return render(request, 'webapp/res.html', {'form': form, 'images': sortedCaptionRanksDict, 'imgSrc': constants.QUERY_IMAGE_PATH.replace(constants.QIK_WEBAPP_PATH, constants.QIK_TOMCAT_URL)})

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

                # Adding to LIRE Index.
                req = constants.LIRE_INDEX_URL + constants.QUERY_IMAGE_DIR + f.name
                res = requests.get(req).text

        # Returning the index form.
        form = IndexForm();
        return render(request, 'webapp/index.html', {'form': form})

    else:
        caption_generator.init()
        autoencoder.init()

    # Returning the index form.
    form = IndexForm();
    return render(request, 'webapp/index.html', {'form': form})