import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vault_client import VaultClient
from scripts.db_client import DBClient
from scripts.woo_client import WooCommerceClient

def run_gold_sync():
	print("------Running Gold Syncronization (PostrgeSQL -> WooCommerce)")

	vault = VaultClient()
    db_secrets = vault.get_secret(path="staging_db")
    woo_secrets = vault.get_secret(path="woocommerce_api")

    if not woo_secrets:
        print("[ERROR] getting secrets dailed using path 'secret/woocommerce_api'!")
        return
    

    db = DBClient(credentials=db_secrets)
    woo = WooCommerceClient(credentials=woo_secrets)

    print("[READING] actual(relevant) data from Silver Layer")
    with db.conn.cursor(cursor_factory=None) as cursor:
        cursor.execute("""
            SELECT insales_id, sku, title, price
            FROM insales_products_silver
            WHERE is_active = TRUE;
        """)
        colums = [desc[0] for desc in cursor.description]
        active_products = [dict(zip(colums, row)) for row in cursor.fetchall()]

        print(f"[SEARCH] -> Found {len(active_products)} active products for SYNC")

        print("------Processing products to Gold Layer (WooCommerce)------")
        for prod in active_products:
            sku = prod['sku']
            
            woo_product = woo.get_product_by_sku(sku)
            if not woo_product:
                woo.create_product(prod)
            else:
                woo_id = woo_product["id"]
                woo_price = float(woo_product.get('regular_price', 0.0) or 0.0)
                woo_title = woo_product.get('name', '')
                if woo_price != float(prod['price']) or woo_title != prod['title']:
                    print(f"[UPDATE] is nessary, there different in SKU info")
                    woo.update_product(woo_id, prod)
                else:
                    print(f"[SKIPPING] SKU info is equal")

        db.close()
        print(f"[FINISH] All products are up to date")

if __name__ == "__main__":
    run_gold_sync()
    
