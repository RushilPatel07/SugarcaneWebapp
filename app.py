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
                                    "Banded Chlorosis is a common symptom observed in sugarcane leaves, where yellow bands or stripes appear parallel to the veins, while the rest of the leaf remains green. This condition is typically a sign of nutrient deficiency, especially of iron or zinc, which affects chlorophyll production. It may also indicate underlying soil issues such as poor drainage or imbalanced pH levels. If left untreated, banded chlorosis can reduce the plant’s photosynthetic efficiency, leading to stunted growth and decreased sugarcane yield. Early detection through image-based models helps in timely corrective action and improves crop health.",
                                    "To prevent and manage Banded Chlorosis in sugarcane, it is important to ensure balanced soil nutrition and proper field management. Regular soil testing can help identify deficiencies, especially of micronutrients like iron and zinc. Applying appropriate fertilizers or foliar sprays containing these nutrients can effectively correct the condition. Improving soil drainage, avoiding waterlogging, and maintaining optimal pH levels also support nutrient uptake. Early detection through visual monitoring or automated disease detection models enables timely intervention, reducing the risk of long-term crop damage."
                                ),
                                "BrownRust": (
                                    "Brown Rust is a fungal disease that affects sugarcane leaves, caused by Puccinia melanocephala. It appears as small, round to oval, reddish-brown pustules scattered mainly on the upper leaf surfaces. These pustules release spores that spread easily through wind and rain, leading to rapid infection under warm and humid conditions. Brown Rust reduces photosynthetic area and weakens the plant, which can result in lower sugar content and reduced cane yield if the infection is severe.",
                                    "To prevent and control Brown Rust, it is essential to use resistant sugarcane varieties and practice crop rotation to reduce fungal buildup in the soil. Fungicide applications during the early stages of infection can help limit disease spread. Maintaining good field sanitation by removing infected crop residues and controlling weeds also minimizes inoculum sources. Early detection through field scouting or automated disease detection systems allows timely treatment and protects overall crop health."
                                ),
                                "Brown Spots": (
                                    "Brown Spots is a fungal disease commonly seen on sugarcane leaves, characterized by small, irregularly shaped brown lesions that may enlarge and merge over time. These spots often have a darker border and can cause the affected leaf tissue to dry out and die. The disease thrives in warm, humid environments and can spread rapidly, reducing the photosynthetic area of the leaves, which negatively impacts plant growth and sugar production.",
                                    "To manage Brown Spots, it is important to maintain proper field hygiene by removing infected leaves and crop debris that can harbor fungal spores. Using disease-resistant varieties and ensuring good airflow through appropriate planting density helps reduce humidity levels that favor disease development. Fungicide sprays applied during the early signs of infection can effectively control the spread. Monitoring the crop regularly using visual inspection or automated detection models ensures timely intervention and helps maintain healthy sugarcane plants."
                                ),
                                "Dried Leaves": (
                                    "Dried Leaves in sugarcane refer to the condition where leaves lose moisture, turn brown, and become brittle, often as a result of environmental stress, disease, or nutrient deficiencies. This symptom can be caused by factors such as drought, excessive heat, fungal infections, or lack of essential nutrients like potassium. Dried leaves reduce the plant’s ability to perform photosynthesis effectively, leading to weakened growth and lower sugar yields.",
                                    "To prevent and manage Dried Leaves, it is important to ensure adequate irrigation, especially during dry periods, and maintain balanced soil fertility through proper fertilization. Protecting the crop from fungal infections by applying fungicides when needed and improving field drainage can also help reduce stress on the plants. Early detection through visual checks or disease detection models allows farmers to respond promptly, minimizing damage and supporting healthy sugarcane development."
                                ),
                                "Grassy shoot": (
                                    "Grassy Shoot is a serious disease of sugarcane caused by the Phytoplasma pathogen. Infected plants show excessive proliferation of thin, pale green shoots that resemble grass blades instead of normal thick cane stalks. These shoots lack proper internode development and produce few or no leaves, severely affecting cane growth and yield. The disease spreads through insect vectors like leafhoppers and by using infected planting material.",
                                    "To control Grassy Shoot, it is crucial to use disease-free and certified seed cane for planting. Removing and destroying infected plants helps reduce the spread of the disease. Controlling insect vectors with appropriate insecticides can also limit transmission. Regular field monitoring and early detection using visual symptoms or automated models enable timely action to protect healthy crops and improve sugarcane productivity."
                                ),
                                "Pokkah Boeng": (
                                    "Pokkah Boeng is a fungal disease that affects sugarcane, caused by Fusarium moniliforme. It is characterized by twisted, stunted, and malformed leaves with distinctive reddish or purple streaks and lesions. The infected leaves often show a distortion that resembles burning or scorching, which can reduce photosynthesis and weaken the plant. The disease is more prevalent in warm, humid conditions and can significantly reduce cane yield and quality if left unmanaged.",
                                    "To prevent and manage Pokkah Boeng, it is important to plant disease-free seed material and use resistant sugarcane varieties when available. Proper field sanitation, including the removal of infected plant debris, helps reduce fungal spores in the field. Avoiding excessive nitrogen fertilizer and maintaining balanced nutrition can reduce disease severity. Early detection through visual inspection or automated disease detection models allows for timely fungicide applications and effective disease control, protecting crop health."
                                ),
                                "Sett Rot": (
                                    "Sett Rot is a fungal disease in sugarcane caused by Macrophomina phaseolina. It affects the setts (cuttings) used for planting, leading to rotting of the buds and basal parts of the cane pieces. Infected setts fail to sprout properly or produce weak shoots, resulting in poor crop establishment and reduced yield. The disease thrives in warm and dry conditions and can spread through contaminated planting material and soil.",
                                    "To prevent and manage Sett Rot, it is important to use healthy, disease-free setts for planting. Treating the setts with fungicides before planting can effectively reduce infection. Crop rotation and proper field sanitation, including removal of infected debris, help minimize soil-borne inoculum. Ensuring optimal soil moisture and avoiding planting in excessively dry or stressed conditions also reduce disease incidence. Early detection and careful monitoring support timely interventions for healthy sugarcane growth."
                                ),
                                "smut": (
                                    "Smut is a fungal disease of sugarcane caused by Sporisorium scitamineum. It is characterized by the appearance of a black, whip-like structure called a smut whip that emerges from the growing shoot or the top of the cane stalk. The infected shoots become distorted and stunted, and the disease spreads rapidly through spores carried by wind and rain. Smut reduces the overall vigor of the plant and significantly lowers sugarcane yield and quality.",
                                    "To control Smut, it is essential to use disease-free and certified seed cane for planting. Hot water treatment of setts before planting can help eliminate the pathogen. Removing and destroying infected plants and practicing crop rotation reduce disease spread. Early detection through visual symptoms or automated disease detection tools allows timely removal of infected canes, limiting the impact on the crop and supporting healthy sugarcane production."
                                ),
                                "Viral Disease": (
                                    "Viral Disease in sugarcane refers to infections caused by various plant viruses that disrupt normal growth and development. Symptoms often include mosaic patterns, yellowing, stunted growth, and malformed leaves. Viral diseases are usually transmitted by insect vectors such as aphids, whiteflies, or leafhoppers, or through infected planting material. These diseases reduce photosynthesis, weaken the plant, and cause significant yield losses.",
                                    "To manage Viral Diseases, using virus-free planting material is critical. Controlling insect vectors through appropriate insecticide applications helps limit virus spread. Regular field inspections and early detection with visual checks or automated detection models allow for quick removal of infected plants to prevent further transmission. Integrating resistant sugarcane varieties and practicing crop hygiene are also effective strategies for minimizing viral disease impact."
                                ),
                                "Yellow Leaf": (
                                    "Yellow Leaf is a viral disease of sugarcane caused by the Sugarcane Yellow Leaf Virus (SCYLV). It is characterized by yellowing of the leaf midrib and adjacent tissues, which eventually spreads to the entire leaf blade. Infected plants show stunted growth, reduced tillering, and poor cane quality. The disease is primarily transmitted by the aphid vector Melanaphis sacchari and through infected planting material, leading to significant yield losses if unmanaged.",
                                    "To prevent and control Yellow Leaf disease, it is essential to use virus-free seed cane and adopt strict quarantine measures. Managing aphid populations with insecticides reduces virus transmission. Regular monitoring through visual inspection or automated detection systems enables early identification and removal of infected plants. Cultivating resistant sugarcane varieties and maintaining good field hygiene further help in minimizing the spread and impact of this disease."
                                ),
                                "Healthy Leaves": (
                                    "Healthy sugarcane leaves are green, turgid, and disease-free.",
                                    "To maintain Healthy Leaves, it is important to provide balanced fertilization, adequate irrigation, and proper pest and disease management. Regular field monitoring helps detect early signs of stress or infection, allowing timely intervention. Using disease-free planting material and maintaining good agricultural practices support overall plant health and contribute to higher sugarcane yields."
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
