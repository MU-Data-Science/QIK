from sys import path
path.append("util/")

import requests
import constants
import caption_generator
import json
import subprocess
import shlex

from nltk.tree import Tree
from nltk.draw.tree import TreeWidget
from nltk.draw.util import CanvasFrame

def create_tree_ps(parse_tree):
    cf = CanvasFrame(width=550, height=450, closeenough=2)

    t = Tree.fromstring(parse_tree)

    tc = TreeWidget(
        cf.canvas(),
        t,
        draggable=1,
        node_font=("helvetica", -14, "bold"),
        leaf_font=("helvetica", -12, "italic"),
        roof_fill="white",
        roof_color="black",
        leaf_color="green4",
        node_color="blue2",
    )
    cf.add_widget(tc, 10, 10)

    cf.print_to_file(constants.QIK_DATA_DIR + "query_parse_tree.ps")


def explain(query_image_path):
    # Initializing the caption generator model.
    caption_generator.init()

    # Obtaining the caption for the image.
    img_caption = caption_generator.get_caption(query_image_path, True)
    print("explain.py :: explain :: image caption :: ", img_caption)

    # Handling the fullstops in captions.
    query_caption = img_caption
    if query_caption[-1] == '.':
        query_caption = query_caption[:-1].strip()
    print("explain.py :: explain :: caption after cleaning :: ", query_caption)

    # Obtaining the explain plan contents from the backend.
    explain_req = constants.EXPLAIN_SEARCH_URL + query_caption
    explain_res_text = requests.get(explain_req).text
    explain_json = json.loads(explain_res_text)
    print("explain.py :: explain :: response from the backend :: ", explain_json)

    # Constructing the parse tree ps file.
    parse_tree = explain_json['Parse_Tree']
    print("explain.py :: explain :: parse tree :: ", parse_tree)
    create_tree_ps(parse_tree)

    # Converting the ps file to pdf and pdf to png.
    subprocess.call(shlex.split("ps2pdf -dEPSCrop " + constants.QIK_DATA_DIR + "query_parse_tree.ps " + constants.QIK_DATA_DIR+ "query_parse_tree.pdf"))
    subprocess.call(shlex.split("pdfcrop --margins '5 10 20 30' " + constants.QIK_DATA_DIR+ "query_parse_tree.pdf" + " " + constants.QIK_DATA_DIR+ "query_parse_tree_cropped.pdf"))
    subprocess.call(shlex.split("gs -o " + constants.QIK_WEBAPP_PATH + "query_parse_tree.jpg -sDEVICE=jpeg -r500 " + constants.QIK_DATA_DIR + "query_parse_tree_cropped.pdf"))

    # Return values.
    parse_tree = explain_json['Parse_Tree']
    parse_tree_img = constants.QIK_WEBAPP_PATH + "query_parse_tree.jpg"
    xml_representation = explain_json['XML_Representation']
    min_xml_representation = explain_json['Minimum_XML_Representation']
    xpath = explain_json['XPath']
    optimized_xpath = explain_json['Optimized_XPath']
    query_exec_time = explain_json['Query_Exec_Time']
    similar_exec_time = explain_json['Similar_Exec_Time']
    similar_xpath = explain_json['Similar_XPath']

    return img_caption, parse_tree, parse_tree_img, xml_representation, min_xml_representation, xpath, optimized_xpath, query_exec_time, similar_exec_time, similar_xpath