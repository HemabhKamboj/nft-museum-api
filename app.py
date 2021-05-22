import sys
import logging
from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import DB_URI

app = Flask(__name__)
cors = CORS(app)
app.config['DEBUG'] = True
app.config['CORS_HEADERS'] = 'Content-Type'

engine = create_engine(DB_URI)
db = scoped_session(sessionmaker(bind=engine))
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


@app.route("/user/create", methods=["POST"])
@cross_origin()
def create_user():
#this is a function to create user
    parameters = request.json
    user_name = parameters.get('user_name')
    valora_id = parameters.get('valora_id')
    valora_id = valora_id.lower()
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
@cross_origin()
def get_user():
    # this is a function to get user
    valora_id = request.args.get('id')
    try:
        rows = db.execute("SELECT * FROM users WHERE valora_id = :valora_id and is_archived = :is_archived ",
                          {"valora_id": valora_id,
                           "is_archived": "f"})

        result = rows.fetchone()
    except Exception as e:
        logger.error("Unable to get user :{e}".format(e=e))
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


@app.route("/collection/create", methods=["POST"], endpoint='crate_collection')
@cross_origin()
def create_collection():
    #this is a function to create collection
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
        logger.error("Unable to Add Collection with error :{e}".format(e=e))
        code = 400
        message = str(e)
    data = {'status_code': code, 'message': message}
    return make_response(data, code)


@app.route("/collections/all/", methods=["GET"], endpoint='collections')
@cross_origin()
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
            results.append([x for x in row])  # or simply data.append(list(row))
    except Exception as e:
        logger.error("Unable to get collections :{e}".format(e=e))
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


@app.route("/collection/save", methods=["POST"], endpoint='save_collection_to_user')
@cross_origin()
def save_collection_to_user():
    parameters = request.json
    collection_id = parameters.get('collection_id')
    user_id = parameters.get('user_id')
    try:
        db.execute(
            "INSERT INTO saved_collections (user_id, collection_id, collection_added_at) VALUES ("
            ":user_id, :collection_id, :collection_added_at )",
            {"user_id": user_id,
             "collection_id": collection_id,
             "collection_added_at": "NOW()"
             })
        db.execute("UPDATE collections SET no_of_saves = no_of_saves + 1 WHERE id = :collection_id",
                   {"collection_id": collection_id})

        db.commit()
        code = 200
        message = "Collection Saved Successfully"
    except Exception as e:
        logger.error("Unable to Save Collection with error :{e}".format(e=e))
        code = 400
        message = str(e)
    data = {'status_code': code, 'message': message}
    return make_response(data, code)


@app.route("/nft/save", methods=["POST"], endpoint='add_nft_to_user')
@cross_origin()
def save_collection_to_user():
    parameters = request.json
    nft_id = parameters.get('nft_id')
    user_id = parameters.get('user_id')
    try:
        db.execute(
            "INSERT INTO saved_nfts (user_id, nft_id, nft_saved_at) VALUES ("
            ":user_id, :nft_id, :nft_saved_at )",
            {"user_id": user_id,
             "nft_id": nft_id,
             "nft_saved_at": "NOW()"
             })

        db.commit()
        code = 200
        message = "NFT Saved Successfully"
    except Exception as e:
        logger.error("Unable to Save NFT with error :{e}".format(e=e))
        code = 400
        message = str(e)
    data = {'status_code': code, 'message': message}
    return make_response(data, code)


@app.route("/collection/", methods=["GET"], endpoint='get_collection_by_id')
@cross_origin()
def get_collection_by_id():
    collection_id = request.args.get('collection_id')
    # TODO : Add order by in below query
    try:
        collections = db.execute("SELECT id, name, description, no_of_saves,tags, created_by  FROM collections WHERE "
                                 "is_archived = 'f' and id = :collection_id",
                                 {"collection_id": collection_id})

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

            # Find meta of all nfts
            all_nfts = db.execute("SELECT b.* from nft_to_collection as a  "
                                  "LEFT JOIN nfts as b on a.nft_id = b.id  where "
                                  "collection_id = :collection_id",
                                  {"collection_id": i.get("id")})
            fetch_all = all_nfts.fetchall()
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
            results.append([x for x in row])  # or simply data.append(list(row))
    except Exception as e:
        logger.error("Unable to get collection :{e}".format(e=e))
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    if not data:
        code = 404
        message = "Collection Not found"
        data = {'status_code': code, 'message': message}
    else:
        code = 200
        data = {"results": data, 'status_code': code}
    return make_response(data, code)


@app.route("/collection/user/", methods=["GET"], endpoint='get_collection_by_user_id')
@cross_origin()
def get_collection_by_user_id():
    user_id = request.args.get('id')
    # TODO : Add order by in below query
    try:
        collections = db.execute("SELECT id, name, description, no_of_saves,tags, created_by  FROM collections WHERE "
                                 "is_archived = 'f' and created_by = :user_id",
                                 {"user_id": user_id})

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

            # Find meta of all nfts
            all_nfts = db.execute("SELECT b.* from nft_to_collection as a  "
                                  "LEFT JOIN nfts as b on a.nft_id = b.id  where "
                                  "collection_id = :collection_id",
                                  {"collection_id": i.get("id")})
            fetch_all = all_nfts.fetchall()
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
            results.append([x for x in row])  # or simply data.append(list(row))
    except Exception as e:
        logger.error("Unable to get collection :{e}".format(e=e))
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    if not data:
        code = 404
        message = "Collection Not found"
        data = {'status_code': code, 'message': message}
    else:
        code = 200
        data = {"results": data, 'status_code': code}
    return make_response(data, code)


@app.route("/collection/saved/", methods=["GET"], endpoint='get_saved_collection')
@cross_origin()
def get_collection_by_saved_user_id():
    user_id = request.args.get('user_id')
    # TODO : Add order by in below query
    collection_ids = []
    try:
        collections = db.execute("SELECT b.id, b.name, b.description, b.no_of_saves, b.tags, b.created_by  FROM "
                                 "saved_collections as a LEFT JOIN collections as b ON a.collection_id = b.id WHERE "
                                 "b.is_archived = 'f' and a.user_id = :user_id",
                                 {"user_id": user_id})

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

            # Find meta of all nfts
            all_nfts = db.execute("SELECT b.* from nft_to_collection as a  "
                                  "LEFT JOIN nfts as b on a.nft_id = b.id  where "
                                  "collection_id = :collection_id",
                                  {"collection_id": i.get("id")})
            fetch_all = all_nfts.fetchall()
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
            results.append([x for x in row])  # or simply data.append(list(row))
    except Exception as e:
        logger.error("Unable to get collection :{e}".format(e=e))
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    if not data:
        code = 404
        message = "No Saved collections found"
        data = {'status_code': code, 'message': message}
    else:
        code = 200
        data = {"results": data, 'status_code': code}
    return make_response(data, code)


@app.route("/nft/saved/", methods=["GET"], endpoint='get_saved_nfts')
@cross_origin()
def get_nft_by_saved_user_id():
    user_id = request.args.get('user_id')
    # TODO : Add order by in below query
    nft_ids = []
    try:
        nfts_data = db.execute("SELECT b.*  FROM "
                               "saved_nfts as a LEFT JOIN nfts as b ON a.nft_id = b.id WHERE "
                               "a.user_id = :user_id",
                               {"user_id": user_id})
        fetch_all = nfts_data.fetchall()
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
    except Exception as e:
        logger.error("Unable to get collection :{e}".format(e=e))
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    if not fetch_all:
        code = 404
        message = "No Saved collections found"
        data = {'status_code': code, 'message': message}
    else:
        code = 200
        data = {"results": nfts, 'status_code': code}
    return make_response(data, code)


@app.route("/search/", methods=["GET"], endpoint='search_collections')
@cross_origin()
def search_collections():
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    first_n_nfts = request.args.get('first_n_nfts')
    search_param = request.args.get('search_param')
    search_param_value = request.args.get('search_param_value')
    # TODO : Add order by in below query
    try:
        if search_param == 'name':
            collections = db.execute("SELECT id, name, description, no_of_saves,tags, created_by  FROM collections "
                                     "WHERE "
                                     "is_archived = 'f' AND name like :like order by no_of_saves DESC "
                                     "limit :limit offset :offset",
                                     {"like": '%' + search_param_value + '%',
                                      "limit": limit,
                                      "offset": offset})
        elif search_param == 'tag':
            collections = db.execute("SELECT id, name, description, no_of_saves,tags, created_by  FROM collections "
                                     "WHERE "
                                     "is_archived = 'f' AND name :tag=ANY(tags) order by no_of_saves DESC "
                                     "limit :limit offset :offset",
                                     {"tag": search_param_value,
                                      "limit": limit,
                                      "offset": offset})
        else:
            code = 400
            message = "Search Method not implemented"
            data = {'status_code': code, 'message': message}
            return make_response(data, code)
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
            results.append([x for x in row])  # or simply data.append(list(row))
    except Exception as e:
        logger.error("Unable to get collections :{e}".format(e=e))
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    code = 200
    data = {"results": data, 'status_code': code}
    return make_response(data, code)


@app.route("/tags/", methods=["GET"], endpoint='get_tags')
@cross_origin()
def get_tags():
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    try:
        tags = db.execute("SELECT distinct tags FROM collections "
                          "WHERE "
                          "is_archived = 'f' "
                          "limit :limit offset :offset",
                          {"limit": limit,
                           "offset": offset})
        all_data = tags.fetchall()
        resulted_tags = []
        for d in all_data:
            for i in d:
                print('i', i)
                for j in i:
                    resulted_tags.append(j)
        resulted_tags = list(dict.fromkeys(resulted_tags))
    except Exception as e:
        logger.error("Unable to get collections :{e}".format(e=e))
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
    code = 200
    data = {"results": resulted_tags, 'status_code': code}
    return make_response(data, code)


@app.route("/collection/edit/id/", methods=["POST"], endpoint='edit_meta')
@cross_origin()
def edit_collection_meta():
    parameters = request.json
    collection_id = parameters.get('collection_id')
    name = parameters.get('name')
    description = parameters.get('description')
    try:
        db.execute("UPDATE collections SET name = :name , description = :description, updated_at = :updated_at WHERE "
                   "id = :collection_id",
                   {"name": name,
                    "description": description,
                    "updated_at": "NOW()",
                    "collection_id": collection_id})
        db.commit()
    except Exception as e:
        logger.error("Unable to get collections :{e}".format(e=e))
        code = 400
        message = str(e)
        data = {'status_code': code, 'message': message}
        return make_response(data, code)
    code = 200
    data = {"message": "Collection Updated Successfully", 'status_code': code}
    return make_response(data, code)
