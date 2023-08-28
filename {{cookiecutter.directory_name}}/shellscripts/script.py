#!/bin/python

import os
import random, string
import shutil

from sys import argv
import requests
from urllib.parse import urlparse
from zipfile import ZipFile

# the path to this python script
scriptDir=os.path.dirname(os.path.realpath(argv[0]))

# the tmp dir where files get downloaded to
tmpDir=scriptDir+"/tmp"

# root path of the dse cookie cutter
dseCokieCutterHome=scriptDir+"/.."

# data directory of the dse cookie cutter
dataDir=dseCokieCutterHome+"/data"

saxonTargetPath=dseCokieCutterHome+"/saxon"
imprintTargetPath=dseCokieCutterHome+"/data/imprint.xml"
staticSearchTargetPath=dseCokieCutterHome+"/static-search"
stopwordsTargetPath=dseCokieCutterHome+"/words.txt"

def rand(length=10):
    s = string.lowercase+string.digits
    return (''.join(random.sample(s, length)))


def fileInfoFromUrl(url):
    """derive filename information from a URL"""
    parsedUrl = urlparse(url)
    fn = os.path.basename(parsedUrl.path)
    basename = os.path.splitext(fn)[0]
    ext = os.path.splitext(fn)[1]
    return {
        "url": url,
        "basename": basename,
        "extension": ext,
        "filename" :fn
    }


def downloadAndStore(url, target=None, force=False):   
    """Download and store the resource located at url.
    
    
    Keyword arguments:
    url -- the url of the resource to be downloaded
    target -- path where the downloaded resource should be saved to. Defaults to tmpDir.
    force -- download file even if it already exists in the target directory
    """

    if target is None:
        fileInfo = fileInfoFromUrl(url)
        fn = fileInfo["filename"]
        dlFilePath = tmpDir + "/" + fn
    else:
        dlFilePath = target
    
    real_path = os.path.realpath(dlFilePath)
    dir_path = os.path.dirname(real_path)
    # create output path if it doesn't exist yet
    if os.path.exists(dlFilePath) and force != True:
        print("File "+dlFilePath+" was already downloaded.")
        return dlFilePath
    else:
        if os.path.exists(dlFilePath) and force == True:
            print("Forcing download of existing file "+dlFilePath)
        else:
            os.makedirs(dir_path, exist_ok=True)
            print("Downloading file "+dlFilePath)
        payload = requests.get(url).content
        open(dlFilePath, 'wb').write(payload)
        return dlFilePath
    
def downloadAndUnzip(url, target=None, force=False):    
    """"Download a zip file and unpack it.
    
    Keyword arguments: 
    -- target: the directory to unzip the content to
    -- force: see downloadAndStore().
    """
    fileInfo = fileInfoFromUrl(url)
    if target is None:
        fn=fileInfoFromUrl(url)["filename"]
        if fn is None:
            targetDirPath=tmpDir+"/"+rand(8)
        else:
            targetDirPath=tmpDir+"/"+fn
    else:
        targetDirPath=target
    
    # download zipfile to temporary location
    zipFilePath = downloadAndStore(url, target=tmpDir+"/tmp.zip")
    ZipFile(zipFilePath).extractall(path=targetDirPath)
    
    return targetDirPath




def dl_imprint(redmineID=18716, target=tmpDir+"/imprint.xml"):
    """Create imprint.xml by downloading an HTML page containing the imprint of the target service. 
    
    Keyword arguments:
    -- redmineID= the ID of the service in the database of services 
    -- target=the path where the file should be saved to
    """
    imprint_url = f"https://shared.acdh.oeaw.ac.at/acdh-common-assets/api/imprint.php?serviceID={redmineID}"
    path_to_imprint_html = downloadAndStore(imprint_url, target=tmpDir+"/imprint.html")   
    
    with open(target, "w", encoding="utf-8") as f:
        with open(path_to_imprint_html, "r", encoding="utf-8") as imprint_html:
            content = f'<?xml version="1.0" encoding="UTF-8"?><root>{imprint_html.read()}</root>'
            f.write(content)

def dl_saxon(target):
    saxon_url = "https://sourceforge.net/projects/saxon/files/Saxon-HE/9.9/SaxonHE9-9-1-7J.zip/download"
    saxon_dl_path = downloadAndUnzip(saxon_url, target="tmp/saxon")
    shutil.move(saxon_dl_path, saxonTargetPath)

def dl_staticSearch(target):
    """Download and install Static Search plugin"""
    #   rm -rf ./static-search
    # rm -rf ./tmp
    print("downloading static search")
    staticSearch_url="https://github.com/projectEndings/staticSearch/archive/refs/tags/v1.4.1.zip"
    downloadAndUnzip(url=staticSearch_url, target=staticSearchTargetPath)
    # mv ./tmp/staticSearch-1.4.1 ./static-search && rm -rf ./tmp#

    print("get stopword list")
    stopwords_url="https://raw.githubusercontent.com/stopwords-iso/stopwords-de/master/stopwords-de.txt"
    downloadAndStore(stopwords_url, target=stopwordsTargetPath)


def setup():
    """This function sets up necessary directories."""
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)


def teardown():
    """This function cleans up temporary files."""
    for i in os.listdir(tmpDir):
        os.remove(tmpDir+"/"+i)
    os.rmdir(tmpDir)

setup()

dl_imprint(target=imprintTargetPath)
dl_saxon(target=saxonTargetPath)
dl_staticSearch(target=staticSearchTargetPath)
teardown()