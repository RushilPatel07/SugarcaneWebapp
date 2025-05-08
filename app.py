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
    gdown.download( id= "1YEF6cAAds6JYxMDemKYnPzqIWt8nVJoj", output="sugarcane_disease_model.h5", quiet=False)
    gdown.download( id= "1-5hXemE0DFVrpIQoHgjKhXoLpULDBJUd", output="encoder.pkl", quiet=False)

# DB Management
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()

st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #D6AD60;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: black;
        color: white;
    }

    /* Sidebar text and labels */
    section[data-testid="stSidebar"] .css-1v3fvcr, .css-10trblm {
        color: white;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: black;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Predict Button */
    .stButton>button {
        background-color: #F4EBD0;
        color: black;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #B68D40;
        color: white;
    }

    /* Inputs and other elements - no background, keep clean */
    .stTextInput>div>div>input,
    .stTextArea>div>textarea {
        color: black;
        font-weight: 500;
    }

    /* Dataframe and tables */
    .css-1d391kg {
        background-color: transparent;
    }

    /* Markdown text styling */
    .markdown-text-container {
        color: black;
        font-size: 17px;
    }
    </style>
""", unsafe_allow_html=True)



# DB Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(FirstName TEXT, LastName TEXT, Mobile TEXT, Email TEXT, password TEXT, Cpassword TEXT)')
def add_userdata(FirstName, LastName, Mobile, Email, password, Cpassword):
    c.execute('INSERT INTO userstable(FirstName, LastName, Mobile, Email, password, Cpassword) VALUES (?,?,?,?,?,?)', (FirstName, LastName, Mobile, Email, password, Cpassword))
    conn.commit()
def login_user(Email, password):
    c.execute('SELECT * FROM userstable WHERE Email =? AND password = ?',(Email, password))
    data = c.fetchall()
    return data
def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data
def delete_user(Email):
    c.execute("DELETE FROM userstable WHERE Email="+"'"+Email+"'")
    conn.commit()

# Function to apply CSS styles
def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Predict Button styling */
        .stButton>button {
            background-color: #F4EBD0;
            color: #122620;
            border-radius: 10px;
            border: none;
        }

        /* Button Hover Effect */
        .stButton>button:hover {
            background-color: #B68D40;
        }

        /* Labels (text outside input boxes) */
        label, .stTextInput > label, .stSelectbox > label, .stCheckbox > label {
            color: black !important;
        }

        /* Text inside text boxes (inputs) */
        input, textarea {
            color: white !important;
            background-color: #333 !important;  /* optional: dark background for contrast */
        }

        /* Sidebar background color */
        section[data-testid="stSidebar"] {
            background-color: black;
            color: white;
        }

        /* Header styling */
        h1, h2, h3, h4, h5, h6 {
            color: #122620;
        }
        </style>
        """, unsafe_allow_html=True
    )



apply_custom_styles()  # Apply the color styles

menu1 = ["Home", "Login", "Signup"]
choice1 = st.sidebar.selectbox("Menu", menu1)

if choice1 == "Home":
    st.markdown("<h1 style='text-align: center; color: black;'>Sugarcane Leaf Diseases Detection</h1>", unsafe_allow_html=True)
    
    description = """
    <p style='font-size: 17px; text-align: justify; font-family: Verdana; color: black;'>
    This application uses a deep learning model to identify various sugarcane leaf diseases from uploaded images.
    Sugarcane, a vital commercial crop, is prone to several foliar diseases that can significantly affect yield and quality.
    Early detection of diseases such as red rot, rust, and leaf scald allows for timely intervention and better crop management.
    Simply upload a clear image of the infected sugarcane leaf to receive a prediction.
    </p>
    """
    st.markdown(description, unsafe_allow_html=True)


if choice1 == "Login":
    st.markdown("<h2 style='color:black;'>Login Section</h2>", unsafe_allow_html=True)
    Email = st.sidebar.text_input('Email')
    password = st.sidebar.text_input('Password', type='password')
    b1 = st.sidebar.checkbox("Login")
    
    if b1:
        # Validation
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, Email):
            create_usertable()
            if Email == 'a@a.com' and password == '123':
                st.success("Logged In as {}".format("Admin"))
                Email = st.text_input("Delete Email")
                if st.button('Delete'):
                    delete_user(Email)
                user_result = view_all_users()
                clean_db = pd.DataFrame(user_result, columns=["FirstName", "LastName", "Mobile", "Email", "password", "Cpassword"])
                st.dataframe(clean_db)
            else:
                result = login_user(Email, password)
                st.markdown("<p style='color:black;'> Model Accuracy : 91 % </p>", unsafe_allow_html=True)
                if result:
                    imgur = st.file_uploader("Browse Sugarcane Leaf Image")
                    if imgur:
                        image = Image.open(imgur)
                        image.save("original.jpg")
                        img1 = Image.open("original.jpg")
                        st.image(img1, width=200)
                        b2 = st.button("Predict")
                        if b2:
                            model = load_model("sugarcane_disease_model.h5")
                            encoder = pickle.load(open("encoder.pkl", "rb"))
                            timg = cv2.imread("original.jpg")
                            timg = cv2.resize(timg, (224, 224))
                            timg = np.expand_dims(timg, axis=0)
                            prd = encoder.categories_[0][int(np.argmax(model.predict(timg), axis=1)[0])]
                            st.success(prd)
                            
                            diseases = {
                                "Banded Chlorosis": (
                                    "Banded chlorosis causes yellow bands across leaves due to nutrient deficiency or viral infection.",
                                    "Use balanced fertilizers and virus-free setts."
                                ),
                                "BrownRust": (
                                    "Brown rust appears as reddish-brown pustules on leaves affecting photosynthesis.",
                                    "Use resistant varieties and fungicides."
                                ),
                                "Brown Spots": (
                                    "Brown spots are small lesions caused by fungal infections on sugarcane leaves.",
                                    "Avoid waterlogging and apply proper fungicides."
                                ),
                                "Dried Leaves": (
                                    "Leaves dry due to drought, pests, or poor nutrition.",
                                    "Maintain irrigation and proper fertilization."
                                ),
                                "Grassy shoot": (
                                    "Caused by phytoplasma, results in bushy, grassy appearance.",
                                    "Use hot water treatment and healthy planting material."
                                ),
                                "Pokkah Boeng": (
                                    "This fungal disease deforms young leaves and top shoots.",
                                    "Use fungicides and destroy affected plants."
                                ),
                                "Sett Rot": (
                                    "Sett rot rots the planting setts due to fungal or bacterial pathogens.",
                                    "Use fungicide-treated, disease-free setts for planting."
                                ),
                                "smut": (
                                    "Smut causes whip-like growth on the stalk due to fungal infection.",
                                    "Remove infected plants and use resistant varieties."
                                ),
                                "Viral Disease": (
                                    "Viral infections cause mosaic, chlorosis, and stunted growth.",
                                    "Use certified virus-free seed cane and control vectors."
                                ),
                                "Yellow Leaf": (
                                    "Caused by phytoplasma, it leads to yellowing from midrib to edge.",
                                    "Use healthy setts and vector control practices."
                                ),
                                "Healthy Leaves": (
                                    "Healthy sugarcane leaves are green, turgid, and disease-free.",
                                    "Maintain optimal irrigation, nutrients, and disease control."
                                )
                            }
                            
                            if prd in diseases:
                                definition, precaution = diseases[prd]
                                st.error(f"Definition: {definition}")
                                st.warning(f"Precaution: {precaution}")
                            else:
                                st.warning("Please upload a valid sugarcane image.")
                else:
                    st.warning("Incorrect Email/Password")  
        else:
            st.warning("Not Valid Email")

if choice1 == "Signup":
    st.markdown("<h2 style='color:black;'>Signup Section</h2>", unsafe_allow_html=True)
    FirstName = st.text_input('First Name')
    LastName = st.text_input('Last Name')
    Mobile = st.text_input('Contact No')
    Email = st.text_input('Email')
    new_password = st.text_input('Password', type='password')
    Cpassword = st.text_input('Confirm Password', type='password')
    b4 = st.button("Sign up")
    
    if b4:
        if new_password == Cpassword:
            # Validation
            pattern = re.compile("(0|91)?[7-9][0-9]{9}")
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if pattern.match(Mobile):
                if re.fullmatch(regex, Email):
                    create_usertable()
                    add_userdata(FirstName, LastName, Mobile, Email, new_password, Cpassword)
                    st.success("You have successfully created a valid Account")
                    st.info("Go to Login Menu to login")
                else:
                    st.warning("Not Valid Email")               
            else:
                st.warning("Not Valid Mobile Number")
        else:
            st.warning("Password Does not Match")
