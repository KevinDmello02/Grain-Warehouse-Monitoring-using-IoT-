from flask import Flask, render_template, redirect,url_for, request, jsonify
import random, datetime,sqlite3,json,csv,pathlib
import pandas as pd
from pandas import ExcelWriter
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
from openpyxl import load_workbook



app = Flask(__name__, static_url_path='/static')
Bootstrap(app)

conn = sqlite3.connect('Testdb.db', check_same_thread=False)
c = conn.cursor()



def create_sqltemp(t, h, d):
    conn = sqlite3.connect('Testdb.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS TempData (Datestamp TEXT, Temperature INTEGER, Humidity INTEGER)')
    c.execute("INSERT INTO TempData (Temperature, Humidity, Datestamp) VALUES  (?, ?, ?)", (t, h, d))
    conn.commit()
    c.close()
    conn.close()
    return



def data_sensor():
    date= datetime.datetime.now()
    datestamp = date.strftime('%Y-%m-%d %m %H:%M:%S')
    Temp = random.randint(15, 30)
    Hum = random.randint(40, 70)
    return Temp, Hum, datestamp


def time_job():
    Temp, Hum, datestamp = data_sensor()
    create_sqltemp(Temp, Hum, datestamp)


#c.execute("INSERT INTO TempData ")

sched = BackgroundScheduler()
sched.add_job(time_job,'interval',minutes=2)
sched.start()


@app.route('/')
def home():
    Temp, Hum, datestamp=data_sensor()
    return render_template('home.html',Temp=Temp,Hum=Hum)

@app.route('/stock')
def warehouse():

    Temp, Hum, datetime = data_sensor()


    return render_template('stock.html', Temp=Temp, Hum=Hum)

@app.route('/viewstock')
def viewstock():

    c = conn.cursor()
    c.execute("SELECT * FROM Stock")
    data = c.fetchall()

    return render_template('viewstock.html', data=data)


@app.route('/delete/<id>')
def delete(id):
    conn = sqlite3.connect('Testdb.db', check_same_thread=False)
    c = conn.cursor()
    
    date= datetime.datetime.now()
    deletedate = date.strftime('%c')

    c.execute("SELECT * FROM Stock WHERE Id=?",(id,))
    deletedStock = str(c.fetchone()).strip("'' ()")

    labels = ["Id","Block","Added Time","Grain","Type","Weight","Deleted Time"]

    li = list(deletedStock.split(','))
    li.append(deletedate)
    file = pathlib.Path("test.csv")
    if file.exists ():
        with open('test.csv', 'a', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_ALL)
            filewriter.writerow(li)
    else:
        with open('test.csv', 'a', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_ALL)
            filewriter.writerow(labels)
            filewriter.writerow(li)




    #with open("copy.txt", "a") as file:
        #file.write(deletedStock)


    #book = load_workbook('test.xlsx')
    #writer = pd.ExcelWriter('test.xlsx', engine='openpyxl') 
    #writer.book = book
    #writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    #df.to_excel(writer, "Main" ,columns=["Id","Block","Added Time","Grain","Type","Weight"])

    #writer.save()

    c.execute("DELETE FROM Stock Where Id=?",(id,))
    conn.commit()
    c.close()
    conn.close()
    return redirect(url_for('viewstock'))



@app.route('/process', methods=['POST'])
def process():
    block = request.form['block']
    grain = request.form['grain']
    type = request.form['type']
    weight = request.form['weight']
    dates= datetime.datetime.now()
    datestock = dates.strftime('%c')
    if block and grain and type and weight:
        conn = sqlite3.connect('Testdb.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS Stock (ID INTEGER PRIMARY KEY AUTOINCREMENT, Block TEXT, Date TEXT ,Grain TEXT, Type TEXT, Weight INTEGER)')
        c.execute("INSERT INTO Stock (Block, Date, Grain, Type, Weight) VALUES  (?,?, ?, ?, ?)", (block,datestock,grain, type, weight))
        conn.commit()
        c.close()
        conn.close()
        return render_template('stock.html')
    return jsonify({'error': 'Missing Data!'})


@app.route('/editprocess/<id>')
def editprocess(id):
    conn = sqlite3.connect('Testdb.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT Block FROM Stock WHERE id=?",(id,))
    b=str(c.fetchone()).strip("(),''")
    c.execute("SELECT Grain FROM Stock WHERE id=?",(id,))
    g=str(c.fetchone()).strip("(),''")
    c.execute("SELECT Type FROM Stock WHERE id=?",(id,))
    t=str(c.fetchone()).strip("(),''")
    c.execute("SELECT Weight FROM Stock WHERE id=?",(id,))
    w=str(c.fetchone()).strip("(),''")
    conn.commit()
    c.close()
    conn.close()
    return render_template('edit.html',b=b,g=g,t=t,w=w,id=id)


@app.route('/edit',methods=['POST'])
def edit():

    id=request.form['id']
    block = request.form['block']
    grain = request.form['grain']
    type = request.form['type']
    weight = request.form['weight']
    dates= datetime.datetime.now()
    datestock = dates.strftime('%c')
    if block and grain and type and weight:
        conn = sqlite3.connect('Testdb.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("UPDATE Stock SET Block = ?, Date = ?, Grain = ?, Type = ?, Weight = ? WHERE Id=?",(block,datestock,grain, type, weight,id))
        conn.commit()
        c.close()
        conn.close()
        return render_template('edit.html')
    return jsonify({'error': 'Missing Data!'})


@app.route('/history')
def history():
    conn = sqlite3.connect('Testdb.db', check_same_thread=False)
    c = conn.cursor()
    m='04'
    i=12
    list=[""]
    while i!=0 :

        c.execute("SELECT AVG(Temperature) from TempData WHERE STRFTIME('%m')='"+str(i)+"'")
        list.append(c.fetchone())
        i-=1

    df1 = pd.DataFrame(list)
    df=pd.read_sql_query("SELECT Temperature from TempData WHERE STRFTIME('%m')='"+m+"'", conn)
    pf=pd.read_sql_query("SELECT Humidity from TempData WHERE STRFTIME('%m')='"+m+"'",conn)

    conn.close()

    data11=df['Temperature'].values.tolist()
    data22=pf['Humidity'].values.tolist()

    months =['January','February','March','April','May','June','July','August','September','October','November','December']

    return render_template('history.html',months=json.dumps(months),data1=data11,data2=data22)


@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/contact')
def contact():
    return render_template('contactus.html')

if __name__ == '__main__':
    app.run(debug=True)

STATIC_URL = '/static/'