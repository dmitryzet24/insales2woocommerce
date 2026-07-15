import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class DBClient:
    def __init__(self, credentials: dict):
        print("------Client initialization for PostgresSQL (Staging)------")
        
        db_host=credentials.get('host') or 'localhost'
        db_port=credentials.get('port') or  5432
        db_name=credentials.get('database') or 'staging_warehouse' 
        db_password=credentials.get('password') or ''
        db_user = credentials.get('user') or 'db_data_engineer'
        
        print(f"-> Connecting to database '{db_name}' as user '{db_user}' on {db_host}:{db_port}")
        dsn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self.init_tables()

    def init_tables(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS insales_products_silver (
                    id SERIAL PRIMARY KEY,
                    insales_id BIGINT NOT NULL,
                    sku VARCHAR(255) NOT NULL,
                    title VARCHAR(512),
                    price NUMERIC (10, 2),
                    valid_from TIMESTAMP NOT NULL,
                    valid_to TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE
                );
                CREATE INDEX IF NOT EXISTS idx_products_sku_active 
                ON insales_products_silver (sku, is_active);
            """)

    def upsert_product_scd2(self, product: dict):
        sku = product['sku']
        insales_id = product['id']
        title = product['title']
        price = float(product.get('price', 0.0) or 0.0)
        now = datetime.now()

        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, title, price FROM insales_products_silver
                WHERE sku = %s AND is_active = TRUE LIMIT 1;
            """, (sku,))
            current_version = cursor.fetchone()

            if not current_version:
                cursor.execute("""
                    INSERT INTO insales_products_silver (insales_id, sku, title, price, valid_from, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE);
                """, (insales_id, sku, title, price, now))
            else:
                db_price = float(current_version['price'])
                db_title = current_version['title']

                if db_price != price or db_title != title:
                    print(f"-> Changes encountered for SKU {sku}: Price ({db_price} -> {price}) or Title")
                    cursor.execute("""
                        UPDATE insales_products_silver
                        SET is_active = FALSE, valid_to = %s
                        WHERE id = %s;
                    """, (now, current_version['id']))

                    cursor.execute("""
                        INSERT INTO insales_products_silver (insales_id, sku, title, price, valid_from, is_active)
                        VALUES (%s, %s, %s, %s, %s, TRUE);
                    """, (insales_id, sku, title, price, now))

    def close(self):
        if self.conn:
            self.conn.close()

    

