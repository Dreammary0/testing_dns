from config import host, user, password, db_name
import psycopg2
from modules.timing import write_function_results_to_file

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
        )
    except Exception as _ex:
        print("*[INFO] Error while working with PostgreSQL", _ex)
    else: return conn


# Я анализировала по поводу индексов в explain analyze как могла, но ускорение все равно мизерное :(
@write_function_results_to_file
def create_db_(conn):
    cursor = conn.cursor()
    cursor.execute('''
    drop table if exists t_branches CASCADE;
    drop table if exists t_cities CASCADE;
    drop table if exists t_products CASCADE;
    drop table if exists t_sales CASCADE;
    
    create table t_cities(
    id integer ,
    Ссылка text primary key,
    Наименование varchar(128));
    
    create table t_products(
    id integer,
    Ссылка text primary key,
    Наименование text);
    
    create table t_branches(
    id integer,
    Ссылка text  primary key,
    Наименование text,
    Город text references t_cities(Ссылка),
    КраткоеНаименование text,
    Регион text);
    
    create table t_sales(
    id integer primary key,
    Период timestamp,
    Филиал text references t_branches(Ссылка),
    Номенклатура text references t_products(Ссылка),
    Количество float,
    Продажа float);
        
    create index idx_sales_period_amount on t_sales("Количество", "Период");
    create index idx_sales_filial on t_sales("Филиал");
    create index idx_sales_tovar on t_sales("Номенклатура");
    create index idx_sales_prodaga on t_sales("Продажа");
    create index trmg_idx_branches_name on t_branches using gin (КраткоеНаименование gin_trgm_ops);
       
    ''')
    conn.commit()
    return "БД создана."

@write_function_results_to_file
def create_tables_values(conn):
    tables = ['t_cities', 't_products', 't_branches', 't_sales']
    cursor = conn.cursor()
    cursor.execute('''
    ALTER TABLE t_sales DISABLE TRIGGER ALL;
    ALTER TABLE t_branches DISABLE TRIGGER ALL;
    ''')
    conn.commit()
    for table in tables:
        with open(f'test_data/{table}.csv', 'r', encoding='utf-8') as f:
            next(f)
            cursor.copy_expert(f"copy {table} from stdin (format csv)", f)
            conn.commit()
    return "БД заполнена."


# Решила не учитывать доставку грузов в статистике продаж, это все таки не товар...
@write_function_results_to_file
def product_data_cleaning(conn):
    cursor = conn.cursor()
    cursor.execute('''
        delete from t_sales s using t_products p 
        where 
            s."Номенклатура" = p."Ссылка" 
            and (lower(p."Наименование") like '%грузов%'
            or lower(p."Наименование") like '%доставка%');
        delete from t_products 
        where 
            lower("Наименование") like '%грузов%'
            or lower("Наименование") like '%доставка%';
            ALTER TABLE t_sales ENABLE TRIGGER ALL;
            ALTER TABLE t_branches ENABLE TRIGGER ALL;
        ''')
    conn.commit()
    cursor.close()
    return "Из данных удалены грузы и доставки."


