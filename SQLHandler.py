#find classes here: https://docs.python.org/2/tutorial/classes.html

import pandas as pd
from sqlalchemy import create_engine, MetaData
import sqlalchemy
import psycopg2

database = "dsif"
user = "boys"
password = "zaubermaus"
host = "localhost"
port = "1997"
directory = '/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/DAX.txt'
codeRegister = 'companies'
tableName = "acp"


def setUp(name):
    global database, host, user, password, port, directory, codeRegister
    #remove all old relations first to avoid duplicates
    clean()

    if name == "Jochen":
        database = "postgres"
        user = "postgres"
        password = "Apfel@Data@1996"
        host = "localhost"
        port = "5432"
        directory = "C:\\Users\joche\OneDrive\TUM - TUM-BWL\Semester 7\\04 Seminar Data Science in Finance\Capstone Projekt\Data\DAX.txt"
        codeRegister = "companies"
    elif name == "Marcel":
        database = "postgres"
        user = "postgres"
        password = "zaubermaus"
        host = "localhost"
        port = "5432"
        directory = "C:\\Users\mpere\Documents\Python Scripts\DSIF-Markowitz/DAX.txt"
        codeRegister = "companies"
    elif name == "Alex":
        database = "dsif"
        user = "boys"
        password = "zaubermaus"
        host = "localhost"
        port = "1997"
        directory = '/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/DAX.txt'
        codeRegister = 'companies'
    inTable()
    directory = "/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/CAC40.txt"
    inTable()


def inTable():
    # create a connection
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    # read in the future codeNames relation
    df = pd.read_csv(directory, sep="\t", error_bad_lines=False, decimal=',')
    df.columns = df.columns.str.lower()
    #df['isin'] = df['isin'].str.lower()

    # ****************************Puts the Companies Names ISIN  DSCD and Index in a relation***********************************
    codeNames = df[['name', 'isin', 'dscd', 'index']]
    try:
        codeNames.to_sql(codeRegister, create_engine(
            'postgresql://' + user + ':' + password + '@' + host + ':' + port + '/' + database), if_exists='append',
                         index=False)
    except sqlalchemy.exc.DataError:
        print("******************** \n"
              " Your input file is apparently in the wrong format, please check if the file is in txt with tapstop and not as CSV \n"
              "********************")

    # now drop those data, only the isin is now relevant
    df = df.drop(columns=['name', 'dscd', 'index'])

    # df wide to long format to put the data to sql
    df = df.melt(id_vars="isin", var_name="date", value_name="acp")
    try:
        df.to_sql(tableName,
                  create_engine('postgresql://' + user + ':' + password + '@' + host + ':' + port + '/' + database),
                  if_exists='append', index=False)
    except sqlalchemy.exc.DataError:
        print("******************** \n"
              " Your input file is apparently in the wrong format, please check if the date is in the format YYYY-MM-DD and the file is in txt with tapstop and not as CSV \n"
              "********************")
    command = '''alter table {} 
                    alter column date 
                    type date using date::date;'''.format(tableName)
    cur = con.cursor()
    cur.execute(command)
    con.commit()
    cur.close()
    return

def getACP (startDate, endDate, comps):
    #create connection
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    #make comps to lower case
    compsStr = "','".join([comp.upper() for comp in comps])

    command = '''
            select *
            from acp
            where isin in ('{}') and date between '{}' and '{}';
            '''.format(compsStr, startDate, endDate)
    # catching error if the company does not exists or is written wrongly
    try:
        cur.execute(command)
    except (psycopg2.errors.UndefinedColumn, sqlalchemy.exc.DataError):
        print(
            'Not a valid column name, please check!or not a valid date please check if the date is in the format YYYY-MM-DD')
        return
    #catch the result from terminal
    result = cur.fetchall()
    cur.close()
    result = pd.DataFrame(result)
    #set the column names
    result.columns = ['isin','date','acp']
    #long to wide
    result = result.pivot(index= 'date', columns= 'isin', values='acp')
    return result

def findComp(searchterm, columnToSearch, columnsToReturn ,assetClass):
    # columnstoReturn must be list in ,columnToSearch and  assetClass and searchterm a strings
    searchterm = searchterm.upper()
    #create connection
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()

    #put the columns-to-return in the right format
    selected = ', '.join([col.lower() for col in columnsToReturn])

    command = '''
            select {}
            from {}
            where {} like '%{}%';
            '''.format(selected, assetClass, columnToSearch, searchterm)
    try:
        cur.execute(command)
    except psycopg2.errors.UndefinedColumn:
        print('psycopg2.errors.UndefinedColumn: Not a valid column name, please check!')
        return

    #catch the result
    result = pd.DataFrame(cur.fetchall())
    cur.close()
    return result

def saveUser (optimizeResult, optimizeRequest):
    #list mit procedures
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    optimizeResult.security_weights.to_sql('weights', create_engine('postgresql://'+user+':'+password+'@'+host+":"+port+"/"+database), if_exists='append', index = True)


def getResult (name):
    #return an optimizeResult - object
    return


def clean():
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    command = '''
    drop table acp;
    '''
    cur.execute(command)
    con.commit()
    command = '''
        drop table companies;
        '''
    cur.execute(command)
    con.commit()
    cur.close()

# main
#clean()
#setUp("Alex")
comps = ['DE000a1EWWW0', 'de0008404005', 'ie00bz12wp82', 'de0007100000']
print(getACP('2019-01-01', '2019-02-28', comps))
exit(0)