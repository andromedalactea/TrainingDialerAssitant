# Training Dialer Assistant

## Overview

The Training Dialer Assistant is a Python-based application designed to integrate voice interactions through the VAPI API, evaluate the responses using OpenAI's language models, and present the interactions and evaluations through a user-friendly interface built with Streamlit.

## Key Components

- **Flask Application**: Manages incoming webhook requests and processes call transcriptions.
- **Streamlit Interface**: Provides a GUI for initiating calls and viewing evaluations.
- **VAPI Integration**: Uses the VAPI to handle phone calls with predefined scripts and evaluates responses based on AI models.
- **Ngrok**: Creates a secure tunnel to expose the Flask application on an internet-accessible endpoint.


### Requirements

```bash
  ´pip install -r requirements.txt
```
### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/andromedalactea/TrainingDialerAssitant.git
   cd TrainingDialerAssitant
   ```


## To run the Streamlit interface:

bash
```bash
    streamlit run main_streamlit.py
```
Open your browser and navigate to the URL provided by Streamlit, typically http://localhost:8501.

## Usage
- Initiating Calls: Enter a phone number in the Streamlit interface and click "Call". The system will use VAPI to place the call and evaluate the interaction.

- Viewing Results: After the call, the system will automatically fetch and display the evaluation results in the Streamlit interface.

## Contributing
Contributions are welcome! Please feel free to submit pull requests or create issues for bugs, questions, and suggestions.

## License
MIT License