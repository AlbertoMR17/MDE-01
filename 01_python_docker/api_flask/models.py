# operations = []
from sqlalchemy import create_engine, text
from flask import jsonify
import os
import base64

#POST IMAGE----------------------------------------------------------

try:

    #⚠️localhost por el nombre del contenedor cuando se haga en docker-compose
    engine = create_engine('mysql+pymysql://mbit:mbit@localhost:3306/Pictures')
    print(f"Connection created successfully: {engine.url}")
except Exception as ex:

 	print("Connection could not be made due to the following error: \n", ex)


def pictures(id, path, date, size):


    picture_data = [
        {'id': id, 'path': path, 'date': date, 'size': size},
    ]
    query = text("INSERT INTO pictures (id, path, date, size) VALUES (:id,:path,:date,:size)")

    try:

        with engine.connect() as conn:
            conn.execute(query,picture_data)
            conn.commit()
            print("Data inserted successfully")
            picture_id = id
            return picture_id


    except Exception as e:

        print(f"error {str(e)}")
        return jsonify({"error":str(e)}),500


def tags(tags,picture_id,date):



    query = text("INSERT INTO tags (tag, picture_id, confidence, date) VALUES (:tag,:picture_id,:confidence,:date)")

    try:

        with engine.connect() as conn:
            for tag_info in tags:
                 conn.execute(query,[{'tag':tag_info['tag'], 'picture_id':picture_id, "confidence":tag_info['confidence'],"date":date}])
            conn.commit()
            print("Data inserted successfully")
        return {"message": "Data inserted successfully"}

    except Exception as e:

        print(f"error {str(e)}")
        return jsonify({"error":str(e)}),500





def save_image(decoded_image,file_name):



    volume_path = r"/var/lib/mysql"

    full_path = os.path.join(volume_path,file_name).replace('\\', '/')

    # Asegurarse de que el directorio exista
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    #Save the image in the volume
    with open(full_path,"wb") as f:
        f.write(decoded_image)

    print(f"Imagen guardada en: {full_path}")




    return full_path

    #LEER LA IMAGEN DESDE EL VOLUMEN
    # Verificar si el archivo existe antes de intentar leerlo
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            image_bytes = f.read()

    #         return image_bytes


#GET IMAGES-----------------------------------------------------

def max_date(max_date):

    query = text("""SELECT p.id, p.size, t.tag, t.confidence, p.date AS picture_date
                    FROM pictures p
                    LEFT JOIN tags t ON p.id = t.picture_id
                    WHERE p.date < :max_date
                    ORDER BY p.date DESC, p.id, t.tag""")
    try:

        with engine.connect() as conn:
            result=conn.execute(query, [{'max_date':max_date}])
            rows = result.fetchall()
            data = []
            for row in rows:
                data.append({
                    'id': row.id,
                    'size': row.size,
                    'tag': row.tag,
                    'confidence': row.confidence,
                    'picture_date': str(row.picture_date)
                })

            print("Query executed successfully")
        return jsonify({"data": data})


    except Exception as e:

        print(f"error {str(e)}")
        return jsonify({"error":str(e)}),500


def min_date(min_date):

    query = text("""SELECT p.id, p.size, t.tag, t.confidence, p.date AS picture_date
                    FROM pictures p
                    LEFT JOIN tags t ON p.id = t.picture_id
                    WHERE p.date >= :min_date
                    ORDER BY p.date ASC, p.id, t.tag""")
    try:
        with engine.connect() as conn:
            result = conn.execute(query, [{'min_date':min_date}])
            rows = result.fetchall()

            data = []
            for row in rows:
                data.append({
                    'id': row.id,
                    'size': row.size,
                    'tag': row.tag,
                    'confidence': row.confidence,
                    'picture_date': str(row.picture_date)
                })

            print("Query executed successfully")

        return jsonify({"data": data})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def interval_date(min_date,max_date):

    query = text("""SELECT p.id, p.size, t.tag, t.confidence, p.date AS picture_date
                    FROM pictures p
                    LEFT JOIN tags t ON p.id = t.picture_id
                    WHERE p.date BETWEEN :min_date AND :max_date
                    ORDER BY p.date ASC, p.id, t.tag""")
    try:
        with engine.connect() as conn:
            result = conn.execute(query, [{'min_date':min_date, 'max_date': max_date}])
            rows = result.fetchall()

            data = []
            for row in rows:
                data.append({
                    'id': row.id,
                    'size': row.size,
                    'tag': row.tag,
                    'confidence': row.confidence,
                    'picture_date': str(row.picture_date)
                })

            print("Query executed successfully")

        return jsonify({"data": data})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def tags_images(tags_list):

    # query = text("""SELECT p.id, p.size, t.tag, t.confidence, p.date AS picture_date
    #                 FROM pictures p
    #                 LEFT JOIN tags t ON p.id = t.picture_id
    #                 ORDER BY p.date ASC, p.id, t.tag""")



    query = text("""SELECT p.id, p.size, p.date AS picture_date, t.tag, t.confidence
                FROM pictures p
                JOIN tags t ON p.id = t.picture_id
                WHERE p.id IN (
                    SELECT picture_id
                    FROM tags
                    WHERE tag IN :tags_list
                    GROUP BY picture_id
                    HAVING COUNT(DISTINCT tag) = :num_tags
                )
                ORDER BY p.date ASC, p.id""")


    try:
        with engine.connect() as conn:

            result = conn.execute(query,{'tags_list':tags_list,'num_tags':len(tags_list)})
            print(result)
            rows = result.fetchall()
 
            data = []
            if not rows:
                print("La consulta no devolvió ningún valor")
            else:
            
                for row in rows:
                             
                    #if all(tag in [row.tag] for tag in tags_list):
                    #if all(tag == row.tag for tag in tags_list) and row.tag is not None:
                    #if row is not None:

                     data.append({
                        'id': row.id,
                        'size': row.size,
                        'tag': row.tag,
                        'confidence': row.confidence,
                        'picture_date': str(row.picture_date)
                     })

            tags_obtained = set(tag['tag'] for tag in data)
            if set(tags_list) != tags_obtained:
                print("No todas las tags coinciden con las de la imagen")
                return jsonify({"error": "No todas las tags coinciden con las de la imagen"}), 400

            print("Query executed successfully")
            print("A continuacion se muestra la respuesta")
            print(data)

        return jsonify({"data": data})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500



def get_image(id):


    query = text("""SELECT p.id, p.size, p.date AS picture_date, p.path,
                          t.tag, t.confidence
                   FROM pictures p
                   LEFT JOIN tags t ON p.id = t.picture_id
                   WHERE p.id = :picture_id""")
    
    try:
        print("prueba 1")
        with engine.connect() as conn:
            result = conn.execute(query, {'picture_id': id})
            rows = result.fetchall()

            if not rows:
                return jsonify({"error": "Imagen no encontrada"}), 404

            tags = [{"tag": row.tag, "confidence": row.confidence} for row in rows if row.tag is not None]

            with open(rows[0].path, "rb") as image_file:
                image_content = image_file.read()

        
                encoded_image = base64.b64encode(image_content).decode("utf-8")

            image_info = {
                "id": rows[0].id,
                "size": rows[0].size,
                "date": str(rows[0].picture_date),
                "data" : encoded_image,
                "tags": tags
            }

            print("Query executed successfully")
            print(image_info)
            return jsonify(image_info)

    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return jsonify({"error": "Error executing query"}), 500

