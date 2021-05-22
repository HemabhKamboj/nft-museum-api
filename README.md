# NFT Museum API



> NFT Museum is a mobile first platform for art lovers to curate their favourite digital art.

## Table of contents
- [What is  NFT Museum?](#what)
- [Why  NFT Museum?](#why)
- [User Flows](#user_flows)
- [⛏️ Built Using](#built_using)
- [✍️ Authors](#authors)
- [Setup](#setup)


###  What is NFT Museum ? <a name = "what"></a>

NFT Museum is a mobile first platform authenticated by multiple Crypto Wallets including Valora for art lovers to curate their favourite digital art pieces as a collection and be shared to community. A curator ( user who creates collection) can add multiple NFTs from OpenSea and create a collection by theme, asthetics or free will, just like a Spotify playlists !
These collections are visible to everyone, searchable by Tags and number of likes.

###  Why NFT Museum? <a name = "why"></a>

With mind bogling numbers of NFT enabled digital art minted each day, it is harder and harder for collectors to find there next collection piece, NFT Museum helps you to discover the precious pearls from the "Open Sea".
You can also save your favourite collections and NFTs to your librar in single tap which can be easily accessible anytime.

## User flows <a name = "user_flows"></a>


## ⛏️ Built Using <a name = "built_using"></a>

-   [React JS](https://reactjs.org/) - A JavaScript library for building user interfaces
-   [Ant Design](https://ant.design//) - A React UI library that has a plethora of easy-to-use components that are useful for building elegant user interfaces
-   [Flask ](https://palletsprojects.com/p/flask/) - A python based lightweight WSGI web application framework.
-   [Open Sea APIs](https://docs.opensea.io/reference) - Official APIs built on [Open Sea](https://https://opensea.io/)
-   [Valora](https://valoraapp.com/) - Crypto Mobile First Wallet based on [Celo](https://celo.org/)
-   [Contractkit](https://github.com/celo-tools/use-contractkit/) - SDK for helping wallet integration

### Link for Frontend Repository
[@nft-museum](https://github.com/dhruv10/nft-museum)


## Setup <a name = "setup"></a>
1. Run the [DB Initialization](#db_commands) commands in your SQL Database
2. For local setup better to use Pycharm as IDE because even when creating virtual environment, flask run out of virtual environment.
3. After setting project up in Pycharm, open terminal within Pycharm and run `pip install -r requirements.txt`
4. Run `export DB_URI=<DB_URI>` or enter `DB_URI` in `config.py`
5. Run `export FLASK_APP=app.py` and `export FLASK_DEBUG=1` in root directory of project from within the Pycharm terminal.

#### DB Initialization commands Setup <a name = "db_commands"></a>

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

## ✍️ Authors <a name = "authors"></a>
-   [@dhruv10](https://github.com/dhruv10)
-   [@hardik-ahuja](https://github.com/hardik-ahuja)
-   [@HemabhKamboj](https://github.com/HemabhKamboj)
