import pandas as pd
from modules.timing import write_function_results_to_file

@write_function_results_to_file
def get_product_class(conn):
    cursor = conn.cursor()
    query = """
     with sales as (SELECT 
                    p."Наименование" AS Товар,
                    SUM(s."Количество") AS "Количество продаж"
                    FROM t_sales s
                    join t_products as p on s.Номенклатура = p.Ссылка
                    GROUP BY Товар
                    order by "Количество продаж" ASC),
          sales_quantiles AS (SELECT
                                "Товар",
                                NTILE(10) OVER (ORDER BY "Количество продаж" ASC) AS quantile
                                FROM sales s
                                order by quantile desc)
     SELECT 
        "Товар" AS Номенклатура,
        CASE
            WHEN quantile = 10 THEN 'Наиболее продаваемый'
            WHEN quantile <= 9 AND quantile > 3 THEN 'Средне продаваемый'
            ELSE 'Наименее продаваемый'
        END AS КлассТовара
     FROM sales_quantiles;
        """
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall(), columns=['Номенклатура', 'КлассТовара'])
    df.to_csv('t_class_product.csv', index=True)
    cursor.close()
    return "Посчитаны классы товаров."

@write_function_results_to_file
def save_product_class(conn):
    cursor = conn.cursor()
    # Создание таблицы в БД
    cursor.execute('''
            drop table if exists t_class_product;
            create table t_class_product(
            id integer,
            Номенклатура text,
            КлассТовара text);
        ''')
    conn.commit()
    with open(f't_class_product.csv', 'r', encoding='utf-8') as f:
        next(f)
        cursor.copy_expert(f"copy t_class_product from stdin (format csv)", f)
        conn.commit()
    cursor.close()
    return "Таблица с классами товаров добавлена в БД"
