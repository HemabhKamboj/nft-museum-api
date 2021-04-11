# NFT Museum API
APIs serving nft museum app. Powered by Flask. Link to frontend repo: https://github.com/dhruv10/nft-museum


## Setup
1. Run the [following](DB Initialization commands) commands in your SQL Database
2. For local setup better to use Pycharm as IDE because even when creating virtual environment, flask run out of virtual environment.
3. After setting project up in Pycharm, open terminal within Pycharm and run `pip install -r requirements.txt`
4. Run `export DB_URI=<DB_URI>` or enter `DB_URI` in `config.py`
5. Run `export FLASK_APP=app.py` and `export FLASK_DEBUG=1` in root directory of project from within the Pycharm terminal.

#### DB Initialization commands

  ```CREATE TABLE "users" (
	"id" serial NOT NULL,
	"valora_id" varchar(255) NOT NULL UNIQUE,
	"name" varchar(255) NOT NULL,
	"created_at" TIMESTAMP NOT NULL,
	"updated_at" TIMESTAMP,
	"img_url" TEXT,
	"is_archived" BOOLEAN NOT NULL DEFAULT 'False',
	CONSTRAINT "users_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "collections" (
	"id" serial NOT NULL,
	"name" varchar(255) NOT NULL UNIQUE,
	"created_by" int NOT NULL,
	"description" TEXT,
	"no_of_saves" int,
	"is_archived" BOOLEAN NOT NULL DEFAULT 'False',
	"tags" varchar ARRAY[] NOT NULL,
	CONSTRAINT "collections_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "nfts" (
	"id" serial NOT NULL,
	"name" varchar(255) NOT NULL UNIQUE,
	"token_id" varchar(255) NOT NULL,
	"created_at" TIMESTAMP NOT NULL,
	"updated_at" TIMESTAMP,
	"img_url" TEXT,
	"perma_link" TEXT,
	CONSTRAINT "nfts_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "nft_to_ collection" (
	"nft_id" int NOT NULL,
	"collection_id" int NOT NULL,
	"nft_added_at" TIMESTAMP NOT NULL,
	"nft_updated_at" TIMESTAMP,
	"nft_archived" BOOLEAN NOT NULL DEFAULT 'False'
) WITH (
  OIDS=FALSE
);



CREATE TABLE "saved_collections" (
	"user_id" int NOT NULL,
	"collection_id" int NOT NULL,
	"collection_added_at" TIMESTAMP NOT NULL,
	"collection_updated_at" TIMESTAMP,
	"is_archived" BOOLEAN NOT NULL DEFAULT 'False'
) WITH (
  OIDS=FALSE
);



CREATE TABLE "saved_nfts" (
	"user_id" int NOT NULL,
	"nft_id" int NOT NULL,
	"nft_saved_at" TIMESTAMP NOT NULL,
	"nft_updated_at" TIMESTAMP,
	"is_archived" BOOLEAN NOT NULL DEFAULT 'False'
) WITH (
  OIDS=FALSE
);




ALTER TABLE "collections" ADD CONSTRAINT "collections_fk0" FOREIGN KEY ("created_by") REFERENCES "users"("id");


ALTER TABLE "nft_to_ collection" ADD CONSTRAINT "nft_to_ collection_fk0" FOREIGN KEY ("nft_id") REFERENCES "nfts"("id");
ALTER TABLE "nft_to_ collection" ADD CONSTRAINT "nft_to_ collection_fk1" FOREIGN KEY ("collection_id") REFERENCES "collections"("id");

ALTER TABLE "saved_collections" ADD CONSTRAINT "saved_collections_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "saved_collections" ADD CONSTRAINT "saved_collections_fk1" FOREIGN KEY ("collection_id") REFERENCES "collections"("id");

ALTER TABLE "saved_nfts" ADD CONSTRAINT "saved_nfts_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "saved_nfts" ADD CONSTRAINT "saved_nfts_fk1" FOREIGN KEY ("nft_id") REFERENCES "nfts"("id");
```