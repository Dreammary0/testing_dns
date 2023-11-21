from modules.create_db import *
from modules.analytical_part import *
from modules.calculation_part import *

if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()

    # Создание БД
    create_db_(conn)
    create_tables_values(conn)
    product_data_cleaning(conn)

    # Аналитическая часть
    get_top_branches(cursor)
    get_top_warehouses(cursor)
    get_top_products_warehouse(cursor)
    get_top_products_branch(cursor)
    get_top_cities(cursor)
    get_max_sales_time_day(cursor)
    max_sales_graphics(conn)

    # Расчетная часть
    get_product_class(conn)
    save_product_class(conn)

    conn.close()