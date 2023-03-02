import unittest
from flask import Flask, render_template, request, url_for, redirect
from app import app
from model import db, Customer, User,Role,Account
from flask_security import Security,SQLAlchemyUserDatastore, hash_password
from sqlalchemy import create_engine
from datetime import datetime
#from flask_sqlalchemy import SQLAlchemy


def set_current_user(app, ds, email):
    """Set up so that when request is received,
    the token will cause 'user' to be made the current_user
    """

    def token_cb(request):
        if request.headers.get("Authentication-Token") == "token":
            return ds.find_user(email=email)
        return app.security.login_manager.anonymous_user()

    app.security.login_manager.request_loader(token_cb)


init = False

class FormsTestCases(unittest.TestCase):
    # def __init__(self, *args, **kwargs):
    #     super(FormsTestCases, self).__init__(*args, **kwargs)
    def tearDown(self):
        self.ctx.pop()
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        #self.client = app.test_client()
        app.config["SERVER_NAME"] = "ranim.se"
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['SECURITY_FRESHNESS_GRACE_PERIOD'] = 123454
        global init
        if not init:
            #db.init_app(app)
            db.create_all()
            init = True
            user_datastore = SQLAlchemyUserDatastore(db, User, Role)
            app.security = Security(app, user_datastore,register_blueprint=False)
            app.security.init_app(app, user_datastore,register_blueprint=False)
            app.security.datastore.db.create_all()


    def test_when_withdrawing_more_than_balance_should_show_errormessage(self):
        # arrangera världen så att kund med id 1 har amount 100
        # ta ut 200
        # kolla i resultat HTML = "Belopp to large"
        customer = Customer()
        customer.GivenName= "Sara"
        customer.Surname="blabla"
        customer.TelephoneCountryCode = "1223"
        customer.Telephone = "0780000011"
        customer.City = "Sundes"
        customer.Streetaddress="dhdidjjdk"
        customer.Birthday="20200101"
        customer.Zipcode="1234"
        customer.Country="Sweden"
        customer.CountryCode="se"
        customer.NationalId="1223"
        customer.EmailAddress="ww@re.se"
        customer.Amount=1


        db.session.add(customer)
        db.session.commit()
       
        account = Account()
        account.AccountType="Personal"
        account.Created=datetime.now()
        account.Balance=5200
        account.CustomerId=customer.Id
        db.session.add(account)
        db.session.commit()

        test_client = app.test_client()
        
        with test_client:
            customer = Customer.query.filter_by(Id=customer.Id).first()
            url = '/withdraw/'+ str(account.Id)
            response = test_client.post(url, data={"amount":6000})
            s = response.data.decode("utf-8") 
            ok = 'Beloppet är stort' in s
            self.assertTrue(ok)

   

    def test_when_tranfer_negative_amount_show_errormessage(self):
        customer = Customer()
        customer.GivenName= "Sara"
        customer.Surname="blabla"
        customer.TelephoneCountryCode = "1223"
        customer.Telephone = "0780000011"
        customer.City = "Sundes"
        customer.Streetaddress="dhdidjjdk"
        customer.Birthday="20200101"
        customer.Zipcode="1234"
        customer.Country="Sweden"
        customer.CountryCode="se"
        customer.NationalId="1223"
        customer.EmailAddress="ww@re.se"
        customer.Amount=100
        db.session.add(customer)
        db.session.commit()
       

        account = Account()
        account.AccountType="Personal"
        account.Created=datetime.now()
        account.Balance=5200
        account.CustomerId= customer.Id
        db.session.add(account)
        db.session.commit()

        account_2 = Account()
        account_2.AccountType="Personal"
        account_2.Created=datetime.now()
        account_2.Balance=5200
        account_2.CustomerId= customer.Id
        db.session.add(account)
        db.session.commit()

        test_client = app.test_client()
        with test_client:
             url = '/transactions/' + str(account.Id)
             response = test_client.post(url, data={"amount":-100,"account":"1","account_2":"2"})
             s = response.data.decode("utf-8") 
             ok='Must be positive' in s
             self.assertTrue(ok)

        
        
    def test_when_amount_which_want_withdraw_shounld_be_positive_show_errormessage(self):
        customer = Customer()
        customer.GivenName= "Sara"
        customer.Surname="blabla"
        customer.TelephoneCountryCode = "1223"
        customer.Telephone = "0780000011"
        customer.City = "Sundes"
        customer.Streetaddress="dhdidjjdk"
        customer.Birthday="20200101"
        customer.Zipcode="1234"
        customer.Country="Sweden"
        customer.CountryCode="se"
        customer.NationalId="1223"
        customer.EmailAddress="ww@re.se"
        customer.Amount=100
        db.session.add(customer)
        db.session.commit()

        account = Account()
        account.AccountType="Personal"
        account.Created=datetime.now()
        account.Balance=5200
        account.CustomerId=customer.Id
        db.session.add(account)
        db.session.commit()
        test_client = app.test_client()
        with test_client:
             
             url = '/withdraw/' + str(account.Id) 
             response = test_client.post(url, data={"amount":-50})
             s = response.data.decode("utf-8") 
             ok = 'Must be positive' in s
             self.assertTrue(ok)
    
    def test_when_amount_which_want_deposite_should_be_positive_show_errormessage(self):
        customer = Customer()
        customer.GivenName= "Sara"
        customer.Surname="blabla"
        customer.TelephoneCountryCode = "1223"
        customer.Telephone = "0780000011"
        customer.City = "Sundes"
        customer.Streetaddress="dhdidjjdk"
        customer.Birthday="20200101"
        customer.Zipcode="1234"
        customer.Country="Sweden"
        customer.CountryCode="se"
        customer.NationalId="1223"
        customer.EmailAddress="ww@re.se"
        customer.Amount=100
        db.session.add(customer)
        db.session.commit()

        account = Account()
        account.AccountType="Personal"
        account.Created=datetime.now()
        account.Balance=5200
        account.CustomerId=customer.Id
        db.session.add(account)
        db.session.commit()
        test_client = app.test_client()
        with test_client:
           
            url = '/deposite/' + str(account.Id)
            response = test_client.post(url, data={"amount":-50})
            s = response.data.decode("utf-8")
            ok = 'Must be positive' in s
            self.assertTrue(ok)
    

if __name__ == "__main__":
    unittest.main()


    #komentera auth_required och roles_accepted när du kör unittester