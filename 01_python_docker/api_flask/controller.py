from . import models
import base64
from PIL import Image
import io
import datetime
from imagekitio import ImageKit
import json
import requests
from json.decoder import JSONDecodeError
import datetime
import os
import random
from flask import jsonify

#POST IMAGE---------------------------------------------

def image_url(b64str_input):

    with open("credentials.json","r") as f:
        credentials = json.load(f)
    
    imagekit = ImageKit(
        private_key = credentials["private_key"],
        public_key = credentials["public_key"],
        url_endpoint = credentials["url_endpoint"]
    )


    #upload the image
    upload_info = imagekit.upload(file = b64str_input , file_name ="01_imagen.png" )
    url = upload_info.url

    return url

    #return url,image_volume

def image_path_size_id(b64str_input):
    
    #SIZE
    decoded_image=base64.b64decode(b64str_input)
    size = len(decoded_image)/1024
    print(size)

    #ID
    id = random.randint(1000, 9999)
    print(id)

    #PATH
    #Usar ese mismo id para el nombre del archivo
    file_name = "image_"+f"{id}"+".png"
    print(file_name)
    path = models.save_image(decoded_image,file_name)
    print(path)

    print(f"Tamaño del archivo: {size} bytes")
    
    #DATE
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
    
    picture_id=models.pictures(id,path,date,size)

    return picture_id,date,size



    #Si queremos leer el archivo desde el volumen de docker, descomentar 
    #image_volume=models.image_to_volume(b64str_input,file_name)
    



def image_tag(b64str_url,min_confidence,picture_id,date):

    
    with open("credentials.json","r") as f:
        credentials = json.load(f)

    api_key = credentials["api_key"]
    api_secret = credentials["api_secret"]
    image_url = b64str_url



    try:
  
        response = requests.get(f"https://api.imagga.com/v2/tags?image_url={image_url}", auth=(api_key, api_secret))
        print(response.json())
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP


        # Intenta convertir min_confidence a un número de punto flotante
        min_confidence = float(min_confidence)
    except requests.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return []

    tags = [
        {   
            "tag": t["tag"]["en"],
            "confidence": t["confidence"]
        }
        for t in response.json()["result"]["tags"]
        if t["confidence"] > min_confidence

        ]


    models.tags(tags,picture_id,date)
    

    return tags


#GET IMAGES---------------------------------------------

def max_date(max_date):

    data_max_date=models.max_date(max_date)
    print(data_max_date)
    return data_max_date


def min_date(min_date):

    data_min_date=models.min_date(min_date)
    print(data_min_date)
    return data_min_date
    
def interval_date(min_date,max_date):

    data_interval_date=models.interval_date(min_date,max_date)
    print(data_interval_date)
    return data_interval_date


def tags(tags):

    tags_list=tags.split(',')
    print (tags_list)
    data_tags=models.tags_images(tags_list)
    return data_tags



def get_image(id):

    data_image = models.get_image(id)
    print("hola")
 

    return data_image




    # image_path=data_image.get("path")

    # try:
    #     with open(image_path, "rb") as image_file:
    #         image_content = image_file.read()

    #         # Encode the content as base64
    #         encoded_image = base64.b64encode(image_content).decode("utf-8")
    #         print(encoded_image[:20])
    #         #return encoded_image

    # except Exception as e:
    #     print(f"Error: {str(e)}")
    #     return None
