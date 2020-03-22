from sys import path
path.append("../APTED/apted")
path.append("../ML_Models/ObjectDetection")
path.append("util/")

import caption_generator
import constants
import json
import requests
import datetime
import parse_show_tree
import urllib
from apted import APTED, PerEditOperationConfig
import apted.helpers as apth
import detect_objects

def qik_search(query_image, ranking_func=None, obj_det_enabled=False, pure_objects_search=False, fetch_count=None):
    obj_res = None
    cap_res = None

    captionRanksDict = {}
    sortedCaptionRanksDict = {}

    # Noting the time taken for further auditing.
    time = datetime.datetime.now()

    if obj_det_enabled:
        # Initial Loading of the object detection model.
        detect_objects.init()

        # Detecting objects.
        json_data = {}
        json_data['objects'] = detect_objects.get_detected_objects(query_image, constants.OBJECT_DETECTED_THRESHOLD)
        print("qik_search :: qik_search :: objects :: ", json_data['objects'])

        # Querying the backend to fetch the list of images and captions based on the objects detected.
        obj_req = constants.DETECT_OBJECTS_URL + urllib.parse.quote(str(json_data))
        obj_res = json.loads(requests.get(obj_req).text)
        print("qik_search :: qik_search :: obj_res :: ", obj_res)

    if pure_objects_search:
        # Forming the return image set.
        for resMap in obj_res:
            caption = resMap['caption']
            image = resMap['fileURL']

            # Temp Fix done to replace Tomcat IP. Needs to be handled in the IndexEngine.
            image_path = image.replace(constants.TOMCAT_OLD_IP_ADDR, constants.TOMCAT_IP_ADDR)

            captionRanksDict[image_path + ":: " + caption] = 1
        print(captionRanksDict)

        # Formating done for Ranking
        sortedCaptionRanksDict = sorted(captionRanksDict.items(), key=lambda kv: kv[1], reverse=True)

        # Auditing the QIK execution time.
        print("QIK Execution time :: ", (datetime.datetime.now() - time))

        if sortedCaptionRanksDict and fetch_count is not None:
            print("sortedCaptionRanksDict :: ", sortedCaptionRanksDict[:fetch_count])
            return sortedCaptionRanksDict[:fetch_count]
        else:
            print("sortedCaptionRanksDict :: ", sortedCaptionRanksDict)
            return sortedCaptionRanksDict

        return sortedCaptionRanksDict

    # Initial Loading of the caption generator model.
    caption_generator.init()

    # Generating the captions.
    query = caption_generator.get_caption(query_image, True)

    # Handling the fullstops in captions.
    if query[-1] == '.':
        query = query[:-1].strip()
    print("Caption Generated :: ", query)

    # Querying the backend to fetch the list of images and captions.
    cap_req = constants.SOLR_QUERY_URL + query
    cap_res = json.loads(requests.get(cap_req).text)
    print("QIK Captions Response :: ", cap_res)
    print("QIK Fetch Execution time :: ", (datetime.datetime.now() - time))

    # Merging the two responses.
    if obj_res is None:
        res = cap_res
    elif cap_res is None:
        res = obj_res
    else:
        res = obj_res + cap_res
    print("QIK Combined Response :: ", res)

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

                # Temp Fix done to replace Tomcat IP. Needs to be handled in the IndexEngine.
                image_path = image.replace(constants.TOMCAT_OLD_IP_ADDR, constants.TOMCAT_IP_ADDR)

                captionRanksDict[image_path + ":: " + caption] = parseTED

            # Sorting the results based on the Parse TED.
            sortedCaptionRanksDict = sorted(captionRanksDict.items(), key=lambda kv: kv[1], reverse=False)

        elif ranking_func == 'Dependency Tree':
            for resMap in res:
                # for Auditing TED Time
                ted_time = datetime.datetime.now()

                image = resMap['fileURL']
                caption = resMap['caption']
                depTree = resMap['depTree']

                parseTED = APTED(apth.Tree.from_text(queryDepTree), apth.Tree.from_text(depTree),
                                 PerEditOperationConfig(1, 1, 1)).compute_edit_distance()

                # Temp Fix done to replace Tomcat IP. Needs to be handled in the IndexEngine.
                image_path = image.replace(constants.TOMCAT_OLD_IP_ADDR, constants.TOMCAT_IP_ADDR)

                captionRanksDict[image_path + ":: " + caption] = parseTED

            # Sorting the results based on the Parse TED.
            sortedCaptionRanksDict = sorted(captionRanksDict.items(), key=lambda kv: kv[1], reverse=False)

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

    # Auditing the QIK execution time.
    print("QIK Execution time :: ", (datetime.datetime.now() - time))

    if sortedCaptionRanksDict and fetch_count is not None:
        print("sortedCaptionRanksDict :: ", sortedCaptionRanksDict[:fetch_count])
        return sortedCaptionRanksDict[:fetch_count]
    else:
        print("sortedCaptionRanksDict :: ", sortedCaptionRanksDict)
        return sortedCaptionRanksDict