import sqlite3
import os
import glob
import pandas as pd
import requests  # shodan


###################################################################################################
# This is for simplifying alias management.
# By sname we mean a server name, where a server may be any of mail domain, mail server, web server, name server, script server.
#
# We want a simple way for finding all aliases of a given sname, even when aliases are CHAINED.
# For example, the ALIAS table might contain
#  sname, alias
#  alias, alias1
#  alias1, alias2
# In SQL, extracting from this table all the rows related to 'sname' is difficult.
# We want to create an additional table ALIAS_EXPANDED that in this case will contain:
#  sname, domain, alias
#  sname, alias, alias1
#  sname, alias1, alias2
# Extracting from this table all the rows related to 'sname' is trivial.
#
# works - ab March 15-th
###################################################################################################


# for each sname that has an alias (i.e., a row <sname, alias> in ALIAS)
# construct a row <sname, sname, alias>
# (i.e., the starting point for navigating between aliases)
def select_starting_aliases(alias, other_tables):
    column_names = ['domain', 'name_id', 'alias_id']
    df = pd.DataFrame(columns=column_names)
    for t in other_tables:
        d_expanded = pd.merge(t, alias, left_on='name_id', right_on='name_id')
        print(d_expanded)
        d_expanded = d_expanded[~d_expanded['alias_id'].isnull()]
        if not d_expanded.empty:
            d_expanded['domain'] = d_expanded['name_id']
            d_expanded = d_expanded[['domain', 'name_id', 'alias_id']]
            if df.empty:
                df = d_expanded.copy(deep=True)
            else:
                df = pd.concat([df, d_expanded.copy(deep=True)], ignore_index=True, axis=0)
    return df


# see beginning of this file
def construct_alias_chained(db_name):
    # read all the relevant tables
    connection = sqlite3.connect(db_name)



    alias = pd.read_sql_query("SELECT * from ALIAS", connection)
    mail_domains = pd.read_sql_query('SELECT * from MAIL_DOMAIN', connection)
    mail_servers = pd.read_sql_query('SELECT * from MAIL_SERVER', connection)
    web_servers = pd.read_sql_query('SELECT * from WEB_SERVER', connection)
    name_servers = pd.read_sql_query('SELECT * from NAME_SERVER', connection)
    script_servers = pd.read_sql_query('SELECT * from SCRIPT_SERVER', connection)
    connection.close()

    alias_chained = select_starting_aliases(alias, [mail_domains, mail_servers, web_servers, name_servers, script_servers])

    # If ALIAS table contains <sname, alias_x> and <aliasx, aliasy>,
    #  then ALIASEXPANDED contains <sname, sname, alias_x> (inserted by the previous function)
    #  and we now need to add <sname, alias_x, alias_y>
    rows = pd.DataFrame()
    for row in alias_chained.iterrows():
        d = row[1]['domain']
        n = row[1]['name_id']
        a = row[1]['alias_id']
        looping = True
        while looping:
            nf = alias.loc[alias['name_id'] == a]
            if not nf.empty:
                n = nf['name_id'].values[0]
                a = nf['alias_id'].values[0]
                df_tmp = pd.DataFrame({'domain': [d], 'name_id': [n], 'alias_id': [a]})
                rows = pd.concat([rows, df_tmp], ignore_index=True, axis=0)
                n = a
            else:
                looping = False
    alias_chained = pd.concat([alias_chained, rows], ignore_index=True, axis=0)


    # at this point ALIASEXPANDED contains all rows of ALIAS related to sname
    # now we need to insert in ALIASEXPANDED all rows of ALIAS that are not related to any sname
    # this is tricky because these tables have different schema
    alias_tmp = alias[['name_id', 'alias_id']]
    alias_expanded_tmp = alias_chained[['name_id', 'alias_id']]
    df_all = alias_tmp.merge(alias_expanded_tmp.drop_duplicates(), on=['name_id', 'name_id'],
                             how='left', indicator=True)
    df_all = df_all[df_all['_merge'] == 'left_only']
    df_all = df_all[['name_id', 'alias_id_x']]
    df_all = df_all.rename(columns={'alias_id_x': 'alias_id'})

    # print(df_all)
    # df_all contains all the rows to be added to alias_chained
    # we need to add a domain column; the value of this column will reflect that there is not a chaining
    df_all['domain'] = df_all['name_id']

    if alias_chained.empty:
        return df_all
    else:
        return pd.concat([alias_chained, df_all], ignore_index=True, axis=0)


def insert_table_in_db(df, db_name, table_name):
    connection = sqlite3.connect(db_name)
    df.to_sql(table_name, connection, if_exists="replace")
    connection.close()
    # print(db_name)

def play_with_sql(db_name):
    connection = sqlite3.connect(db_name)
    check_existence = connection.execute('SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name=\'directzone\';').fetchone()
    if(check_existence[0] == 1):
        print('exists')
    else:
        print('does not exist')
    print(check_existence[0])
    connection.close()


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    df = construct_alias_chained('results.sqlite')
    insert_table_in_db(df, 'results.sqlite', 'ALIAS_CHAINED')
    exit(0)

    base_dir = os.getcwd()
    # where query files (sql) are stored
    sql_script_dir = base_dir + ''
    # where db files (sqllite) are stored
    db_dir = base_dir + ''
    # where output files are stored
    query_output_dir = base_dir + ''

    db_list = []
    for file in glob.glob("*.sqlite"):
        db_list.append(file)

    for db_name in db_list:
        df = construct_alias_chained(db_name)
        insert_table_in_db(df, db_name, 'ALIAS_CHAINED')
