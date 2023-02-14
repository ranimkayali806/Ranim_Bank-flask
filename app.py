

from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from model import db, seedData, Customer, Account
from flask_wtf import FlaskForm
from forms import WithdrawForm , DepositeForm
import os
from flask_security import roles_accepted, auth_required, logout_user

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:R0944351861m.@localhost/Bank'
#app.config['SECRET_KEY'] = os.urandom(32)  för secerhet
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
 
 

@app.route("/")
def startpage():
   
     return render_template("index.html", activePage="startPage" )
   # pass
    
# @app.route('/withdraw', method = ['Get','Post'])
# def withdraw():
#     form = WithdrawForm()
#     if form.validate_on_submit():
#         return redirect("")
#     return render_template('withdraw.html',formen=form)

# @app.route('/deposit', method=['Get','Post'])
# def Deposite():
#     form = DepositeForm()
#     if form.validate_on_submit():
#         return redirect("")
#     return render_template('Deposite.html',formen = form)


@app.route("/customerimage/<id>")
def customerimagepage(id):
     customer = Customer.query.filter_by(Id = id).first()
     return render_template("customerimage.html", customer=customer )



@app.route("/customers")
def customers():  #/customers?sortColumn=surname&sortOrder=asc"page=11
    sortColumn = request.args.get('sortColumn', 'givenname')
    sortColumn = request.args.get('sortColumn', 'surname')
    sortOrder = request.args.get('sortOrder','asc')
    q = request.args.get('q','')
    page = int(request.args.get('page' , 1))
    

    customers = Customer.query  #kanske inte all(check)
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

@app.route("/customer/<id>")
def customer(id):
    length = request.args.get('length', '')
    # customer_1 = Customer.query.filter_by(Id=id).first()
    return render_template("customer.html", 
                           
                        #    customer = customer_1)
                           customer=Customer.query.filter_by(Id=id).first(), activepage = 'customers',length = length)

@app.route('/account/<id>')
def account(id):
    # sortColumn = request.args.get('sortColumn', 'transactions')
    # sortOrder = request.args.get('sortOrder','desc')
    # q = request.args.get('q','')
  
    
    # if sortColumn == 'transactions':
    #     if sortOrder == 'desc':
    #         customer=customer.order_by(Account.Transactions.desc())
    
    return render_template('account.html',account=Account.query.filter_by(Id=id).first())
                           
                          
                         



if __name__  == "__main__":
    with app.app_context():
         upgrade()
    
         seedData(app,db)
         app.run()
    













        
    
    
        