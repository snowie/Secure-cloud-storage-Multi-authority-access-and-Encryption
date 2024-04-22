import json
import os
import streamlit as st
from streamlit import session_state
import streamlit as st
import google.generativeai as genai
from st_audiorec import st_audiorec
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from time import sleep
import smtplib
import random
import string
import re
import pypdfium2 as pdfium
import datetime
import os
import json
from PIL import Image
import os
import numpy as np
import streamlit as st
from streamlit import session_state
import streamlit as st
from pytube import YouTube
import whisper
import os
import hashlib

st.set_page_config(
    page_title="Smart Examination Portal",
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)
from bs4 import BeautifulSoup
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
from pytube import YouTube
from deep_translator import GoogleTranslator
from gtts import gTTS
from string import punctuation
from heapq import nlargest
import os
import json
from bs4 import BeautifulSoup
import requests
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_sm
import io
from gtts import gTTS
import datetime
from googlesearch import search

session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0

load_dotenv()


safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


def generate_search_terms(Highlights):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        prompt = (
            """
As a smart teaching assistant, your task is to generate relevant search terms based on the provided highlights for the previous teaching sessions. You should identify the key topics discussed during the session and generate search terms that can be used to find more information on those topics. Do not mention that you are an AI assistant.

Your responsibilities also include:
- Identifying the main topics discussed in the class.
- Generating search terms based on those topics.
- Search term should be in the form of a list separated by newline python characters ordered from most to least relevant topics.
- Format: 
search term 1
search term 2
search term 3
..
- Do not add anythig else in the response."""
            + Highlights
        )
        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo-0125",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def smart_assistant_query(email, query):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        Highlights = []
        with open("data.json", "r") as json_file:
            user_data = json.load(json_file)
            for user in user_data["students"]:
                if user["email"] == email:
                    if user["highlights"] is None or len(user["highlights"]) == 0:
                        return "No previous MoMs found for the user."
                    Highlights = user["highlights"]
                    break

        prompt = f"""
As a smart teaching assistant, your task is to answer the user's queries based on the provided data. The provided data is of highlights of the previous teaching sessions. You should be able to give all the insights possible only from the given data. You should provide detailed responses to the user's questions without revealing that you are an AI assistant. You should also be able to answer follow-up questions and provide additional information as needed. If the user asks for more information, you should be able to provide it. You should also be able to answer any questions that the user may have about the data.

Your responsibilities also include:
- Identifying useful insights from the provided data.
- Answering queries based on the information in the data.
- Providing additional information or answering questions from the user.
- Conducting internet searches to gather relevant results if needed. + Query: {query}

Previous Teaching session (Provided data):
""" + str(
            Highlights
        )
        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            # model="gpt-3.5-turbo",
            model="gpt-3.5-turbo-0125",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def smart_teaching_assistant(session_transcription):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        prompt = (
            """
As a smart teaching assistant, your task is to generate detailed class session highlights based on the provided session transcription. Additionally, you are responsible for conducting relevant internet research to supplement the teaching with necessary information. This includes details about discussed topics such as Homework, Assignments, Projects,Food for thoughts, Higher Order thinking questions, and other important information. You should provide a detailed summary of the session and highlight key takeaways without revealing that you are an AI assistant.
Your responsibilities also include:
- Identifying the main topics discussed in the class.
- Executing possible insights from the provided data.
- Providing additional information or answering questions from the user.
- Conducting internet searches to gather relevant results if the meeting involves gathering information on a specific topic.

Session Transcription:
"""
            + session_transcription
        )

        prompt += session_transcription
        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            # model="gpt-3.5-turbo",
            model="gpt-3.5-turbo-0125",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def transcribe_audio_from_data(file_data):
    with st.spinner("Transcribing audio..."):
        with open("temp.mp3", "wb") as f:
            f.write(file_data)
        model = whisper.load_model("base")
        result = model.transcribe("temp.mp3")
        os.remove("temp.mp3")
        return result["text"]


def get_summary(text_content, percent):
    nlp = en_core_web_sm.load()
    stop_words = list(STOP_WORDS)
    punctuation_items = punctuation + "\n"
    nlp = spacy.load("en_core_web_sm")

    nlp_object = nlp(text_content)
    word_frequencies = {}
    for word in nlp_object:
        if word.text.lower() not in stop_words:
            if word.text.lower() not in punctuation_items:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    sentence_token = [sentence for sentence in nlp_object.sents]
    sentence_scores = {}
    for sent in sentence_token:
        sentence = sent.text.split(" ")
        for word in sentence:
            if word.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.lower()]

    select_length = int(len(sentence_token) * (int(percent) / 100))
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = " ".join(final_summary)
    return summary


def get_transcript_from_url(url):
    try:
        url_data = urlparse(url)
        id = url_data.query[2::]
        script = YouTubeTranscriptApi.get_transcript(id)
        transcript = ""
        for text in script:
            t = text["text"]
            if t != "[Music]":
                transcript += t + " "
        return transcript
    except:
        try:
            try:
                yt = YouTube(url)
            except:
                return "Connection Error"

            stream = yt.streams.get_by_itag(251)
            stream.download("", "temp.webm")
            model = whisper.load_model("base")
            result = model.transcribe("temp.webm")
            if os.path.exists("temp.webm"):
                os.remove("temp.webm")
            return result["text"]
        except Exception as e:
            return f"Error in fetching transcript {e}"


def get_transcript_from_video():
    try:
        model = whisper.load_model("base")
        result = model.transcribe("temp.mp4")
        return result["text"]
    except Exception as e:
        return f"Error in fetching transcript {e}"


def translate(summary, language):
    try:
        summaries = []
        while len(summary) > 5000:
            index = 5000
            while summary[index] != "." and index > 0:
                index -= 1
            if index == 0:
                index = 5000
            summaries.append(summary[:index])
            summary = summary[index:]
        summaries.append(summary)
        translated_summary = ""
        for s in summaries:
            translated_summary += (
                GoogleTranslator(source="auto", target=language).translate(s) + " "
            )
    except Exception:
        st.warning(f"Translation to the selected language is not supported.")
        translated_summary = summary
    return translated_summary


def summarize(transcript, length, language, option):
    if option == "Get Transcription":
        summary = transcript
    else:
        summary = get_summary(transcript, int(length[:2]))
    if language == "en":
        return summary
    try:
        summaries = []
        while len(summary) > 5000:
            index = 5000
            while summary[index] != "." and index > 0:
                index -= 1
            if index == 0:
                index = 5000
            summaries.append(summary[:index])
            summary = summary[index:]
        summaries.append(summary)
        translated_summary = ""
        for s in summaries:
            translated_summary += (
                GoogleTranslator(source="auto", target=language).translate(s) + " "
            )
    except:
        st.warning(f"Translation to the selected language is not supported.")
        translated_summary = summary
    return translated_summary


def get_text_from_image(image, API):
    try:
        genai.configure(api_key=os.getenv(API))
        try:
            image = Image.open(image)
        except:
            pass
        model = genai.GenerativeModel("gemini-pro-vision")
        response = model.generate_content(
            [
                "Please analyze the handwritten text in the provided image and provide the corresponding text.",
                image,
            ],
            safety_settings=safety_settings,
        )
        return response.text
    except Exception as e:
        st.error(f"Error getting text from image: {e}")
        return None


def get_text_from_pdf(pdf_file, APIS):
    try:
        pdf = pdfium.PdfDocument(pdf_file)
        student_answer = ""
        for i in range(len(pdf)):
            page = pdf[i]
            API = APIS[i % len(APIS)]
            image = page.render(scale=4).to_pil()
            student_answer += get_text_from_image(image, API)
        return student_answer
    except Exception as e:
        st.error(f"Error getting text from pdf: {e}")
        return None


def get_marks(question, answer_key, student_answer, total_marks):
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        prompt = f"""Question: {question}\n\nAnswer Key: {answer_key}\n\nStudent Answer: {student_answer}\n\nTotal Marks: {total_marks}\n\nPlease read the question and the answer key provided below to understand the context. Then, evaluate the student's answer based on the answer key and allocate marks accordingly from the total marks given. Provide the marks obtained by the student for the question as an integer value and justify the marks awarded.\n\nThe marks and justification should be formatted as follows:\n\n"marks": <integer_value>,\n"justification": <reason_for_marks>\n"""
        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo-0125",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def evaluate(question, answer_key, student_answer):
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        prompt = f"""Question: {question}\n\nAnswer Key: {answer_key}\n\nStudent Answer: {student_answer}\n\nEvaluate the student's response based on the provided answer key. Your evaluation should be detailed and constructive, offering feedback to help the student improve. Please refrain from using headings in your response."""
        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo-0125",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def user_exists(email, json_file_path):
    # Function to check if user with the given email exists
    with open(json_file_path, "r") as file:
        users = json.load(file)
        for user in users["students"]:
            if user["email"] == email:
                return True
    return False


def send_verification_code(email, code):
    SENDER_MAIL_ID = os.getenv("SENDER_MAIL_ID")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    RECEIVER = email
    server = smtplib.SMTP_SSL("smtp.googlemail.com", 465)
    server.login(SENDER_MAIL_ID, APP_PASSWORD)
    message = f"Subject: Your Verification Code\n\nYour verification code is: {code}"
    server.sendmail(SENDER_MAIL_ID, RECEIVER, message)
    server.quit()
    st.success("Email sent successfully!")
    return True


def generate_verification_code(length=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def signup(json_file_path="students.json"):
    st.title("Student Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")
        if (
            session_state.get("verification_code") is None
            or session_state.get("verification_time") is None
            or datetime.datetime.now() - session_state.get("verification_time")
            > datetime.timedelta(minutes=5)
        ):
            verification_code = generate_verification_code()
            session_state["verification_code"] = verification_code
            session_state["verification_time"] = datetime.datetime.now()
        if st.form_submit_button("Signup"):
            if not name:
                st.error("Name field cannot be empty.")
            elif not email:
                st.error("Email field cannot be empty.")
            elif not re.match(r"^[\w\.-]+@[\w\.-]+$", email):
                st.error("Invalid email format. Please enter a valid email address.")
            elif user_exists(email, json_file_path):
                st.error(
                    "User with this email already exists. Please choose a different email."
                )
            elif not age:
                st.error("Age field cannot be empty.")
            elif not password or len(password) < 6:  # Minimum password length of 6
                st.error("Password must be at least 6 characters long.")
            elif password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            else:
                verification_code = session_state["verification_code"]
                send_verification_code(email, verification_code)
                entered_code = st.text_input(
                    "Enter the verification code sent to your email:"
                )
                if entered_code == verification_code:
                    user = create_account(
                        name, email, age, sex, password, json_file_path
                    )
                    session_state["logged_in"] = True
                    session_state["user_info"] = user
                    st.success("Signup successful. You are now logged in!")
                elif len(entered_code) == 6 and entered_code != verification_code:
                    st.error("Incorrect verification code. Please try again.")


def check_login(username, password, json_file_path="evaluator.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["students"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                return user
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(
    json_file_path="students.json", question_paper="question_paper.json"
):
    try:
        if not os.path.exists(json_file_path):
            data = {"students": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
        if not os.path.exists(question_paper):
            data = {"subjects": []}
            with open(question_paper, "w") as json_file:
                json.dump(data, json_file)
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(name, email, age, sex, password, json_file_path="students.json"):
    try:
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"students": []}
        else:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

        # Append new user data to the JSON structure
        email = email.lower()
        password = hashlib.md5(password.encode()).hexdigest()
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
            "exams": None,
            "highlights": None,
        }

        data["students"].append(user_info)

        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="evaluator.json", question_paper="question_paper.json"):
    st.title("Login Page")
    username = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    username = username.lower()
    password = hashlib.md5(password.encode()).hexdigest()

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password, json_file_path)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def get_user_info(email, json_file_path="evaluator.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["students"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None


def render_dashboard(user_info, json_file_path="evaluator.json"):
    try:
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("Student Information")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def main(json_file_path="students.json", question_paper="question_paper.json"):
    st.header("Welcome to the Student's Dashboard!")
    page = st.sidebar.radio(
        "Go to",
        (
            "Signup/Login",
            "Dashboard",
            "Attempt Exam",
            "View Previous Exams",
            "Student Learning Hub",
            "View Previous Lectures",
        ),
        key="page",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"])
        else:
            st.warning("Please login/signup to view the dashboard.")

    elif page == "Attempt Exam":
        if session_state.get("logged_in"):
            user_info = session_state["user_info"]
            APIS = ["GOOGLE_API_KEY_1", "GOOGLE_API_KEY_2", "GOOGLE_API_KEY_3"]
            st.title("Attempt Exam")
            user_info = session_state["user_info"]
            with open("question_paper.json", "r") as question_data_json_file:
                question_data = json.load(question_data_json_file)
            codes = [
                subject["Subject_name"] + " - " + subject["Subject_code"]
                for subject in question_data["subjects"]
            ]
            codes.insert(0, "--Select--")
            subject_code = st.selectbox(
                "Select a subject code to attempt the exam:", codes
            )
            if subject_code != "--Select--":
                subject_code = subject_code.split(" - ")[1]
                subject_code_ = next(
                    (
                        i
                        for i, subject in enumerate(question_data["subjects"])
                        if subject["Subject_code"] == subject_code
                    ),
                    None,
                )
                if subject_code_ is not None:
                    # upload or type the answer
                    option = st.radio(
                        "Select an option", ("Upload Answer", "Type Answer")
                    )
                    if option == "Upload Answer":
                        st.write("Upload your answer for the questions below:")
                    else:
                        st.write("Type your answer for the questions below:")
                    exam = question_data["subjects"][subject_code_]
                    questions = exam["questions"]
                    st.write(f"Subject: {exam['Subject_name']}")
                    st.write(f"Subject Code: {exam['Subject_code']}")
                    number_of_questions = len(questions)
                    question_details = []
                    with st.form("exam_form"):
                        for i in range(number_of_questions):
                            st.write(f"Question {i+1}: {questions[i]['question']}")
                            if option == "Type Answer":
                                answer = st.text_area(
                                    f"Type your answer for Question {i+1}:"
                                )
                            else:
                                answer = st.file_uploader(
                                    f"Upload your answer for Question {i+1}:",
                                    type=["pdf", "png", "jpg", "jpeg"],
                                )
                            question_details.append(
                                {
                                    "question": questions[i]["question"],
                                    "answer": answer,
                                    "answer_key": questions[i]["answer"],
                                    "total_marks": questions[i]["marks"],
                                }
                            )
                        if st.form_submit_button("Submit Exam"):
                            with st.spinner("Evaluating your answers..."):
                                final_details = {
                                    "Subject_name": exam["Subject_name"],
                                    "Subject_code": exam["Subject_code"],
                                    "Number_of_questions": number_of_questions,
                                    "questions": [],
                                }
                                for response in question_details:
                                    question = response["question"]
                                    answer_key = response["answer_key"]
                                    if option == "Upload Answer":
                                        student_answer = ""
                                        if answer is not None:
                                            if answer.type == "application/pdf":
                                                with open(
                                                    "student_answer.pdf", "wb"
                                                ) as file:
                                                    file.write(answer.read())
                                                student_answer = get_text_from_pdf(
                                                    "student_answer.pdf", APIS
                                                )
                                                if os.path.exists("student_answer.pdf"):
                                                    os.remove("student_answer.pdf")
                                            else:
                                                student_answer = get_text_from_image(
                                                    answer, random.choice(APIS)
                                                )
                                    else:
                                        student_answer = response["answer"]
                                    total_marks = response["total_marks"]
                                    evaluation = evaluate(
                                        question, answer_key, student_answer
                                    )
                                    result = get_marks(
                                        question, answer_key, student_answer, total_marks
                                    )
                                    marks_index = result.find('"marks":') + len('"marks":')
                                    marks = int(
                                        result[marks_index : result.find(",", marks_index)]
                                    )
                                    justification_index = result.find(
                                        '"justification":'
                                    ) + len('"justification":')
                                    justification = result[justification_index:]
                                    response["marks"] = marks
                                    final_details["questions"].append(
                                        {
                                            "question": question,
                                            "answer": student_answer,
                                            "answer_key": answer_key,
                                            "total_marks": total_marks,
                                            "evaluation": evaluation,
                                            "marks": marks,
                                            "justification": justification,
                                        }
                                    )

                            with open("students.json", "r+") as json_file_student:
                                student_data = json.load(json_file_student)
                                student_email = next(
                                    (
                                        i
                                        for i, student in enumerate(
                                            student_data["students"]
                                        )
                                        if student["email"] == user_info["email"]
                                    ),
                                    None,
                                )
                                if student_email is not None:
                                    if (
                                        student_data["students"][student_email]["exams"]
                                        is None
                                    ):
                                        student_data["students"][student_email][
                                            "exams"
                                        ] = []
                                    student_data["students"][student_email][
                                        "exams"
                                    ].append(final_details)
                                    json_file_student.seek(0)
                                    json.dump(student_data, json_file_student, indent=4)
                                    json_file_student.truncate()
                                    st.success("Exam submitted successfully!")

                            # show total marks
                            obtained_marks = sum(
                                [
                                    question["marks"]
                                    for question in final_details["questions"]
                                ]
                            )
                            total_marks = sum(
                                [
                                    question["total_marks"]
                                    for question in final_details["questions"]
                                ]
                            )
                            st.markdown(
                                f"Total Marks Obtained: {obtained_marks}/{total_marks}"
                            )
                else:
                    st.error("Invalid subject code. Please try again.")

    elif page == "View Previous Exams":
        if session_state.get("logged_in"):
            st.title("View Previous Exams")
            with open("students.json", "r") as json_file:
                data = json.load(json_file)
                student_index = next(
                    (
                        i
                        for i, student in enumerate(data["students"])
                        if student["email"] == session_state["user_info"]["email"]
                    ),
                    None,
                )
                if student_index is not None:
                    exams = data["students"][student_index]["exams"]
                    if exams:
                        for exam in exams:
                            st.subheader(f"Subject: {exam['Subject_name']}")
                            st.markdown(f"**Subject Code:** {exam['Subject_code']}")
                            st.markdown(
                                f"**Number of Questions:** {exam['Number_of_questions']}"
                            )
                            st.markdown("---")
                            for i in range(exam["Number_of_questions"]):
                                
                                st.markdown(f"#### Question {i+1}:")
                                st.markdown(
                                    f"{exam['questions'][i]['question']}"
                                )
                                st.markdown(f"#### Answer:")
                                st.markdown(
                                    f"{exam['questions'][i]['answer']}"
                                )
                                st.markdown(f"#### Answer Key:")
                                st.markdown(
                                    f"{exam['questions'][i]['answer_key']}"
                                )
                                st.markdown(f"#### Evaluation:")
                                st.markdown(
                                    f"{exam['questions'][i]['evaluation']}"
                                )
                                st.markdown(f"#### Marks:")
                                st.markdown(
                                    f"{exam['questions'][i]['marks']}"
                                )
                                st.markdown(f"#### Justification:")
                                st.markdown(
                                    f"{exam['questions'][i]['justification']}"
                                )
                                
                                st.markdown("---")
                            st.markdown("---")
                    else:
                        st.error("No exams found. Please attempt an exam.")
                else:
                    st.error("No exams found. Please attempt an exam.")


    elif page == "Student Learning Hub":
        
        if session_state.get("logged_in"):
            APIS = ["GOOGLE_API_KEY_1", "GOOGLE_API_KEY_2", "GOOGLE_API_KEY_3"]
            user_info = session_state["user_info"]
            st.title("Student Learning Hub")
            st.write("Welcome to the Student Learning Hub.")
            st.write(
                "Here you can upload various types of media to enhance your learning experience."
            )
            media_format = st.selectbox(
                "Select a type of media to upload:",
                (
                    "Video",
                    "YouTube URL",
                    "PDF Document",
                    "Audio Recording",
                    "Image",
                    "Text",
                ),
            )
            option_ = st.radio(
                "Choose an option:", ("Get Transcription", "Get Summary")
            )
            button_name = ""
            type_name = ""
            transcription = None
            highlights = None
            result = None
            transcription_translated = None
            summary_translated = None
            highlights_translated = None
            if option_ == "Get Transcription":
                button_name = "Get Transcription"
                type_name = "Transcription"
                length = "100%"
            else:
                button_name = "Get Summary"
                type_name = "Summary"
                length = st.select_slider(
                    "Specify length of Summary",
                    options=[
                        "10%",
                        "20%",
                        "30%",
                        "40%",
                        "50%",
                        "60%",
                        "70%",
                        "80%",
                        "90%",
                    ],
                )
            languages = {
                "English": "en",
                "Afrikaans": "af",
                "Albanian": "sq",
                "Amharic": "am",
                "Arabic": "ar",
                "Armenian": "hy",
                "Azerbaijani": "az",
                "Basque": "eu",
                "Belarusian": "be",
                "Bengali": "bn",
                "Bosnian": "bs",
                "Bulgarian": "bg",
                "Catalan": "ca",
                "Cebuano": "ceb",
                "Chichewa": "ny",
                "Chinese (simplified)": "zh-cn",
                "Chinese (traditional)": "zh-tw",
                "Corsican": "co",
                "Croatian": "hr",
                "Czech": "cs",
                "Danish": "da",
                "Dutch": "nl",
                "Esperanto": "eo",
                "Estonian": "et",
                "Filipino": "tl",
                "Finnish": "fi",
                "French": "fr",
                "Frisian": "fy",
                "Galician": "gl",
                "Georgian": "ka",
                "German": "de",
                "Greek": "el",
                "Gujarati": "gu",
                "Haitian creole": "ht",
                "Hausa": "ha",
                "Hawaiian": "haw",
                "Hebrew": "he",
                "Hindi": "hi",
                "Hmong": "hmn",
                "Hungarian": "hu",
                "Icelandic": "is",
                "Igbo": "ig",
                "Indonesian": "id",
                "Irish": "ga",
                "Italian": "it",
                "Japanese": "ja",
                "Javanese": "jw",
                "Kannada": "kn",
                "Kazakh": "kk",
                "Khmer": "km",
                "Korean": "ko",
                "Kurdish (kurmanji)": "ku",
                "Kyrgyz": "ky",
                "Lao": "lo",
                "Latin": "la",
                "Latvian": "lv",
                "Lithuanian": "lt",
                "Luxembourgish": "lb",
                "Macedonian": "mk",
                "Malagasy": "mg",
                "Malay": "ms",
                "Malayalam": "ml",
                "Maltese": "mt",
                "Maori": "mi",
                "Marathi": "mr",
                "Mongolian": "mn",
                "Myanmar (burmese)": "my",
                "Nepali": "ne",
                "Norwegian": "no",
                "Odia": "or",
                "Pashto": "ps",
                "Persian": "fa",
                "Polish": "pl",
                "Portuguese": "pt",
                "Punjabi": "pa",
                "Romanian": "ro",
                "Russian": "ru",
                "Samoan": "sm",
                "Scots gaelic": "gd",
                "Serbian": "sr",
                "Sesotho": "st",
                "Shona": "sn",
                "Sindhi": "sd",
                "Sinhala": "si",
                "Slovak": "sk",
                "Slovenian": "sl",
                "Somali": "so",
                "Spanish": "es",
                "Sundanese": "su",
                "Swahili": "sw",
                "Swedish": "sv",
                "Tajik": "tg",
                "Tamil": "ta",
                "Telugu": "te",
                "Thai": "th",
                "Turkish": "tr",
                "Ukrainian": "uk",
                "Urdu": "ur",
                "Uyghur": "ug",
                "Uzbek": "uz",
                "Vietnamese": "vi",
                "Welsh": "cy",
                "Xhosa": "xh",
                "Yiddish": "yi",
                "Yoruba": "yo",
                "Zulu": "zu",
            }

            language = st.selectbox(
                "Select Language",
                (
                    "English",
                    "Hindi",
                    "Afrikaans",
                    "Albanian",
                    "Amharic",
                    "Arabic",
                    "Armenian",
                    "Azerbaijani",
                    "Basque",
                    "Belarusian",
                    "Bengali",
                    "Bosnian",
                    "Bulgarian",
                    "Catalan",
                    "Cebuano",
                    "Chichewa",
                    "Chinese (simplified)",
                    "Chinese (traditional)",
                    "Corsican",
                    "Croatian",
                    "Czech",
                    "Danish",
                    "Dutch",
                    "Esperanto",
                    "Estonian",
                    "Filipino",
                    "Finnish",
                    "French",
                    "Frisian",
                    "Galician",
                    "Georgian",
                    "German",
                    "Greek",
                    "Gujarati",
                    "Haitian creole",
                    "Hausa",
                    "Hawaiian",
                    "Hebrew",
                    "Hmong",
                    "Hungarian",
                    "Icelandic",
                    "Igbo",
                    "Indonesian",
                    "Irish",
                    "Italian",
                    "Japanese",
                    "Javanese",
                    "Kannada",
                    "Kazakh",
                    "Khmer",
                    "Korean",
                    "Kurdish (kurmanji)",
                    "Kyrgyz",
                    "Lao",
                    "Latin",
                    "Latvian",
                    "Lithuanian",
                    "Luxembourgish",
                    "Macedonian",
                    "Malagasy",
                    "Malay",
                    "Malayalam",
                    "Maltese",
                    "Maori",
                    "Marathi",
                    "Mongolian",
                    "Myanmar (burmese)",
                    "Nepali",
                    "Norwegian",
                    "Odia",
                    "Pashto",
                    "Persian",
                    "Polish",
                    "Portuguese",
                    "Punjabi",
                    "Romanian",
                    "Russian",
                    "Samoan",
                    "Scots gaelic",
                    "Serbian",
                    "Sesotho",
                    "Shona",
                    "Sindhi",
                    "Sinhala",
                    "Slovak",
                    "Slovenian",
                    "Somali",
                    "Spanish",
                    "Sundanese",
                    "Swahili",
                    "Swedish",
                    "Tajik",
                    "Tamil",
                    "Telugu",
                    "Thai",
                    "Turkish",
                    "Ukrainian",
                    "Urdu",
                    "Uyghur",
                    "Uzbek",
                    "Vietnamese",
                    "Welsh",
                    "Xhosa",
                    "Yiddish",
                    "Yoruba",
                    "Zulu",
                ),
            )
            if media_format == "Video":
                video = st.file_uploader(
                    "Upload Video", type=["mp4", "avi", "mov", "wmv"]
                )
                if video is not None:
                    # save the video file
                    with open("temp.mp4", "wb") as f:
                        f.write(video.read())
                    with st.spinner("Transcribing video..."):
                        transcription = get_transcript_from_video()
                    if os.path.exists("temp.mp4"):
                        os.remove("temp.mp4")

            elif media_format == "YouTube URL":
                youtube_url = st.text_input("Enter YouTube URL:")
                if youtube_url:
                    st.markdown(
                        '<h1 style="color:#FF0000;">YouTube Video Summariser</h1>',
                        unsafe_allow_html=True,
                    )
                    # Fetch video title from YouTube link
                    r = requests.get(youtube_url)
                    soup = BeautifulSoup(r.text, "html.parser")
                    title = soup.title.string if soup.title else "No title available"

                    # Display video title
                    st.info(f"Video Title: {title}")

                    st.video(youtube_url)
                    with st.spinner("Transcribing YouTube video..."):
                        transcription = get_transcript_from_url(youtube_url)

            elif media_format == "PDF Document":
                pdf_file = st.file_uploader("Upload PDF Document", type=["pdf"])
                if pdf_file is not None:
                    transcription = get_text_from_pdf(pdf_file, APIS)

            elif media_format == "Audio Recording":
                record_or_upload = st.radio(
                    "Select an option", ("Record Audio", "Upload Audio")
                )
                if record_or_upload == "Record Audio":
                    st.write("Click the button below to start recording:")
                    audio = st_audiorec()
                    if audio is not None:
                        transcription = transcribe_audio_from_data(audio)
                else:
                    audio = st.file_uploader("Upload Audio", type=["mp3", "wav"])
                    if audio is not None:
                        transcription = transcribe_audio_from_data(audio.read())

            elif media_format == "Image":
                image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
                if image is not None:
                    with st.spinner("Extracting text from image..."):
                        transcription = get_text_from_image(image, random.choice(APIS))

            elif media_format == "Text":
                transcription = ""
                transcription = st.text_area("Enter Text:")

            if transcription is not None:
                st.markdown(f"### Transcription: \n")
                if language != "English":
                    with st.spinner("Translating transcription..."):
                        transcription_translated = translate(
                        transcription, languages[language]
                    )
                else:
                    transcription_translated = transcription
                st.markdown(f"{transcription_translated}")
                if option_ == "Get Summary":
                    with st.spinner("Summarizing transcription..."):
                        result = summarize(
                            transcription, length, languages[language], option_
                        )
                        if result is not None:
                            st.markdown(f"### {type_name}:")
                            st.markdown(f"{result}")
                        else:
                            st.error("Error getting summary.")
                with st.spinner("Generating highlights..."):
                    highlights = smart_teaching_assistant(transcription)
                st.subheader("Session Highlights and Takeaways:")
                if language != "English":
                    highlights_translated = translate(highlights, languages[language])
                else:
                    highlights_translated = highlights
                st.write(highlights_translated)
                with open(json_file_path, "r+") as json_file:
                    data = json.load(json_file)
                    for user in data["students"]:
                        if user["email"] == user_info["email"]:
                            if user["highlights"] is None:
                                user["highlights"] = [
                                    {
                                        "Timestamp": datetime.datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        ),
                                        "Transcription": transcription_translated,
                                        "Summary": result,
                                        "Highlight": highlights_translated,
                                    }
                                ]
                            else:
                                user["highlights"].append(
                                    {
                                        "Timestamp": datetime.datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        ),
                                        "Transcription": transcription_translated,
                                        "Summary": result,
                                        "Highlight": highlights_translated,
                                    }
                                )
                            json_file.seek(0)
                            json.dump(data, json_file, indent=4)
                            json_file.truncate()

            if highlights and transcription:
                with st.spinner("Generating search terms..."):
                    search_terms = generate_search_terms(highlights).split("\n")
                    search_terms = search_terms[: (min(3, len(search_terms)))]
                st.subheader("Suggested links for further reading:")
                for search_term in search_terms:
                    searches = search(search_term, num_results=2)
                    for search_ in searches:
                        st.write(search_)
                with st.spinner("Generating audio highlights..."):
                    speech = gTTS(text=highlights, lang="en", slow=False)
                    speech.save("user_trans.mp3")
                    st.success("###  \U0001F3A7 Hear the Highlights")
                audio_file = open("user_trans.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/ogg", start_time=0)
                audio_file.close()
                if os.path.exists("user_trans.mp3"):
                    os.remove("user_trans.mp3")

                # add transcription, summary and highlights download buttons

                if transcription is None:
                    transcription = ""
                if result is None:
                    result = ""
                if highlights is None:
                    highlights = ""
                data = f"""
                    Transcription:\n {transcription_translated}\n\n
                    Summary:\n {result}\n\n
                    Highlights and key takeaways:\n {highlights_translated}
                
                """

                download_button_str = f"Download Highlights and Takeaways"
                with io.BytesIO(data.encode()) as stream:
                    st.download_button(
                        download_button_str, stream, file_name="highlights.txt"
                    )

        else:
            st.warning("Please login/signup to access this page.")

    elif page == "View Previous Lectures":
        if session_state.get("logged_in"):
            user_info = session_state["user_info"]
            st.title("View Previous Lectures")
            st.write("Welcome to the View Previous Lectures page.")
            st.write("Here you can access previous lectures.")
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)
                for user in data["students"]:
                    if user["email"] == user_info["email"]:
                        user_info = user
                        break
            if user_info["highlights"] is not None:
                st.header("Previous highlights:")
                for highlight in user_info["highlights"]:
                    st.markdown(f"## {highlight['Timestamp']}")
                    if highlight["Transcription"]:
                        st.markdown(f"### Transcription:")
                        st.markdown(f"{highlight['Transcription']}")
                        # st.markdown(f"**Transcription:** {highlight['Transcription']}")
                    if highlight["Summary"]:
                        st.markdown(f"### Summary:")
                        st.markdown(f"{highlight['Summary']}")
                    st.markdown(f"### Highlights:")
                    st.write(highlight["Highlight"])
                    st.write("---")
                    st.write("---")
            else:
                st.warning("You do not have any previous Sessions.")

        else:
            st.warning("Please login/signup to access this page.")
    else:
        st.warning("Please login/signup to access this page.")


if __name__ == "__main__":

    initialize_database()
    main()
