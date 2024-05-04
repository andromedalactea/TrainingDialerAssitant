import streamlit as st
import json
import time
import os

# Import the necessary modules from your custom scripts.
from scripts.weebhook_calification import *
from scripts.call_vapi_api import *

def main_interface():
    # Define the domain and server URL for the API calls.
    domain = "loosely-stirred-porpoise.ngrok-free.app"
    url_server = f"https://{domain}/calificate_call"
    
    # Set the title of the main interface.
    st.title("Training Dialer Assistant")
    
    # Create a form for user input.
    with st.form(key='my_form', clear_on_submit=True):
        number = st.text_input("Enter the phone number:", help="Format: +18065133220")
        submit_button = st.form_submit_button(label='Call')
        
        # Handle the form submission.
        if submit_button:
            # Call the function to initiate the AI call and retrieve the call ID.
            call_id = call_ai(number, url_server)
            if call_id:
                # Store the call ID and update the interface to show waiting screen.
                st.session_state['call_id'] = call_id
                st.session_state['current_view'] = 'waiting'
                st.experimental_rerun()
            else:
                # Display an error message if the call initiation fails.
                st.error("There was an error with the number you entered. Please check and try again.")

def waiting_interface():
    # Set the title for the waiting screen.
    st.title('Waiting for Evaluation Results')
    
    # Inform the user that the system is retrieving results.
    st.write(f"Please wait, retrieving results for call ID: {st.session_state['call_id']}")
    
    # Provide a button to return to the home screen.
    if st.button("Back to Home"):
        st.session_state['current_view'] = 'main'
        st.experimental_rerun()

    # Path to the file where call results are stored.
    filepath = "output_files/califications_history.jsonl"
    found = False
    attempts = 0
    
    # Poll the file for results.
    while not found and attempts < 1000:
        with open(filepath, 'r') as file:
            for line in file:
                data = json.loads(line)
                if data.get("call_id") == st.session_state['call_id']:
                    found = True
                    st.session_state['data'] = data
                    st.session_state['current_view'] = 'results'
                    st.experimental_rerun()
                    return
        time.sleep(1)  # Delay between retries.
        attempts += 1
    
    # If no results are found, display an error message.
    if not found:
        st.error("Failed to retrieve results after several attempts. Please try again later.")

def results_interface():
    # Set the title for the results interface.
    st.title('Evaluation Results for Customer Interaction')
    
    # Provide a button to return to the home screen.
    if st.button("Back to Home"):
        st.session_state['current_view'] = 'main'
        st.experimental_rerun()
    
    # Retrieve the evaluation data stored in session state.
    data = st.session_state['data']
    
    # Check if calification data is available and parse it.
    if 'calification' in data:
        calification_data = json.loads(data["calification"])
        st.subheader('Metrics of evaluation (0-10):')
        
        # Display the metrics from the calification data.
        for key, value in calification_data.items():
            if key not in ["Notes", "call_id"]:
                st.metric(label=key, value=value)
        
        # Display detailed notes if available.
        if "Notes" in calification_data:
            st.subheader('Detailed Notes:')
            st.write(calification_data["Notes"])
        else:
            st.write("No detailed notes available.")
    else:
        st.error("Calification data not found in the response.")
    
    # Show the complete JSON data for review.
    st.subheader('JSON Complete:')
    st.json(calification_data)  # Display the complete JSON data.

# Initialize the application state.
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'main'

# Manage the current view of the application based on the state.
if st.session_state['current_view'] == 'main':
    main_interface()
elif st.session_state['current_view'] == 'waiting':
    waiting_interface()
elif st.session_state['current_view'] == 'results':
    results_interface()