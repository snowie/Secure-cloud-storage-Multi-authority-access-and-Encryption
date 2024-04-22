import pickle
import pandas as pd
import numpy as np
import streamlit as st
from streamlit import session_state
from pymongo import MongoClient
import streamlit as st
import smtplib, ssl
import smtplib
# creates SMTP session
server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
MAIL_ID = "YOUR_MAIL_ID"
APP_PASSWORD = "YOUR_APP_PASSWORD"
RECEIVER1 = "RECEIVER!_MAIL_ID"
server.login(MAIL_ID, APP_PASSWORD)


@st.cache_resource
def init_connection():
    return MongoClient("MONGO_URI")

client = init_connection()
db = client["disease_prediction"]
users_collection = db["patient_data"]

session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0
def signup():
    st.title("Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")

        if st.form_submit_button("Signup"):
            if password == confirm_password:
                user = create_account(name, email, age, sex, password)
                session_state["logged_in"] = True
                session_state["user_info"] = user
            else:
                st.error("Passwords do not match. Please try again.")


def check_login(username, password):
    user = users_collection.find_one({"email": username, "password": password})
    if user:
        session_state["logged_in"] = True
        session_state["user_info"] = user
        st.success("Login successful!")
        return user
    else:
        st.error("Invalid credentials. Please try again.")
        return None


def generate_medical_report(predicted_labels):
    # Define class labels and corresponding medical information for each disease
    medical_info = {
        "Breast Cancer": {
            "report": "Based on the analysis, there are indications of breast cancer. Immediate medical attention is necessary for further diagnosis and treatment.",
            "preventative_measures": [
                "Consult with an oncologist for further evaluation",
                "Discuss treatment options such as surgery, chemotherapy, or radiation therapy",
                "Stay informed about breast cancer awareness and early detection methods",
            ],
            "precautionary_measures": [
                "Schedule regular screenings for breast cancer",
                "Consider genetic testing if there is a family history of breast cancer",
            ],
        },
        "Diabetes": {
            "report": "It appears that the patient has diabetes. Proper management and lifestyle changes are essential to prevent complications.",
            "preventative_measures": [
                "Monitor blood sugar levels regularly",
                "Adopt a healthy diet and exercise regularly",
                "Take prescribed medications as directed by healthcare professionals",
            ],
            "precautionary_measures": [
                "Attend diabetes education classes to learn more about managing the condition",
                "Keep emergency contact information readily available in case of diabetic emergencies",
            ],
        },
        "PCOS": {
            "report": "The patient exhibits signs of polycystic ovary syndrome (PCOS). Early intervention and lifestyle modifications can help manage the condition.",
            "preventative_measures": [
                "Maintain a healthy weight through diet and exercise",
                "Monitor hormone levels and menstrual cycles regularly",
                "Consult with a healthcare provider for personalized treatment options",
            ],
            "precautionary_measures": [
                "Stay informed about PCOS and its potential complications",
                "Seek support from healthcare professionals and support groups for managing PCOS symptoms",
            ],
        },
        "Heart Disease": {
            "report": "There are indications of heart disease in the patient. Prompt medical attention and lifestyle changes are crucial for managing the condition.",
            "preventative_measures": [
                "Adopt a heart-healthy diet low in saturated fats and cholesterol",
                "Engage in regular physical activity to improve heart health",
                "Monitor blood pressure and cholesterol levels regularly",
            ],
            "precautionary_measures": [
                "Follow prescribed medication regimen as directed by healthcare professionals",
                "Attend cardiac rehabilitation programs if recommended by healthcare providers",
            ],
        },
    }

    # Generate medical report for each predicted label
    reports = []
    precautions = []

    if len(predicted_labels) == 0:
        reports.append("No diseases were detected.")
        precautions.append([])  # No precautionary measures needed if no diseases detected
    else:
        for label in predicted_labels:
            medical_report = medical_info[label]["report"]
            preventative_measures = medical_info[label]["preventative_measures"]
            precautionary_measures = medical_info[label]["precautionary_measures"]

            report = (
                f"Medical Report for {label}:\n\n"
                + medical_report
                + "\n\nPreventative Measures:\n\n- "
                + ",\n- ".join(preventative_measures)
                + "\n\nPrecautionary Measures:\n\n- "
                + ",\n- ".join(precautionary_measures)
            )
            reports.append(report)
            precautions.append(precautionary_measures)
            
    report = "\n\n".join(reports)
    preventative_measures = ""
    for precaution in precautions:
        preventative_measures += ", ".join(precaution)

    return report, preventative_measures


def initialize_database():
    try:
        # Check if the users collection exists
        if "users" not in db.list_collection_names():
            db.create_collection("users")
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(name, email, age, sex, password):
    try:
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
            "report": None,
            "precautions": None,
            "diseases": None
        }
        result = users_collection.insert_one(user_info)
        user_info["_id"] = result.inserted_id
        st.success("Account created successfully! You can now login.")
        return user_info
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None

def login():
    st.title("Login Page")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def render_dashboard(user_info):
    try:
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("User Information:")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")

        if "diseases" in user_info and user_info["diseases"] is not None:
            st.subheader("Diseases:")
            for disease in user_info["diseases"]:
                st.write(disease)

        if isinstance(user_info["precautions"], list):
            st.subheader("Precautions:")
            for precaution in user_info["precautions"]:
                st.write(precaution)

    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")

        
def convert_categorical_to_numeric(value):
    if value == "Yes" or value == "Male" or value == "Regular":
        return 1
    elif value == "No" or value == "Female" or value == "Irregular":
        return 0
    else:
        return value

def main():
    st.sidebar.title("Multi-Disease Prediction System")
    page = st.sidebar.radio(
        "Go to",
        ("Signup/Login", "Dashboard", "Upload Information", "View Reports"),
        key="Multi-Disease Prediction System",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login()
        else:
            signup()

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"])
        else:
            st.warning("Please login/signup to view the dashboard.")

    elif page == "Upload Information":
        if session_state.get("logged_in"):
            st.title("Provide Information")
            # create a form to get the user's information
            with st.form("user_info_form"):
                st.write("Fill in the details below to provide your information:")
                age = st.number_input("Age:", min_value=0, max_value=120)
                gender = st.radio("Gender:", ("Male", "Female"))
                tumor_size = st.number_input("Tumor Size:", min_value=0.0, max_value=1.0)
                regional_node_examined = st.number_input("Regional Node Examined:", min_value=0.0, max_value=1.0)
                regional_node_positive = st.number_input("Regional Node Positive:", min_value=0.0, max_value=1.0)
                survival_months = st.number_input("Survival Months:", min_value=0.0, max_value=1.0)
                hypertension = st.radio("Hypertension:", ("Yes", "No"))
                heart_disease = st.radio("Heart Disease:", ("Yes", "No"))
                smoking_history = st.radio("Smoking History:", ("No Info", "Never", "Former", "Not Current", "Current", "Ever"))
                bmi = st.number_input("BMI:", min_value=0.0, max_value=1.0)
                hba1c_level = st.number_input("HbA1c Level:", min_value=0.0, max_value=1.0)
                blood_glucose_level = st.number_input("Blood Glucose Level:", min_value=0.0, max_value=1.0)
                education = st.number_input("Education:", min_value=0, max_value=4)
                current_smoker = st.radio("Current Smoker:", ("Yes", "No"))
                cigs_per_day = st.number_input("Cigarettes Per Day:", min_value=0, max_value=60)
                bp_meds = st.radio("BP Meds:", ("Yes", "No"))
                prevalent_stroke = st.radio("Prevalent Stroke:", ("Yes", "No"))
                prevalent_hyp = st.radio("Prevalent Hyp:", ("Yes", "No"))
                # diabetes = st.radio("Diabetes:", "Yes", "No")
                tot_chol = st.number_input("Total Cholesterol:", min_value=107, max_value=696)
                sys_bp = st.number_input("Systolic Blood Pressure:", min_value=83.5, max_value=295.0)
                dia_bp = st.number_input("Diastolic Blood Pressure:", min_value=48.0, max_value=140.0)
                heart_rate = st.number_input("Heart Rate:", min_value=40, max_value=143)
                glucose = st.number_input("Glucose:", min_value=40, max_value=394)
                follicle_no_r = st.number_input("Follicle No. (R):", min_value=0, max_value=20)
                follicle_no_l = st.number_input("Follicle No. (L):", min_value=0, max_value=22)
                skin_darkening = st.radio("Skin Darkening (Y/N):", ("Yes", "No"))
                hair_growth = st.radio("Hair Growth (Y/N):", ("Yes", "No"))
                weight_gain = st.radio("Weight Gain (Y/N):", ("Yes", "No"))
                cycle = st.radio("Cycle (R/I):",("Regular", "Irregular"))
                fast_food = st.radio("Fast Food (Y/N):", ("Yes", "No"))
                pimples = st.radio("Pimples (Y/N):", ("Yes", "No"))
                amh = st.number_input("AMH (ng/mL):", min_value=0.1, max_value=66.0)
                weight = st.number_input("Weight (Kg):", min_value=31, max_value=104)     
                RECEIVER2 = st.text_input("Enter the email address to send the report:")
                if st.form_submit_button("Submit"):
                    diseases = []              
                    breast_cancer_df = pd.DataFrame({
                        "Age": [age],
                        "Tumor Size": [tumor_size],
                        "Regional Node Examined": [regional_node_examined],
                        "Reginol Node Positive": [regional_node_positive],
                        "Survival Months": [survival_months]
                    })
                    model_breast_cancer = pickle.load(open('breast_cancer_model.pkl', 'rb'))
                    breast_cancer_prediction = model_breast_cancer.predict(breast_cancer_df)
                    if breast_cancer_prediction[0] == "Alive":
                        diseases.append("Breast Cancer")

                    diabetes_df = pd.DataFrame({
                        "gender": gender,
                        "age": [age],
                        "hypertension": [convert_categorical_to_numeric(hypertension)],
                        "heart_disease": [convert_categorical_to_numeric(heart_disease)],
                        "smoking_history": "No Info" if smoking_history == "No Info" else "current" if smoking_history == "Current" else "ever" if smoking_history == "Ever" else "former" if smoking_history == "Former" else "never" if smoking_history == "Never" else "not current" if smoking_history == "Not Current" else "No Info",
                        "bmi": [bmi],
                        "HbA1c_level": [hba1c_level],
                        "blood_glucose_level": [blood_glucose_level]
                    })
                    model_diabetes = pickle.load(open('diabetes_model.pkl', 'rb'))
                    diabetes_prediction = model_diabetes.predict(diabetes_df)
                    if diabetes_prediction[0] == 1:
                        diseases.append("Diabetes")

                    heart_disease_df = pd.DataFrame({
                        'male': [convert_categorical_to_numeric(gender)],
                        'age': [age],
                        'education': [education],
                        'currentSmoker': [convert_categorical_to_numeric(current_smoker)],
                        'cigsPerDay': [cigs_per_day],
                        'BPMeds': [convert_categorical_to_numeric(bp_meds)],
                        'prevalentStroke': [convert_categorical_to_numeric(prevalent_stroke)],
                        'prevalentHyp': [convert_categorical_to_numeric(prevalent_hyp)],
                        'diabetes': [convert_categorical_to_numeric(diabetes_prediction[0])],
                        'totChol': [tot_chol],
                        'sysBP': [sys_bp],
                        'diaBP': [dia_bp],
                        'BMI': [bmi],
                        'heartRate': [heart_rate],
                        'glucose': [glucose],
                    })
                    model_heart_disease = pickle.load(open('heart_disease.pkl', 'rb'))
                    heart_disease_prediction = model_heart_disease.predict(heart_disease_df)
                    if heart_disease_prediction[0] == 1:
                        diseases.append("Heart Disease")
                        
                    pcos_df = pd.DataFrame({
                        'Follicle No. (R)': [follicle_no_r],
                        'Follicle No. (L)': [follicle_no_l],
                        'Skin darkening (Y/N)': [convert_categorical_to_numeric(skin_darkening)],
                        'hair growth(Y/N)': [convert_categorical_to_numeric(hair_growth)],
                        'Weight gain(Y/N)': [convert_categorical_to_numeric(weight_gain)],
                        'Cycle(R/I)': [convert_categorical_to_numeric(cycle)],
                        'Fast food (Y/N)': [convert_categorical_to_numeric(fast_food)],
                        'Pimples(Y/N)': [convert_categorical_to_numeric(pimples)],
                        'AMH(ng/mL)': [amh],
                        'Weight (Kg)': [weight]
                    })
                    model_pcos = pickle.load(open('pcos_model.pkl', 'rb'))
                    pcos_prediction = model_pcos.predict(pcos_df)
                    if pcos_prediction[0] == 1:
                        diseases.append("PCOS")
                    report,precautions = generate_medical_report(diseases)
                    user_info = session_state["user_info"]
                    user_info["diseases"] = diseases
                    user_info["precautions"] = precautions
                    user_info["report"] = report
                    users_collection.update_one({"_id": user_info["_id"]}, {"$set": user_info})
                    
                    session_state["user_info"] = user_info
                    st.success("Information submitted successfully!")
                    
                    st.markdown("### Medical Report:")
                    st.write(report)
                    server.sendmail(MAIL_ID, RECEIVER1, report)
                    server.sendmail(MAIL_ID, RECEIVER2, report)
                    st.success("E-mail alert sent successfully")
            
        else:
            st.warning("Please login/signup to upload a retina image.")

    elif page == "View Reports":
        if session_state.get("logged_in"):
            st.title("View Reports")
            user_info = session_state["user_info"]
            if user_info is not None:
                if user_info["report"] is not None:
                    st.subheader("Medical Report:")
                    st.write(user_info["report"])
                else:
                    st.warning("No reports available.")
            else:
                st.warning("User information not found.")
        else:
            st.warning("Please login/signup to view reports.")


if __name__ == "__main__":
    initialize_database()
    main()
