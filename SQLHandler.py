#*******************************************ANWEISUNGEN************************************************
# Alle directories (1-6) für dich in der setUP funktion anpassen für das if statement mit deinem Namen-> hast du nicht alle files? -> schreib Alex
# EINMALIG setUp("Dein Name") ausführen, mit deinem Namen als string
# dann läuft alles von alleine
# ACHTUNG!!! das setUp kann mit allen files bis zu 40 min dauern, nicht erschrecken, nicht abbrechen!
# funktionen saveUser und getUser sind noch nicht fertig implementiert, getUser returned momentan nur einen Dummy!!
# hast du daten kaputt gemacht? :/ führe einfach setUP noch einmal aus

# saveuser erwartet einen User als input (saveUser(User))
# getUser erwartet die UserID als string input (getUser(userID))
# deleteUser erwartet einen user als input (deleteUser(user))
# ****************Bitte niemals den gleichen user (gleiche UserID ist ausschlaggebend) zweimal abspeichern ohne ihn vorher wieder zu löschen
# -> "Sonst passieren schlimme Dinge" (Thomas Neumann)

import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import psycopg2
import User as us
import OptimizeProcedure as op
from django.db import transaction


name = "Alex"
database = "dsif"
user = "boys"
password = "zaubermaus"
host = "localhost"
port = "1997"
directory = '/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/DAX.txt'
directory2 = '/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/CAC40.txt'
directory3 = ""
directory4 = ""
directory5 = ""
directory6 = ""
codeRegister = 'companies'
tableName = "acp"

def start ():
    global database, host, user, password, port, directory, directory2, directory3, codeRegister

    if name == "Jochen":
        database = "postgres"
        user = "postgres"
        password = "Apfel@Data@1996"
        host = "localhost"
        port = "5432"
    elif name == "Marcel":
        database = "postgres"
        user = "postgres"
        password = "zaubermaus"
        host = "localhost"
        port = "5432"
        directory = "C:\\Users\mpere\Documents\Python Scripts\DSIF-Markowitz/DAX.txt"
    elif name == "Alex":
        database = "dsif"
        user = "boys"
        password = "zaubermaus"
        host = "localhost"
        port = "1997"


def setUp(name):

    global database, host, user, password, port, directory, directory2, directory3, codeRegister

    if name == "Jochen":
        database = "postgres"
        user = "postgres"
        password = "Apfel@Data@1996"
        host = "localhost"
        port = "5432"
        directory = "C:\\Users\joche\OneDrive\TUM - TUM-BWL\Semester 7\\04 Seminar Data Science in Finance\Capstone Projekt\Data\DAX.txt"
        directory2 = "C:\\Users\joche\OneDrive\TUM - TUM-BWL\Semester 7\\04 Seminar Data Science in Finance\Capstone Projekt\Data\CAC40.txt"
        directory3 = "C:\\Users\joche\OneDrive\TUM - TUM-BWL\Semester 7\\04 Seminar Data Science in Finance\Capstone Projekt\Data\FTSE100.txt"
        directory4 = "C:\\Users\joche\OneDrive\TUM - TUM-BWL\Semester 7\\04 Seminar Data Science in Finance\Capstone Projekt\Data\HSI.txt"
        directory5 = "C:\\Users\joche\OneDrive\TUM - TUM-BWL\Semester 7\\04 Seminar Data Science in Finance\Capstone Projekt\Data\IBEX35.txt"
        directory6 = "C:\\Users\joche\OneDrive\TUM - TUM-BWL\Semester 7\\04 Seminar Data Science in Finance\Capstone Projekt\Data\SSE.txt"
        codeRegister = "companies"
    elif name == "Marcel":
        database = "postgres"
        user = "postgres"
        password = "zaubermaus"
        host = "localhost"
        port = "5432"
        directory = "C:\\Users\mpere\Documents\Python Scripts\DSIF-Markowitz/DAX.txt"
        directory2 = "" # insert something here
        directory3 = ""
        directory4 = ""
        directory5 = ""
        directory6 = ""
        codeRegister = "companies"
    elif name == "Alex":
        database = "dsif"
        user = "boys"
        password = "zaubermaus"
        host = "localhost"
        port = "1997"
        directory = '/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/DAX.txt'
        directory2 = "/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/CAC40.txt"
        directory3 = "/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/FTSE100.txt"
        directory4 = "/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/IBEX35.txt"
        directory5 = "/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/SSE.txt"
        directory6 = "/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science in Finance/PortfolioProject/NEW/Real/HSI.txt"
        codeRegister = 'companies'

    #remove all old relations
    clean()
    inTable()
    print("First import done of")
    print(directory)
    directory = directory2
    inTable()
    print("Second import done of")
    print(directory)
    directory = directory3
    inTable()
    print("Third import done of")
    print(directory)
    directory = directory4
    inTable()
    print("Fourth import done of")
    print(directory)
    directory = directory5
    inTable()
    print("Fith import done of")
    print(directory)
    directory = directory6
    inTable()
    print("Sixth import done of")
    print(directory)

    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()

    #create the user realtion
    command = '''create table tableUsers
    (userID varchar (80) primary key,
    budget float8,
    initialBudget float8,
    varBroker integer,
    fixBroker integer,
    split bool,
    periodStart date,
    timeInterval char (1),
    optimizeObjective char (1));
    '''
    cur.execute(command)
    con.commit()

    #create the optimize request realtion
    command = '''create table request
    (userID varchar (80),
    requestID varchar (80),
    periodEnd date,
    primary key (userID, requestID),
    foreign key (userID) references tableUsers (userID) on delete cascade);
    '''
    cur.execute(command)
    con.commit()

    #create the relation of isin_list for each user
    command = '''create table isinList
        (userID varchar (80),
        isin varchar (80),
        position integer,
        primary key (userID , isin),
        foreign key (userID) references tableUsers (userID) on delete cascade);
        '''
    cur.execute(command)
    con.commit()

    #create table results
    command = '''create table result
                (requestID varchar (80) ,
                userID varchar (80) ,
                sharpeRatio integer,
                totalVolatility float8,
                totalReturn float8,
                transactionCost float8,
                currentCapital float8, 
                primary key (requestID, userID),
                foreign key (userID) references tableUsers (userID) on delete cascade);
                '''
    cur.execute(command)
    con.commit()

    command = '''create table secweights
                (requestID varchar (80),
                userID varchar (80),
                weight float8,
                isin varchar (80),
                postion integer,
                primary key (requestID, isin, userID),
                foreign key (userID) references tableUsers (userID) on delete cascade);
                '''
    cur.execute(command)
    con.commit()

    command = '''create table guiweights
                    (requestID varchar (80),
                    userID varchar (80),
                    isin varchar (80),
                    percent float8,
                    amount float8,
                    primary key (isin, requestID, userID),
                    foreign key (userID) references tableUsers (userID) on delete cascade);
                    '''
    cur.execute(command)
    con.commit()
    cur.close()

def inTable():
    # create a connection
    start()
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
    start()
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
    start()
    # columnstoReturn must be list in ,columnToSearch and  assetClass and searchterm a strings
    #searchterm = searchterm.upper()
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

def saveRequest (optimizeRequest):
    start()
    #list mit procedures
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    userID = optimizeRequest.user.id
    requestID = optimizeRequest.id
    periodEnd = optimizeRequest.period_end

    command = '''
    insert into request
    values('{}','{}','{}');'''.format(userID,requestID,periodEnd)
    cur.execute(command)
    con.commit()
    cur.close()

def saveUser(newUser):
    start()
    #delete the user first completely
    deleteUser(newUser)
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    command = '''insert into tableusers
    values ('{}',{},{},{},{},{},'{}','{}','{}');
    '''.format(newUser.id, newUser.budget, newUser.initial_budget, newUser.broker_var, newUser.broker_fix, newUser.split_shares, newUser.period_start,
               newUser.time_interval, newUser.optimize_objective)
    cur.execute(command)
    con.commit()

    #ins richtige format bringen
    #isinliste ins richtige format bringen um in relation zu speichern
    i =0
    for isin in newUser.ISIN_list:
        command = '''insert into isinList
        values ('{}','{}', {});'''.format(newUser.id, isin, i)
        i += 1
        cur.execute(command)
        con.commit()


    #relation request User speichern
    i = 0
    for tuple in newUser.req_history:
        req = newUser.req_history[i][0]
        saveRequest(newUser.req_history[i][0])
        saveResult(newUser.req_history[i][1], newUser.req_history[i][0])
        i += 1

def saveResult (result, request):
    start()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()

    #saves the result to the result-relation
    command = '''insert into result
     values ( '{}', '{}', {}, {}, {}, {}, {});
    '''.format(request.id, request.user.id, result.sharpe_ratio, result.total_volatility, result.total_return, result.transaction_cost, result.current_capital)
    cur.execute(command)
    con.commit()

    #array of the security_weights into a relation
    i=0
    for column in result.security_weights.columns:
        command = '''insert into secweights
        values ('{}', '{}', {}, '{}', {});'''.format(request.id, request.user.id, result.security_weights[column][0], column, i)
        i +=1
        cur.execute(command)
        con.commit()

    #dataframe with gui weigths
    for index, row in result.gui_weights.iterrows():
        command = '''insert into guiweights 
        values ('{}', '{}', '{}', {}, {});'''.format(request.id, request.user.id, index, row['percent_portfolio'], row['amount_eur'])
        cur.execute(command)
        con.commit()
    cur.close()

def deleteUser (olduser):
    start()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()

    command = '''delete from tableusers 
    where userID = '{}';'''.format(olduser.id)

    cur.execute(command)
    con.commit()
    cur.close()

def deleteUserRelations ():
    start()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()

    command = '''drop table if exists tableusers cascade;'''

    cur.execute(command)
    con.commit()
    cur.close()

def getUser (id):
    start()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()

    #get the user
    command = '''select * from tableusers where userid = '{}';'''.format(id)
    cur.execute(command)
    con.commit()
    result = pd.DataFrame(cur.fetchall())
    #if the user does not exist
    if result.empty:
        return None

    #get the isin list
    command = '''select * from isinlist where userid = '{}';'''.format(id)
    cur.execute(command)
    con.commit()
    isinResult = pd.DataFrame(cur.fetchall())
    isinList = []
    for index, row in isinResult.iterrows():
        isinList.append(row[1])

    # set the user
    newUser = us.User(result[0][0], budget = result[1][0], broker_var=result[3][0], broker_fix=result[4][0],
                      period_start=result[6][0].strftime ('%Y-%m-%d'),time_interval=result[7][0], optimize_objective=result[8][0], ISIN_list=isinList)
    newUser.initial_budget = result [2][0]

    #create the reqHistory
    # first get alle the requests
    command = '''select * from request where userid = '{}';'''.format(id)
    cur.execute(command)
    con.commit()
    requests = pd.DataFrame(cur.fetchall())

    reqHistory = [] # new

    i =0
    for index, row in requests.iterrows():
        req = us.optimizeRequest
        req.user = newUser
        req.id = row[1]
        req.period_end = row[2]
        #newUser.req_history[i][0] = req
        #newUser.req_history[i][1] = getResult(req)
        tup = (req, getResult(req)) # new
        reqHistory.append(tup) # new
        i += 1 # new
    newUser.req_history = reqHistory
    return newUser

def getResult (request):
    start()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()

    #get the main table of result
    command = '''select * from result where requestid = '{}';'''.format(request.id)

    cur.execute(command)
    con.commit()
    result = pd.DataFrame(cur.fetchall())
    #initialise the new result
    newResult = op.optimizeResult
    newResult.sharpe_ratio = result[2][0]
    newResult.total_volatility = result[3][0]
    newResult.total_return = result[4][0]
    newResult.transaction_cost = result[5][0]
    newResult.current_capital = result[6][0]

    #get the guiWeights
    command = '''select * from guiweights where requestid = '{}';'''.format(request.id)
    cur.execute(command)
    con.commit()
    result = pd.DataFrame(cur.fetchall())
    result = result.drop(columns=[0,1])
    result.rename(columns ={result.columns[0]: 'isin', result.columns[1]: 'percent_portfolio', result.columns[2]: 'amount_eur'}, inplace=True)
    result.set_index('isin', inplace=True)
    newResult.gui_weights = result

    #get the secweigths
    command= '''select isin, weight from secweights where requestid = '{}';'''.format(request.id)
    cur.execute(command)
    con.commit()
    res = pd.DataFrame(cur.fetchall())
    res = res.transpose()
    res.rename(columns = res.iloc[0])
    header = res.iloc[0,:]
    weights = pd.DataFrame(res.iloc[1,:], index= ["isin", "weights"], columns= header)
    newResult.security_weights = weights

    return newResult

def clean():
    start()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    command = '''
    drop table if exists acp;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    con.commit()
    command = '''drop table if exists companies;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    con.commit()
    command = '''drop table if exists tableusers cascade;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    con.commit()
    command = '''drop table if exists request cascade;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    con.commit()
    command = '''drop table if exists isinList;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    con.commit()
    command = '''drop table if exists result;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    con.commit()
    command = '''drop table if exists secweights;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    command = '''drop table if exists guiweights;'''
    try:
        cur.execute(command)
    except psycopg2.errors.InFailedSqlTransaction:
        print(" transaction failed, rollback")
        transaction.rollback()
    con.commit()
    cur.close()
    deleteUserRelations()

def exists(id):
    start()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    command = '''select * from tableusers where userid = '{}';'''.format(id)
    cur.execute(command)
    con.commit()
    result = pd.DataFrame(cur.fetchall())
    # if the user does not exist
    if result.empty:
        return False
    return True