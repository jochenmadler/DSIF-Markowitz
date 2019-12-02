import pandas as pd
from sqlalchemy import create_engine, MetaData
import psycopg2

database="dsif"
user="boys"
password="zaubermaus"
host="localhost"
#port might be 5432 for, if you haven't changed anything in the settings of postgres
port="1997"
directory ='/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/DAX.txt'
#acp = adjusted closing prices
#tableName = 'acp'
tableName = 'dax'
con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

def inTable (database, user, password, host, port, directory):

    #create connection, we do this here, because we might need it later
    con = psycopg2.connect(database = database, user =user, password= password,host= host, port =port)

    #read into dataframe
    #ATTENTION file has to be txt with tabstops as seperators, not a CSV file!
    #to obtain a txt form excel just save as txt (the first option if there are more than one) <3
    df = pd.read_csv(directory, sep="\t", error_bad_lines = False, decimal = ',')

    #reading in the codenames so we can use them later again to match codes with names
    #****************************NEEDS TO BE APPENDED LATER***********************************
    codeNames = df[['Name', 'Code']]

    #for now Names are better because no error appears, no leading digits in column names possible -- I will fix soon
    df.rename(columns = {'Name': 'date'}, inplace = True)
    df = df.drop(columns='Code')

    #set the index as the company names
    df.set_index('date', inplace = True)


    # transpose the dataframe so it fits our database
    df = df.transpose()

    #cleaning the names (column names = company names) and set them to lower case
    # #-- get rid of withespaces and other stuff, so postgres accepts them as columns
    df.columns = df.columns.str.replace(' ', '').str.replace('.', '').str.replace('(', '').str.replace(')', '')
    df.columns = df.columns.str.lower()

    #*******************HERE COMES THE MAGIC*****************************
    #creates a new table out of the dataframe called 'dax' in the database dax
    # if it already exists, it only appends its values to the current database -- usefull for later
    df.to_sql(tableName, create_engine('postgresql://postgres:'+password+'@'+host+':'+port+'/'+database), if_exists ='append', index = True)

    #the previous functions is not able to realize that the index is a date, so we set it mannually here
    command = '''alter table dax 
                alter column index 
                type date using index::date;'''
    cur = con.cursor()
    cur.execute(command)
    con.commit()
    cur.close()

#input is the sting name of the table you want to have the column names, return a list with the names
def getColumns (tableName):
    cur = con.cursor()
    command = '''select column_name 
                from information_schema.columns 
                where table_name = '{}';'''.format(tableName)
    cur.execute(command)
    fetched = cur.fetchall()
    cur.close()
    return pd.DataFrame(fetched, columns=['ColumnNames']).values.tolist()

def addColumns(baseTable, newTable):
    #calculate the columns that are not in the current database by creating two sets and subtracting them
    # be aware that:
    # set([1, 2]) - set([2, 3])
    # results in:
    # set([1])
    colDif= list(set(getColumns(newTable)) - set(getColumns(baseTable)))
    cur = con.cursor()
    dataType = 'float8'
    command = '''
        alter table {}
        '''.format(baseTable)
    i = 0;
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

#expects start date, end date and a list with company name (for now, later ticker)
def getAP (startDate, endDate, comps):
    cur = con.cursor()
    #make list of comps to string
    compsStr = ', '.join(comps)
    #produces the command
    command = '''
    select  index, {}
    from dax
    where index between '{}' and '{}';
    '''.format(compsStr, startDate, endDate)
    try:
        cur.execute(command)
    except psycopg2.errors.UndefinedColumn:
        print ('psycopg2.errors.UndefinedColumn: Not a valid column name, please check!')
        return
    result = cur.fetchall()
    cur.close()
    return pd.DataFrame(result,  columns=['date'].append(comps))
#******************************************************MAIN******************************************
inTable(database,user, password, host, port, directory)
comps = ['adidas', 'allianz']
print(getAP('2019-01-01', '2019-02-28', comps))

con.commit()
con.close()