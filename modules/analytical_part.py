import pandas as pd
from modules.timing import write_function_results_to_file
import matplotlib.pyplot as plt


# _______________________________________Задание 1_________________________________________

# Десять первых магазинов по количеству продаж
@write_function_results_to_file
def get_top_branches(cur):
    query_top_branches = """
    SELECT 
        b."Наименование" AS Магазин,
        sum(s."Количество") AS "Количество продаж"
    FROM t_sales s
        JOIN t_branches b ON s."Филиал" = b."Ссылка"
        WHERE 
            lower(b."КраткоеНаименование") NOT LIKE '%склад%'
    GROUP BY b."Наименование"
    ORDER BY "Количество продаж" DESC
    LIMIT 10;
    """
    cur.execute(query_top_branches)
    result_top_branches = cur.fetchall()
    top_branches_df = pd.DataFrame(result_top_branches, columns=['Магазин', 'Количество продаж'])
    return top_branches_df


# Десять первых складов по количеству продаж
@write_function_results_to_file
def get_top_warehouses(cur):
    query_top_warehouses = """
    SELECT 
        b."Наименование" AS Магазин,
        sum(s."Количество") AS "Количество продаж"
    FROM t_sales s
        JOIN t_branches b ON s."Филиал" = b."Ссылка"
        JOIN t_products p ON s."Номенклатура" = p."Ссылка"
        WHERE 
            lower(b."КраткоеНаименование") LIKE '%склад%'
    GROUP BY b."Наименование"
    ORDER BY "Количество продаж" DESC
    LIMIT 10;
    """
    cur.execute(query_top_warehouses)
    result_top_warehouses = cur.fetchall()
    top_warehouses_df = pd.DataFrame(result_top_warehouses, columns=['Склад', 'Количество продаж'])
    return top_warehouses_df


# Десять самых продаваемых товаров по складам
@write_function_results_to_file
def get_top_products_warehouse(cur):
    query_top_products_warehouse = """
    SELECT 
        p."Наименование" AS Товар,
        SUM(s."Количество") AS "Количество продаж"
    FROM t_sales s
        JOIN t_products p ON s."Номенклатура" = p.Ссылка
        JOIN t_branches b ON s."Филиал" = b.Ссылка
        WHERE 
            lower(b."КраткоеНаименование") LIKE '%склад%'
    GROUP BY Товар
    ORDER BY "Количество продаж" DESC
    LIMIT 10;
    """
    cur.execute(query_top_products_warehouse)
    result_top_products_warehouse = cur.fetchall()
    top_products_warehouse_df = pd.DataFrame(result_top_products_warehouse, columns=['Товар', 'Количество продаж'])
    return top_products_warehouse_df


# Десять самых продаваемых товаров по магазинам
@write_function_results_to_file
def get_top_products_branch(cur):
    query_top_products_branch = """
    SELECT 
        p."Наименование" AS Товар,
        SUM(s."Количество") AS "Количество продаж"
    FROM t_sales s
        JOIN t_products p ON s."Номенклатура" = p.Ссылка
        JOIN t_branches b ON s."Филиал" = b.Ссылка
        WHERE 
            lower(b."КраткоеНаименование") NOT LIKE '%склад%' 
    GROUP BY Товар
    ORDER BY "Количество продаж" DESC
    LIMIT 10;
    """
    cur.execute(query_top_products_branch)
    result_top_products_branch = cur.fetchall()
    top_products_branch_df = pd.DataFrame(result_top_products_branch, columns=['Товар', 'Количество продаж'])
    return top_products_branch_df


# Десять городов, в которых больше всего продавалось товаров
@write_function_results_to_file
def get_top_cities(cur):
    query_top_cities = """
    SELECT 
        c."Наименование" AS "Город",
        SUM(s."Количество") AS "Количество Продаж"
    FROM t_sales s
        JOIN t_branches b ON s."Филиал" = b.Ссылка
        JOIN t_cities c ON b."Город" = c.Ссылка
    GROUP BY c."Наименование"
    ORDER BY SUM(s."Количество") DESC
    LIMIT 10;
    """
    cur.execute(query_top_cities)
    result_top_cities = cur.fetchall()
    top_cities_df = pd.DataFrame(result_top_cities, columns=['Город', 'Количество продаж'])
    return top_cities_df


# _______________________________________Задание 2_________________________________________

# В какие часы и в какой день недели происходит максимальное количество продаж
# (cмотря на другие задания решила вывести топ-10)

@write_function_results_to_file
def get_max_sales_time_day(cur):
    query_max_sales_time_day = """
    select EXTRACT(HOUR FROM s."Период") AS "Час",
        EXTRACT(DOW FROM s."Период") AS "День недели",
        SUM("Количество") AS "Количество продаж"
    FROM t_sales s
    GROUP BY EXTRACT(HOUR FROM s."Период"), EXTRACT(DOW FROM s."Период")
    """

    cur.execute(query_max_sales_time_day)
    result_max_sales_time_day = cur.fetchall()
    cur.close()
    max_sales_time_day_df = pd.DataFrame(result_max_sales_time_day, columns=['Час', 'День недели', 'Количество продаж'])
    day_names = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    max_sales_time_day_df['День недели'] = max_sales_time_day_df['День недели'].apply(lambda x: day_names[int(x)])

    # Визуализация результатов*
    grouped_sales = max_sales_time_day_df.groupby(['Час', 'День недели'])['Количество продаж'].sum().unstack()
    grouped_sales.plot(kind='line', marker='o')
    plt.xlabel('Час')
    plt.ylabel('День недели')
    plt.title = 'Статистика продаж в каждый час каждого дня недели'
    plt.grid(True)
    plt.savefig('graphics/sales_full_statistics.png', bbox_inches='tight')

    top_10_sales = max_sales_time_day_df.sort_values(by='Количество продаж', ascending=False).head(10)
    return top_10_sales


# _______________________________________Задание 3_________________________________________

# Количество продаж в каждом часе и по дням недели
@write_function_results_to_file
def max_sales_graphics(conn):
    query_hourly_sales = """
    SELECT 
        EXTRACT(HOUR FROM "Период") AS Час,
        SUM("Количество") AS "Количество продаж"
    FROM t_sales
    GROUP BY Час
    ORDER BY Час;
    """

    query_weekly_sales = """
    SELECT 
        EXTRACT(DOW FROM "Период") AS "День недели",
        SUM("Количество") AS "Количество продаж"
    FROM t_sales
    GROUP BY "День недели"
    ORDER BY "День недели";
    """

    hourly_sales_df = pd.read_sql(query_hourly_sales, conn)
    weekly_sales_df = pd.read_sql(query_weekly_sales, conn)
    day_names = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    weekly_sales_df['День недели'] = weekly_sales_df['День недели'].apply(lambda x: day_names[int(x)])
    first_row = weekly_sales_df.iloc[0]
    weekly_sales_df = weekly_sales_df.iloc[1:]
    weekly_sales_df = weekly_sales_df._append(first_row)

    # Строим графики
    fig, axs = plt.subplots(2)
    plt.subplots_adjust(wspace=0, hspace=0.7)
    hourly_sales_df.plot(kind='bar', x='Час', y='Количество продаж', ax=axs[0], title='Количество продаж в каждом часе')
    weekly_sales_df.plot(kind='line', x='День недели', y='Количество продаж', ax=axs[1],
                         title='Количество продаж по дням недели')
    axs[0].grid(True)
    axs[1].grid(True)
    fig.suptitle('Статистика продаж')
    plt.show()
    fig.savefig('graphics/sales_statistics.png', dpi=500)
    return "Графики сохранены в папку graphics"
