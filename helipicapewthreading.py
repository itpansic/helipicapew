# FetchParge-code originated by Stereo (stereo_minoprint.py)
# personally I have no clue what I'm doing, so please call in if you see improvements
import ac
import json
import threading

try:
  import urllib.request
  import urllib.parse
except Exception as ex:
  ac.log("helipicapew::urllib not imported: {}".format(str(ex)))

# We'll store any result we get from the MR backend here, it's assumed that
# some other piece of code just uses this AND SETs TO NONE THEN
lastResult = None
requestPending = False

# this is the template for the web request
urlstr = ""

def initConstants():
    global urlstr

    urlstr = 'http://app.minorating.com:806/minodata/drivers/?serverIp={}&serverPort={}'.format(ac.getServerIP(), ac.getServerHttpPort())

def requestMinoratingData():
    global requestPending

    if requestPending == False:
        ac.log("helipicapew::FetchPage.Start(): " + urlstr)
        requestPending = True
        FetchPage().start()

class FetchPage(threading.Thread):
    def run(self):
        global requestPending, lastResult, lastMRSessionId, driverSteamId

        try:
            # this replaces spaces with %20 and so forth
            url = urllib.parse.quote(urlstr, safe="%/:=&?~#+!$,;'@()*[]")
            with urllib.request.urlopen(url, timeout=5) as mresponse:
                request_resp = mresponse.read().decode('utf-8')
                json_data = json.loads(request_resp)
                lastResult = json_data
        except Exception as e:
            lastResult = {}
            lastResult["errorMsg"] = "web request error {}".format(e)
        requestPending = False