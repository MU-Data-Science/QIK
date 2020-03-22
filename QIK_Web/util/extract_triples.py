from lxml import etree
from io import StringIO

verbList = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "VP"]

def getParentNodes(query, tree) :
    r = tree.xpath(f'//*[text()="{query}"]')

    if not r:
        return
		
    parent = r[0].getparent()
    nodelist = [r[0].tag, parent.tag]

    while True: 
        if parent.tag == "ROOT0":
            break
	
        parent = parent.getparent()
        nodelist.append(parent.tag)
        
    return nodelist[:-2]
	
def executeOR(nodelist1, nodelist2) :
    #print("nodelist1 :: ", nodelist1, "nodelist2 :: ", nodelist2)

    for verb in verbList:
        result = [pos for pos in nodelist2 if verb in pos]
        if result:
            result = [pos for pos in nodelist1 if verb in pos]
            
            if result:
                #print("No or relation present")
                return
		    
            return nodelist1
	
    return
	
def getTuples(nounLst, verbLst, inXML) :
    tripleList =[]
    
    for noun1 in nounLst:
        i = 1
        for noun2 in nounLst[i:]:
            #print("noun1 :: ", noun1, " :: noun2 :: ", noun2)
            if executeOR(getParentNodes(noun1.strip(), inXML), getParentNodes(noun2.strip(), inXML)):
                #print("Adding triple :: " , noun1.strip(), " ,  " , verbLst[0].strip(),  " ,  " ,noun2.strip())
                tripleList.append([noun1.strip(),verbLst[0].strip(),noun2.strip()]) #We are assuming that there is just one verb in a sentence.
            i = i + 1
    #print("tripleList :: ", tripleList)
    return tripleList


def extractTriples(verbLst, nounLst, xml):
    #print("nounLst :: ", nounLst)
    intree = etree.parse(StringIO(xml))
    return getTuples(nounLst, verbLst, intree)
