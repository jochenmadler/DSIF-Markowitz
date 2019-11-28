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
tableName = 'acp'
con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

def inTable (database, user, password, host, port, directory):

    #create connection, we do this here, because we might need it later
    con = psycopg2.connect(database, user, password, host, port)

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
    df.to_sql(tableName, create_engine('postgresql://postgres:'+password+'@'+host+':'+port+'//'+database), if_exists ='append', index = True)

    #the previous functions is not able to realize that the index is a date, so we set it mannually here
    command = '''alter table dax 
                alter column index 
                type date using index::date;'''
    cur = con.cursor()
    cur.execute(command)
    con.commit()






    cur.close()

#input is the sting name of the table you want to have the column names, return a dataframe with the name
def getColumns (tableName):
    cur = con.cursor()
    command = '''select column_name 
                from information_schema.columns 
                where table_name = ''' + tableName+''';'''
    cur.execute(command)
    fetched = cur.fetchall()
    cur.close()
    return pd.DataFrame(fetched, columns=['ColumnNames'])

#def addColumns()


#******************************************************MAIN******************************************
#inTable(database,user, password, host, port, directory)
con.commit()
con.close()