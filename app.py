from config import DB_URI
from flask import Flask, request, render_template, redirect, jsonify, flash, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
import sys

app = Flask(__name__)
app.config['DEBUG'] = True

engine = create_engine(DB_URI)
db = scoped_session(sessionmaker(bind=engine))
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


@app.route("/user/create", methods=["POST"])
def create_user():
    parameters = request.json
    user_name = parameters.get('user_name')
    valora_id = parameters.get('valora_id')
    try:
        db.execute("INSERT INTO users (name, valora_id, created_at) VALUES (:name, :valora_id, :created_at)",
                   {"name": user_name,
                    "valora_id": valora_id,
                    "created_at": "NOW()"
                    })
        db.commit()
        code = 200
        message = "User Added Successfully"
    except Exception as e:
        logger.error("Unable to Add user with error :", e)
        code = 400
        message = str(e)
    data = {'status_code': code, 'message': message}
    return make_response(data, code)


@app.route("/user/", methods=["GET"], endpoint='user')
def get_user():
    valora_id = request.args.get('id')
    try:
        rows = db.execute("SELECT * FROM users WHERE valora_id = :valora_id and is_archived = :is_archived ",
                          {"valora_id": valora_id,
                           "is_archived": "f"})

        result = rows.fetchone()
    except Exception as e:
        logger.error("Unable to get user :", e)
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    if not result:
        code = 404
        message = "User Not found"
        data = {'status_code': code, 'message': message}
    else:
        results = [{"id": result[0], "valora_id": result[1], "name": result[2], "created_at": result[3],
                    "updated_at": result[4]}]
        code = 200
        data = {"results": results, 'status_code': code}
    return make_response(data, code)


@app.route("/collection/create", methods=["POST"])
def create_collection():
    parameters = request.json
    collection_name = parameters.get('collection_name')
    collection_description = parameters.get('collection_description')
    tags = parameters.get('tags')
    nft_tokens = parameters.get('nft_tokens')
    created_by = parameters.get('created_by')
    resulted_nft_ids = []

    # TODO : Handle if created by is an archived user

    # TODO : Make insertion of collections and nft a transaction
    try:
        rows = db.execute(
            "INSERT INTO collections (name, description, created_at, no_of_saves, tags, created_by) VALUES ("
            ":name, :description, :created_at, :no_of_saves, :tags, :created_by) RETURNING id",
            {"name": collection_name,
             "description": collection_description,
             "created_at": "NOW()",
             "no_of_saves": 0,
             "tags": tags,
             "created_by": created_by
             })
        collection_id = rows.fetchone()[0]
        print('collection_id', collection_id)
        for i in nft_tokens:
            nft_row = db.execute("INSERT INTO nfts (name, token_id, created_at, img_url, perma_link) VALUES ("
                                 ":name, :token_id, :created_at, :img_url, :perma_link) RETURNING id ",
                                 {"name": i.get('name'),
                                  "token_id": i.get('token_id'),
                                  "created_at": "NOW()",
                                  "img_url": i.get('img_url'),
                                  "perma_link": i.get('perma_link')
                                  })
            resulted_nft_ids.append(nft_row.fetchone()[0])
        print('resulted_nft_ids', resulted_nft_ids)
        for j in resulted_nft_ids:
            db.execute("INSERT INTO nft_to_collection (nft_id, collection_id, nft_added_at) VALUES ("
                       ":nft_id, :collection_id, :nft_added_at)",
                       {"nft_id": j,
                        "collection_id": collection_id,
                        "nft_added_at": "NOW()"
                        })
        db.commit()
        code = 200
        message = "Collection Added Successfully"
    except Exception as e:
        logger.error("Unable to Add Collection with error :", e)
        code = 400
        message = str(e)
    data = {'status_code': code, 'message': message}
    return make_response(data, code)


@app.route("/collections/all/", methods=["GET"], endpoint='collections')
def get_all_collections():
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    first_n_nfts = request.args.get('first_n_nfts')
    # TODO : Add order by in below query
    try:
        collections = db.execute("SELECT id, name, description, no_of_saves,tags, created_by  FROM collections WHERE "
                                 "is_archived = 'f' order by no_of_saves DESC limit :limit offset :offset",
                                 {"limit": limit,
                                  "offset": offset})

        collections_data = collections.fetchall()
        data = []
        for res in collections_data:
            data.append({
                "id": res[0],
                "name": res[1],
                "description": res[2],
                "no_of_saves": res[3],
                "tags": res[4],
                "created_by": res[5]
            })
        for i in data:
            # Find total no of nfts
            count_of_nfts = db.execute("SELECT COUNT(nft_id) from nft_to_collection where collection_id = "
                                       ":collection_id",
                                       {"collection_id": i.get("id")})
            count_of_nft = count_of_nfts.fetchone()[0]
            i['no_of_total_nfts'] = count_of_nft

            # Find meta of n nfts
            first_n_nfts_urls_data = db.execute("SELECT b.* from nft_to_collection as a  "
                                                "LEFT JOIN nfts as b on a.nft_id = b.id  where "
                                                "collection_id = :collection_id LIMIT :LIMIT",
                                                {"collection_id": i.get("id"),
                                                 "LIMIT": first_n_nfts})
            fetch_all = first_n_nfts_urls_data.fetchall()
            nfts = []
            for each in fetch_all:
                nfts.append({
                    "id": each[0],
                    "name": each[1],
                    "token_id": each[2],
                    "created_at": each[3],
                    "updated_at": each[4],
                    "img_url": each[5],
                    "perma_link": each[6]
                })
            i['nfts'] = nfts

            # Find created_by name of collection
            created_by_data = db.execute("SELECT name from users where id = :created_by",
                                         {"created_by": i['created_by']})

            created_by_name = created_by_data.fetchone()[0]
            i['created_by'] = created_by_name
        results = []
        for row in data:
            print(row)
            results.append([x for x in row])  # or simply data.append(list(row))
    except Exception as e:
        logger.error("Unable to get collections :", e)
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    if not data:
        code = 404
        message = "Collections Not found"
        data = {'status_code': code, 'message': message}
    else:
        code = 200
        data = {"results": data, 'status_code': code}
    return make_response(data, code)
