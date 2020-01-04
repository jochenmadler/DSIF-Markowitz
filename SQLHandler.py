#find classes here: https://docs.python.org/2/tutorial/classes.html

import pandas as pd
from sqlalchemy import create_engine, MetaData
import sqlalchemy
import psycopg2

# ist bei euch "postgres"
database = 'postgres'
user = 'postgres'
#database="dsif"
# ist bei euch postgres
#user="boys"
# kann auch euer eigenes Passwort
password="zaubermaus"
#port is immer localhost
host="localhost"
#port might be 5432 for, if you haven't changed anything in the settings of postgres
port = '5432'
#port="1997"
directory ='C:\\Users\mpere\Documents\Python Scripts\DSIF-Markowitz/DAX.txt'
codeRegister = 'companies'

tableName = "acp" # A djusted C losing P rice
#opens connecton
con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

def inTable (database, user, password, host, port, directory, existingTableName):
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    #create connection, we do this here, because we might need it later connection is already created and stable the whole time

    #read into dataframe
    #ATTENTION file has to be txt with tabstops as seperators, not a CSV file!
    #to obtain a txt form excel just save as txt (the first option if there are more than one) <3
    #Date row MUST be in the format YYYY-MM-DD please set it accordingly in excel already
    df = pd.read_csv(directory, sep="\t", error_bad_lines = False, decimal = ',')
    df.columns = df.columns.str.lower()
    df['isin'] = df['isin'].str.lower()
    #reading in the codenames so we can use them later again to match codes with names
    #****************************Handels the Companies Names ISIN  DSCD and Index***********************************
    codeNames = df [['name', 'isin', 'dscd', 'index']]
    try:
        codeNames.to_sql(codeRegister, create_engine('postgresql://'+user+':'+password+'@'+host+':'+port+'/'+database), if_exists='append', index=False)
    except sqlalchemy.exc.DataError:
        print("******************** \n"
              " Your input file is apparently in the wrong format, please check if the file is in txt with tapstop and not as CSV \n"
              "********************")


    #****************************Handels the actual data, the ACP or the whatever price index****************************
    df = df.drop(columns= ['name', 'dscd', 'index'])
    #set the index as the company names
    df.set_index('isin', inplace=True)


    # transpose the dataframe so it fits our database
    df = df.transpose()
    con.commit()
    #checks if the columns of the df already exists in the current table in SQL
    #existingColumns = getColumnsSQL(existingTableName)
    #if some don't exists - add them
    #    print("in the nothonign")
    #if existingColumns is not None:
    #    if len(set(df.columns)-set(existingColumns))!=0:
    #        print(set(df.columns))
    #        print(set(existingColumns))
    #        #addColumns(existingTableName, list(existingColumns = getColumnsSQL(existingTableName)))
            #print("Type of df.columns ")
            #print (type(df.columns))

    #        addColumns(existingTableName, df.columns)
    #*******************HERE COMES THE MAGIC*****************************
    #creates a new table out of the dataframe called 'dax' in the database dax
     #if it already exists, it only appends its values to the current database -- usefull for later
    #print("doing the df to sql")
    try:
        df.to_sql(existingTableName, create_engine('postgresql://'+user+':'+password+'@'+host+':'+port+'/'+database), if_exists='append', index=True)
    except sqlalchemy.exc.DataError:
        print("******************** \n"
              " Your input file is apparently in the wrong format, please check if the date is in the format YYYY-MM-DD and the file is in txt with tapstop and not as CSV \n"
              "********************")
    #the previous functions is not able to realize that the index is a date, so we set it mannually here
    command = '''alter table {} 
                alter column index 
                type date using index::date;'''.format(existingTableName)
    cur = con.cursor()
    cur.execute(command)
    con.commit()
    cur.close()

#input is the sting name of the table you want to have the column names, return a list with the names
def getColumnsSQL (tableName):
    cur = con.cursor()
    command = '''select column_name 
                from information_schema.columns 
                where table_name = '{}';'''.format(tableName)
    cur.execute(command)
    fetched = cur.fetchall()
    cur.close()
    #index out of range, hier muss noch nachgeholfen werden
    if not fetched:
        return
    else:
        return pd.DataFrame(fetched, columns=['ColumnNames']).values.tolist()[0]
def addColumns(baseTable, newColumns):
    #new columns must be a list, basetable must be the name of the table where the columns should be added to
    #calculate the columns that are not in the current database by creating two sets and subtracting them
    # be aware that:
    # set([1, 2]) - set([2, 3])
    # results in:
    # set([1])
    colDif= list(set(newColumns) - set(getColumnsSQL(baseTable)))
    #print(colDif)
    cur = con.cursor()
    dataType = 'float8'
    command = '''
        alter table {}
        '''.format(baseTable)
    i = 1;
    for col in colDif:
        if i == len(colDif):
            command = '''{}
            add column {} {};
            '''.format(command, col, dataType)
            break
        command = ''' {}
        add column {} {},
        '''.format(command, col, dataType )
        i += 1
    #******************the end of command statement is not implemented yet

    cur.execute(command)
    cur.close()
    con.commit()


#expects start date, end date and a list with company name (for now, later ticker)
def getACP (startDate, endDate, comps):
    #start date, end date, isins/code
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    #make list of comps (ISINs) to string

    compsStr = ', '.join([comp.lower() for comp in comps])
    #compsStr = ', '.join(comps)
    #print(compsStr)
    #produces the command
    command = '''
        select index, {}
        from acp
        where index between '{}' and '{}';
        '''.format(compsStr, startDate, endDate)
    #catching error if the company does not exists or is written wrongly
    try:
        cur.execute(command)
    except (psycopg2.errors.UndefinedColumn,sqlalchemy.exc.DataError):
        print ('Not a valid column name, please check!or not a valid please check if the date is in the format YYYY-MM-DD')
        return
    result = cur.fetchall()
    cur.close()

    names = ['date']
    for com in comps:
        names.append(com)
    result = pd.DataFrame(result, columns = names)
    result.set_index('date', inplace=True)
    return result

def findComp(searchterm, columnToSearch, columnsToReturn ,assetClass):
    #columnstoReturn must be list in ,columnToSearch and  assetClass and searchterm a strings
    searchterm = searchterm.upper()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    selected = ', '.join([col.lower() for col in columnsToReturn])
    command = '''
        select {}
        from {}
        where {} like '%{}%';
        '''.format(selected, assetClass, columnToSearch, searchterm)
    #exception catch is not really necessary here, but is ok anyway
    #print(command)
    try:
        cur.execute(command)
    except psycopg2.errors.UndefinedColumn:
        print ('psycopg2.errors.UndefinedColumn: Not a valid column name, please check!')
        return
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

#******************************************************MAIN******************************************
#directory2 ='/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/AEX.txt'
inTable(database,user, password, host, port, directory, tableName)
#comps = ['DE000a1EWWW0', 'de0008404005', 'ie00bz12wp82', 'de0007100000']
#print(getACP('2019-01-01', '2019-02-28', comps))
#print(findComp("deutsch", "name", ["name", "index", "isin"], "companies"))
#getColumnsSQL(tableName)
con.commit()
con.close()

# Nr. 1