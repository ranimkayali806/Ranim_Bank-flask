from flask import Flask, render_template, request,redirect
from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from model import db, seedData, Customer, Account,Transaction
from flask_wtf import FlaskForm
from forms import WithdrawForm, DepositeForm,TransactionsForm
import os
from flask_security import roles_accepted, auth_required, logout_user
from flask_security.models import fsqla_v3 as fsqla
from flask_security import Security, SQLAlchemyUserDatastore

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:R0944351861m.@localhost/Bank1'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://rootpy23:Ranim92#@py23.mysql.database.azure.com/inlämning'
#(kan inte deploya tyvär)

#app.config['SECRET_KEY'] = os.urandom(32)  för secerhet
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
db.app = app
db.init_app(app)
migrate = Migrate(app,db)

fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    pass

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)
 
 

@app.route("/")
def startpage():
   
     return render_template("index.html", activePage="startPage" )

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
    
@app.route("/withdraw/<int:id>", methods=['GET', 'POST'])
@auth_required()  #komentera den här rad när du kör unittester
@roles_accepted("Admin")  # komentera den här rad när du kör unittester
def withdraw(id):
    customer = Customer.query.filter_by(Id=id).first()
    transaction = Transaction.query.filter_by(Id=id).first
    account = Account.query.filter_by(Id=id).first()
    form = WithdrawForm()
    trans = Transaction()
    message = ["Beloppet är stort"]
    message_2 = ["Must be positive"]
    #form.amount.errors = form.amount.errors + ('beloppet är stort',)fungerar inte
    if form.validate_on_submit():
        if account.Balance < form.amount.data:
             form.amount.errors = form.amount.errors + message
        elif form.amount.data < 0:
             form.amount.errors = form.amount.errors + message_2
        else:
            account.Balance= account.Balance - form.amount.data
            #insert in trans
            trans.Type="Credit"
            trans.Operation = "Payment"
            trans.Date = datetime.now()
            trans.NewBalance = account.Balance
            trans.Amount = form.amount.data
            trans.AccountId = account.Id
            db.session.add(trans)
            db.session.commit()
      
            return redirect("/account/" + str(id))
    return render_template("withdraw.html", formen=form, transaction=transaction,account=account,customer=customer)

@app.route("/deposite/<int:id>", methods=['GET', 'POST'])
@auth_required()           #komentera den här rad när du kör unittester
@roles_accepted("Admin")   #komentera den här rad när du kör unittester
def deposite(id):
    transaction = Transaction.query.filter_by(Id=id).first
    account = Account.query.filter_by(Id=id).first()
    form = DepositeForm()
    trans = Transaction()
    message= ["Must be positive"]
   
    if form.validate_on_submit():
        if form.amount.data<0:
             form.amount.errors = form.amount.errors + message
        else:
             
            account.Balance = account.Balance + form.amount.data #to do ändra i database
            trans.Type="Debit"
            trans.Operation = "Salary"
            trans.Date = datetime.now()
            trans.NewBalance = account.Balance
            trans.Amount = form.amount.data
            trans.AccountId = account.Id
            db.session.add(trans)
            db.session.commit()

            return redirect("/account/" + str(id))
       
    return render_template("deposite.html", formen=form, transaction=transaction)

    


@app.route("/customerimage/<id>")
def customerimagepage(id):
     customer = Customer.query.filter_by(Id = id).first()
     return render_template("customerimage.html", customer=customer )



@app.route("/customers")
@auth_required()
@roles_accepted("Admin","Staff")
def customers():  #/customers?sortColumn=surname&sortOrder=asc"page=11
    sortColumn = request.args.get('sortColumn', 'givenname')
    sortColumn = request.args.get('sortColumn', 'surname')
    sortOrder = request.args.get('sortOrder','asc')
    q = request.args.get('q','')
    page = int(request.args.get('page' , 1))
    

    customers = Customer.query  
    customers = customers.filter(
        Customer.GivenName.like('%' + q + '%')|
        Customer.City.like('%' + q + '%'))
    
    if sortColumn == 'givenname':
        if sortOrder == 'asc':
            customers=customers.order_by(Customer.GivenName.asc())
        else:
             customers=customers.order_by(Customer.GivenName.desc())
    elif sortColumn == 'surname':
        if sortOrder == 'asc':
            customers=customers.order_by(Customer.Surname.asc())
        else:
             customers=customers.order_by(Customer.Surname.desc())
    elif sortColumn == 'city':
        if sortOrder == 'asc':
            customers=customers.order_by(Customer.City.asc())
        else:
             customers=customers.order_by(Customer.City.desc())
    
    paginationObject = customers.paginate(page=page, per_page=20, error_out=False)
    return render_template("customers.html", 
                           customers=paginationObject.items,
                           pages=paginationObject.pages,
                           sortOrder=sortOrder,
                           sortColumn=sortColumn,
                           page=page,
                           has_prev=paginationObject.has_prev,
                           has_next=paginationObject.has_next,
                           q = q)

@app.route("/customer/<c_id>")
@auth_required()
@roles_accepted("Admin","Staff")
def customer(c_id):
    
   
    return render_template("customer.html", 
                           customer=Customer.query.filter_by(Id=c_id).first(), activepage = 'customers')
@app.route("/admin")
@auth_required()
@roles_accepted("Admin")
def admin():
    return render_template("admin.html", activePage="secretPage")





@app.route("/account/<a_id>")
@auth_required()
def account(a_id):
    account = Account.query.filter_by(Id=a_id).first()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    return render_template('account.html',account=account,trans=trans)
                             
                           

@app.route("/transactions/<int:id>", methods=['GET', 'POST'])
@auth_required()    #komentera den här rad när du kör unittester
@roles_accepted("Admin")    #komentera den här rad när du kör unittester
def transactions(id):
    
    account = Account.query.filter_by(Id=id).first()
    transactions = Transaction.query.filter_by(Id=id).first()
    form= TransactionsForm()
    message = ["Beloppet är stort"]
    message_2 = ["Must be positive"]
    if form.validate_on_submit():
     
        
                
        account = Account.query.filter_by(Id=int(form.account.data)).first()#konto som jag vill ha 
        if account.Balance < form.amount.data:
             form.amount.errors = form.amount.errors + message
        elif form.amount.data < 0:
             form.amount.errors = form.amount.errors + message_2
        else:           
                    
                    account.Balance= account.Balance - form.amount.data
            
                    newtrans =Transaction(Type="Credit",Operation ="withdraw" ,Date = datetime.now(),
                                    NewBalance =account.Balance,AccountId = form.account.data,
                                    Amount = form.amount.data)
            
                    db.session.add(newtrans)
                    db.session.commit()
    


                    account = Account.query.filter_by(Id=int(form.account_2.data)).first()
                    account.Balance = account.Balance + form.amount.data
                #samma sak men annan konto(en for deposite och en for withdrawing)
             
                    newtrans = Transaction(Type="Debit", Operation="Deposite", Date= datetime.now(),
                                   NewBalance= account.Balance,
                                   AccountId = form.account_2.data,
                                   Amount = form.amount.data)
                    db.session.add(newtrans)
                    db.session.commit()
               
           

               
                    return redirect("/account/" + str(id))
       
    return render_template("transactions.html",transaction = transactions,account=account,formen=form)
                           
            
                    



if __name__  == "__main__":
    with app.app_context():
         upgrade()
    
         seedData(app,db)
         app.run()
    













        
    
    
        