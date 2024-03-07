from time import sleep
import streamlit as st
import fitz  
from datetime import datetime, timedelta
from prompts import *


if 'medical_info_text' not in st.session_state:
    st.session_state['medical_info_text'] = ''
if 'health_issue' not in st.session_state:
    st.session_state['health_issue'] = ''
if 'departure_from' not in st.session_state:
    st.session_state['departure_from'] = ''
if 'departure_date' not in st.session_state:
    st.session_state['departure_date'] = None
if 'arrival_date' not in st.session_state:
    st.session_state['arrival_date'] = None
if 'people_accompanying' not in st.session_state:
    st.session_state['people_accompanying'] = 1
if 'hotel_needed' not in st.session_state:
    st.session_state['hotel_needed'] = False
if 'hotel_dates' not in st.session_state:
    st.session_state['hotel_dates'] = {'departure_date': None, 'arrival_date': None}
if 'accommodation_preference' not in st.session_state:
    st.session_state['accommodation_preference'] = ''
if 'transfers_needed' not in st.session_state:
    st.session_state['transfers_needed'] = False
if 'dietary_restrictions' not in st.session_state:
    st.session_state['dietary_restrictions'] = ''
if 'food_budget' not in st.session_state:
    st.session_state['food_budget'] = 0
if 'activities_post_recovery' not in st.session_state:
    st.session_state['activities_post_recovery'] = False
if 'city' not in st.session_state:
    st.session_state['city'] = ''

st.set_page_config(layout="wide")

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import pandas as pd


load_dotenv()

#google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai_api_key=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


def get_meta_data_from_desc(description):
    message = f'''
    You must extract the necessary data and output it as a json format always. You must also create Here's the sample format: 
    The food_search_term_google is the search term that will be used to search for food options in the area. Based on the medical conditions generate a relevant search term. Do not get too niche otherwise it will end up in less results.
    {
    "medical condition":"add medical condition",
    "treatment period":"",
    "food_search_term_google":""
    }

    Here's the description:
    {description}
    '''

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": message},
        {"role": "user", "content": "JOint Fracture"}
    ],
    response_format = { "type": "json_object" }
    )

    print(completion.choices[0].message)
    op = json.loads(completion.choices[0].message.content)
    return op


def generate_search_term_food(medical_condition, city):
    message = f'''
    You must create a google search term to find relevant restaurants based on the dietary restrictions and the patient's treatment. Output it as a json format always. Here's the sample format: 
    {
    "search_term":"Healthy restaurants for heart patients in riyadh",
    }
    '''

    user_pr = f'''
    Here's the medical condition :{medical_condition}
    Here's the city :{city}
    '''

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": message},
        {"role": "user", "content": f"{user_pr}"}
    ],
    response_format = { "type": "json_object" }
    )

    print(completion.choices[0].message)
    op = json.loads(completion.choices[0].message.content)
    return op


def generate_search_term_hospital(medical_condition):

    message_ = f'''
    You must extract the necessary data and output it as a json format always.Always append saudi Arabia as this is meant for KSA. Here's the sample format: 
    Give short queries, that are effective.
    {{
    "search_term":"hospitals for treatment osteoporosis in Saudi Arabia"
    }}
    '''

    user_pr = f'''
    Here's the medical condition :{medical_condition}
    '''

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": message_},
        {"role": "user", "content": f"{user_pr}"}
    ],
    response_format = { "type": "json_object" }
    )

    print(completion.choices[0].message)
    op = json.loads(completion.choices[0].message.content)
    return op


def get_hospital_names(medical_condition):
    import requests

    search_term = generate_search_term_hospital(medical_condition)
    print(search_term)
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_term}&key={google_maps_api_key}&reviews=most_relevant"
    response = requests.request("GET", url)

    data_hosp = response.json()

    df_main = pd.json_normalize(data_hosp['results'], sep='_')

    df_main_sorted = df_main.sort_values(by="rating", ascending=False)
    #df_main_sorted.head()

    df_main_sorted
    return df_main_sorted

def get_restaurant_names(medical_condition, city):
    import requests

    search_term = generate_search_term_food(medical_condition, city)
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_term}&key={google_maps_api_key}&reviews=most_relevant"
    response = requests.request("GET", url)

    data_hosp = response.json()

    df_main = pd.json_normalize(data_hosp['results'], sep='_')

    df_main_sorted = df_main.sort_values(by="rating", ascending=False)
    df_main_sorted.head()

    df_main_sorted
    return df_main_sorted


def get_restaurant_names(medical_condition, city):
    import requests

    search_term = generate_search_term_food(medical_condition, city)
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_term}&key={google_maps_api_key}&reviews=most_relevant"
    response = requests.request("GET", url)

    data_hosp = response.json()

    df_main = pd.json_normalize(data_hosp['results'], sep='_')

    df_main_sorted = df_main.sort_values(by=["rating","user_ratings_total"], ascending=False)
    df_main_sorted.head()

    df_main_sorted
    return df_main_sorted

def extract_city_from_address(address):
    message = '''
        You must extract the city and output it as a json format always. Here's the sample format: 
        {
        "city":"Riyadh",
        }
        '''

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": message},
        {"role": "user", "content": f"{address}"}
    ],
    response_format = { "type": "json_object" }
    )

    print(completion.choices[0].message)
    op = json.loads(completion.choices[0].message.content)
    return op



def main():
    st.title("MarhamRoute - Your Medical Travel Companion")
    st.write("MarhamRoute is a one-stop platform to help you find and plan your medical travel needs within Saudi Arabia. Whether you are looking for a specific medical specialty or a preferred destination, we have you covered.")

    with st.expander("Visa Information"):
        st.write("You may need a visa to travel to Saudi Arabia for medical treatment. Please check the visa requirements for your country of residence and apply for a visa if necessary.")
        visa_link = "https://www.my.gov.sa/wps/portal/snp/servicesDirectory/servicedetails/7363/!ut/p/z1/jY_BCoJAFEW_pQ-Q957jqC0nA2nIphg0m03MRhNKRaRFX9_QTqTs7h6cw7sXDJRgWvtsajs2XWvv7r6Y8CqPcUACScVEIZ6Sdbw9kGSYIpyngGJ844AsUkIXhMjB_OPjlwhc8uUS4Bb4Q5ZkNZjejjevaasOyoiFzP02U1ulMnA25T6XBWLAZ8B83gf40V_bAfpHXr72ld55YvUGTTMe5w!!/dz/d5/L0lHSkovd0RNQU5rQUVnQSEhLzROVkUvZW4!/"
        
        st.markdown(f"""<a href="{visa_link}" target="_blank"><button>Apply for Medical Treatment Visa</button></a>""", unsafe_allow_html=True)

    st.header("Tell us about your needs")

    st.header("Medical Info")
    medical_info_option = st.radio("Medical history as text or file upload?", ("Text", "File Upload"))

    if medical_info_option == "Text":
        st.session_state['medical_info_text'] = st.text_area("Enter medical history")
    elif medical_info_option == "File Upload":
        uploaded_file = st.file_uploader("Choose a file")

        if uploaded_file is not None:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            st.session_state['medical_info_text'] = text

    health = st.text_input("Health Issue", value=st.session_state['health_issue'])
    st.session_state['health_issue'] = health
    st.session_state['departure_from'] = st.selectbox("Departure from", ["UAE", "London", "New York"])
    st.session_state['departure_date'] = st.date_input("Departure Date")
    default_arrival_date = datetime.now() + timedelta(days=21)
    st.write(f"We've assumed a 3-week stay for the treatment. You can change the arrival date if needed.")
    st.session_state['arrival_date'] = st.date_input("Arrival Date (Optional)", default_arrival_date)
    st.session_state['people_accompanying'] = st.slider("How many people accompanying the patient?", 1, 10, 1)

    st.header("Hotels")
    st.session_state['hotel_needed'] = st.checkbox("Generate hotels as part of the itinerary?")
    if st.session_state['hotel_needed']:
        st.session_state['hotel_dates']['departure_date'] = st.date_input("Select departure date for hotel booking")
        st.session_state['hotel_dates']['arrival_date'] = st.date_input("Select arrival date for hotel booking")
        st.session_state['accommodation_preference'] = st.selectbox("Accommodation Preference",
                                                                    ["1 star", "2 star", "3 star", "4 star", "5 star"], index=3)

    st.header("Transfers")
    st.markdown("This is for a Future version of the app. For now, you can use Careem or Uber to travel anywhere within the country")  
    st.session_state['transfers_needed'] = st.checkbox("Need transfers?")

    st.header("Food")
    st.session_state['dietary_restrictions'] = st.text_input("Dietary Restrictions")
    st.session_state['food_budget'] = st.number_input("Budget", min_value=0)

    st.write("Intercity travel: You can use Careem or Uber to travel anywhere within the country.")

    st.header("Activities Post Recovery")
    st.session_state['activities_post_recovery'] = st.checkbox("Generate activities post recovery?")

    submit_button = st.button(label='Find Medical Services')

    if submit_button:
        with st.spinner("Generating Iternary..."):
            st.header("Recommended Medical Services")
            st.write("Based on your inputs, here are some recommendations:")
            hospitals_df = get_hospital_names(st.session_state['health_issue'])

            #get the rows where the rating is above 4
            hospitals_df = hospitals_df[hospitals_df['rating'] > 4]
            st.markdown(f"#### Here are some hospitals that are recommended for your treatment: ")
            st.dataframe(hospitals_df, use_container_width=True)


if __name__ == "__main__":
    main()
