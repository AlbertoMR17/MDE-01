from flask import Blueprint, request, make_response
from . import controller
import base64

bp = Blueprint('images', __name__, url_prefix='/')

@bp.post("/image")
def image():

    #QUERY PARAMETERS
    min_confidence = request.args.get("min_confidence", "80")
    

    #INPUT CHECKS
    if not request.is_json or "data" not in request.json:
        return make_response({"description": "Debes incluir la imagen en base64 como un campo llamado data en el body"}, 400)

    b64str_input = request.json["data"]

    b64str_path_size_id=controller.image_path_size_id(b64str_input)
    picture_id,date,size =b64str_path_size_id
    print(b64str_path_size_id)

    b64str_url = controller.image_url(b64str_input)

    #LEER UNA IMAGEN DEL VOLUMEN DE DOCKER(descomentar return json)
    #b64str_url,image_vol = controller.image_url(b64str_input)
    #b64str_02 = base64.b64encode(image_vol).decode()


  
    b64str_tag = controller.image_tag(b64str_url,min_confidence,picture_id,date)

    print(b64str_tag)   
    

    return {
        "id" : picture_id,
        "size" : size,
        "date" : date,
        "tags" : b64str_tag,
        "image" : b64str_input[:20]
    }






@bp.get("/images")
def images():

    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    tags = request.args.get("tags")


    if not tags and not min_date and not max_date:
        print(f"No ha proporcionado ningún tag, ni ninguna fecha")

        return [{"images":"No se han proporcionado tags ni fechas"}]

    #Nos proporcionan max_date
    if min_date is None and max_date:
        print(f"Solo se mostrarán las imágenes desde {max_date} hacia atrás")

        data_max_date=controller.max_date(max_date)

        return data_max_date

    #Nos proporcionan min_date
    if max_date is None and min_date:
        print(f"Solo se mostrarán las imágenes desde {min_date} en adelante")

        data_min_date=controller.min_date(min_date)

        return data_min_date

    #Nos proporcionan min_date y max_date
    if min_date and max_date:
        print(f"Se muestran las imágenes entre {min_date} y {max_date}")

        data_interval_date=controller.interval_date(min_date,max_date)

        return data_interval_date

    #Se proporciona la variable tags vacía
    if not tags: 
         print(f"No ha proporcionado ningún tag")

         return [{"images":"No se han proporcionado tags."}]

    if tags:
        print(f"Solo se mostrarán las imágenes que contengan todos los tags:{tags}")

        data_tags = controller.tags(tags)
        return data_tags

    

@bp.get("/image/<int:id>")

def get_image(id):

    data_image = controller.get_image(id)
    print(data_image)
    return data_image















