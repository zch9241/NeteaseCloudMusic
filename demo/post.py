import requests
import json
api_key = ''
language0 = 'chs'
language1 = 'eng'



def ocr_space_file(filename, api_key, overlay=False, language='eng'):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               'OCREngine': 5
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()



# Use examples:
res = json.loads(ocr_space_file(api_key = api_key,filename=r"C:\Users\Lenovo\Desktop\屏幕截图 2023-01-10 183243.png", language='eng'))
print(res["ParsedResults"][0]["TextOverlay"]["Lines"][0]["LineText"])

#print(test_file)
#{"ParsedResults":[{"TextOverlay":{"Lines":[{"LineText":"未登录","Words":[{"WordText":"未","Left":3.0,"Top":8.0,"Height":17.0,"Width":50.0},{"WordText":"登录","Left":3.0,"Top":8.0,"Height":17.0,"Width":50.0}],"MaxHeight":17.0,"MinTop":8.0}],"HasOverlay":true},"TextOrientation":"0","FileParseExitCode":1,"ParsedText":"未登录","ErrorMessage":"","ErrorDetails":""}],"OCRExitCode":1,"IsErroredOnProcessing":false,"ProcessingTimeInMilliseconds":"3436","SearchablePDFURL":"Searchable PDF not generated as it was not requested."}
#{"ParsedResults":[],"OCRExitCode":6,"IsErroredOnProcessing":true,"ErrorMessage":["Timed out waiting for results"],"ProcessingTimeInMilliseconds":"5890"}