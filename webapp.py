import streamlit as st
from PIL import Image
import re
import cv2
import numpy as np
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
import gdown
from keras.preprocessing import image
import os
file_path = "sugarcane_disease_model.h5"
if not os.path.exists(file_path):
    gdown.download( id= "1GKZq8iMh2RO9BMg2lag8jhmc_IZWSBK3", output="sugarcane_disease_model.h5", quiet=False)
    gdown.download( id= "1-5hXemE0DFVrpIQoHgjKhXoLpULDBJUd", output="encoder.pkl", quiet=False)

# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()

# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(FirstName TEXT,LastName TEXT,Mobile TEXT,Email TEXT,password TEXT,Cpassword TEXT)')
def add_userdata(FirstName,LastName,Mobile,Email,password,Cpassword):
    c.execute('INSERT INTO userstable(FirstName,LastName,Mobile,Email,password,Cpassword) VALUES (?,?,?,?,?,?)',(FirstName,LastName,Mobile,Email,password,Cpassword))
    conn.commit()
def login_user(Email,password):
    c.execute('SELECT * FROM userstable WHERE Email =? AND password = ?',(Email,password))
    data = c.fetchall()
    return data
def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data
def delete_user(Email):
    c.execute("DELETE FROM userstable WHERE Email="+"'"+Email+"'")
    conn.commit()
    
menu1 = ["Home","Login", "Signup"]
choice1 = st.sidebar.selectbox("menu",menu1)
if choice1=="Home":
    #html
    testp="<p style='font-size: 17px;text-align:center;font-family:verdana;text-align: justify'>This website is made to check what kind of Sugarcane Leaf Diseases is shown in the submitted image.</p>"
    st.markdown(testp,unsafe_allow_html=True)

if choice1=="Login":
    st.subheader("Login Section")
    Email=st.sidebar.text_input('Email')
    password=st.sidebar.text_input('Password',type='password')
    b1=st.sidebar.checkbox("login")
    if b1:
        #Validation
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, Email):
            create_usertable()
            if Email=='a@a.com' and password=='123':
                st.success("Logged In as {}".format("Admin"))
                Email=st.text_input("Delete Email")
                if st.button('Delete'):
                    delete_user(Email)
                user_result = view_all_users()
                clean_db = pd.DataFrame(user_result,columns=["FirstName","LastName","Mobile","Email","password","Cpassword"])
                st.dataframe(clean_db)
            else:
                result = login_user(Email,password)
                if result:
                    imgur=st.file_uploader("Browse Sugarcane Leaf Image")
                    if imgur:
                        image=Image.open(imgur)
                        image.save("original.jpg")
                        img1= Image.open("original.jpg")
                        st.image(img1, width=200)
                        b2=st.button("Predict")
                        if b2:
                            model=load_model("sugarcane_disease_model.h5")
                            encoder=pickle.load(open("encoder.pkl","rb"))
                            timg=cv2.imread("original.jpg")
                            timg=cv2.resize(timg,(224,224))
                            timg=np.expand_dims(timg,axis=0)
                            prd=encoder.categories_[0][int(np.argmax(model.predict(timg),axis=1)[0])]
                            st.success(prd)
                else:
                    st.warning("Incorrect Email/Password")  
        else:
            st.warning("Not Valid Email")

if choice1=="Signup":
    st.subheader("Signup Section")
    FirstName=st.text_input('First Name')
    LastName=st.text_input('Last Name')
    Mobile=st.text_input('Contact No')
    Email=st.text_input('Email')
    new_password=st.text_input('Password',type='password')
    Cpassword=st.text_input('Confirm Password',type='password')
    b4=st.button("Sign up")
    if b4:
        if new_password==Cpassword:
            #Validation
            pattern=re.compile("(0|91)?[7-9][0-9]{9}")
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if (pattern.match(Mobile)):
                if re.fullmatch(regex, Email):
                    create_usertable()
                    add_userdata(FirstName,LastName,Mobile,Email,new_password,Cpassword)
                    st.success("You have successfully created a valid Account")
                    st.info("Go to Login Menu to login")
                else:
                    st.warning("Not Valid Email")               
            else:
                st.warning("Not Valid Mobile Number")
        else:
            st.warning("Password Does not Match")
            
            
            
            
            
            