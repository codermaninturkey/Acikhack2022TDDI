import base64
import os
import re
import time
from datetime import datetime
import multiprocessing
from typing import Optional

import numpy as np
import pytesseract

from io import BytesIO
from PIL import Image
from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel
from starlette.responses import JSONResponse

routes = APIRouter()

ConfidenceList = [] #bu değişken ocr edilen belgedeki her bir kelime için confidence değeri tutar.

class Data(BaseModel):
    content: Optional[str] = ""
    stats: Optional[bool] = False
    deep: Optional[bool] = False # bu alan ocr işleminin kalitesi açısından; True durumda kaliteli tarama yapar süre uzar, False durumda hızlı ve default tarama yapar.
    page: Optional[str] = "0"

class ByteModel(BaseModel):
    applicationName: Optional[str] = "byte-service"
    data: Data

def confidenceProcess(text, confidence):
    ConfidenceList.append(confidence)
    return text

def getConfidence():

    totalConf = 0

    for conf in ConfidenceList:

        totalConf+= float(conf)

    return totalConf / len(ConfidenceList)

def getFileExtension(filename):
    import os
    split_tup = os.path.splitext(filename)
    return split_tup[1]

def detailsOCR(image, deep):

    ConfidenceList.clear()

    import pandas as pd

    if deep:
        d = pytesseract.image_to_data(image, lang="tur", output_type='data.frame', config='--psm 6')
    else:
        d = pytesseract.image_to_data(image, lang="tur", output_type='data.frame')

    pd.set_option('display.max_rows', None)

    df = pd.DataFrame(data=d)

    df = df.dropna()

    df = df.drop(["level", "top", "left", "width", "height"], axis=1)

    sonuc = ""

    for page in df.page_num.unique():

        page_df = df.where(df["page_num"] == page)

        for block in range(len(page_df.block_num.unique())):

            activeBlock = block + 1

            block_df = page_df.where(page_df["block_num"] == activeBlock).dropna()

            for par in range(len(block_df.par_num.unique())):

                activePar = par + 1

                par_df = block_df.where(block_df["par_num"] == activePar).dropna()

                sonuc += " ".join([confidenceProcess(text, confidence) for text, confidence in zip(par_df['text'],par_df['conf'])])

                sonuc = sonuc + "\n\n"

    return sonuc

def poolOCR(tif, page, stats,deep):

    tif = Image.open(tif)

    tif.seek(int(page))

    tifff = np.array(tif)

    confidence = 0

    if stats == True:

        text = detailsOCR(tifff,deep)

        confidence = getConfidence()

        return {"pageNumber": page, "confidence": confidence, "text": str(text)}


    if deep == True: #derin ocr yapılacağını kontrol eder, default olarak false kullanılır

        text = pytesseract.image_to_string(tifff, lang="tur", config='--psm 6')
    else:
        text = pytesseract.image_to_string(tifff, lang="tur")

    return {"pageNumber":page,"confidence": confidence, "text": str(text)}

@routes.post("/multipart")

async def from_file(file: UploadFile = File(None), pageNumbers: str = Form(""), stats: bool = Form("False"), deep: bool = Form("False") ):

    page = pageNumbers

    if getFileExtension(file.filename) in [".tif",".tiff"]:

        try:
            content = await file.read()

            tif = Image.open(BytesIO(content))

            pageCounts = tif.n_frames  # default total page count

            image_list = list(range(pageCounts))

            if page == "full":  # page = full ise tüm belgeyi ocr eder

                image_list = list(range(pageCounts))

            elif len(page.strip()) == 0:  # page = içerik boş ise ise tüm belgeyi ocr eder

                image_list.clear()
                image_list.append(0)

            elif not len(page.strip()) == 0:  # page alanı gönderilmemiş ise ilk sayfayı ocr eder

                pageError = 0

                pages = page.split(",")

                for i in range(len(pages)):

                    if int(pages[i]) > pageCounts:
                        pageError = 1

                    if int(pages[i]) < 0:
                        pageError = 2

                if pageError == 1:
                    return {"data": {"status": False, "filename": None,
                                     "error": "Belirttiğiniz sayfalar içerisinde toplam sayfa boyutundan büyük sayfa numaraları mevcuttur."}}

                if pageError == 2:
                    return {"data": {"status": False, "filename": None,
                                     "error": "Belirttiğiniz sayfalar içerisinde 0 veya daha küçük numaraları sayfalar mevcuttur. "}}

                image_list.clear()

                for page in pages:
                    image_list.append(page)


            input_list = [[BytesIO(content), image_list[i], stats,deep] for i in range(len(image_list))]

            start_time = time.time()

            if len(image_list) == 1: pool = multiprocessing.Pool(processes=1)
            elif len(image_list) > 1 and len(image_list) < 6 : pool = multiprocessing.Pool(processes=len(image_list))
            elif len(image_list) > 6: pool = multiprocessing.Pool(processes=6)
            else:  pool = multiprocessing.Pool(processes=3)

            returnPool = pool.starmap(poolOCR, input_list)

            pool.close()

            pool.join()

            end_time = time.time()

            return JSONResponse(content={"data":{"time": end_time - start_time, "filename": file.filename, "ocrResponses": returnPool, "status": "SUCCESS"}}, status_code=200)

        except Exception as e:

            return JSONResponse(content={"data":{"status": False, "filename": "", "error": str(e)}}, status_code=200)
    if getFileExtension(file.filename) in [".jpeg", ".jpg", ".png", ".bmp", ".gif"]:

        try:
            content = await file.read()

            image_list = list(range(1))

            processID = str(time.time()).replace('.','')

            input_list = [[BytesIO(content), image_list[i], stats,deep] for i in range(len(image_list))]

            start_time = time.time()

            pool = multiprocessing.Pool(processes=1)# burası tek belge için tek çekirdek planlaması yapıldığı için bu sekılde duzenlendı

            returnPool = pool.starmap(poolOCR, input_list)

            pool.close()

            pool.join()

            end_time = time.time()

            return JSONResponse(content={"data":{"time": end_time - start_time, "filename": file.filename, "ocrResponses": returnPool, "status": "SUCCESS"}}, status_code=200)

        except Exception as e:
            return JSONResponse(content={"data":{"status": False, "filename": "", "error": str(e)}}, status_code=200)


    else:
        return JSONResponse(content={"data":{"status": False, "filename": "{0}".format(file.filename), "error": "Uyumsuz dosya formatı. Bunları kllanabilirsiniz {0}".format(str([".pdf",".jpeg", ".jpg", ".png", ".bmp", ".gif",".tif",".tiff"]))}}, status_code=200)

