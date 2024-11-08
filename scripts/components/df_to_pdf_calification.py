# Local imports
from auxiliar_functions import transcripts_to_md

# Third Party imports
import pandas as pd
import markdown2
import pdfkit
from weasyprint import HTML, CSS


def df_to_pdf(df: pd.DataFrame, output_pdf_path: str, css_path: str) -> None:
    """
    Converts the DataFrame into a PDF using Markdown formatting and applies a CSS style.

    Parameters:
    df (pd.DataFrame): The DataFrame with the lead reports.
    output_pdf_path (str): The path where the PDF file will be saved.
    css_path (str): The path to the CSS file for styling the PDF.
    """
    # Initialize an empty string to store the entire markdown content
    markdown_content = ""
    print(df.head())

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Transfrom transcript to markdown
        if row['qualification_from_audio']:
            transcript = "<div class='transcript-box'><pre><code>Transcript:\n\n" + row['transcript'] + "\n</code></pre></div>"
        else:
            try:
                transcript = transcripts_to_md(row['transcript'])
            except:
                transcript = None

        if transcript and row['qualification_from_audio'] and transcript != "Unavailable":
            # Construct the markdown content for each row
            if row['qualification_from_audio']:
                line_content = f"# Evaluation for {row['full_name']} ({row['user']})\n".upper() 
            else:
                line_content = f"# Evaluation for {row['full_name']} ({row['user']}) [Only with transcribe]\n".upper() 

            # Add header for call information
            line_content += "\n## **Call Information**:\n\n"

            # Call date, checking if it's available
            # line_content += f"**Date:** {row['call_date'] if pd.notna(row['call_date']) else 'Unavailable'}\n\n"

            # Dialed phone number, ensuring 'phone_code' is an integer and 'phone_number_dialed' is not null
            phone_code = int(row['phone_code']) if pd.notna(row['phone_code']) else "Unknown"
            phone_number = row['phone_number_dialed'] if pd.notna(row['phone_number_dialed']) else "Unknown"
            line_content += f"**Phone number dialed:** +{phone_code} {phone_number}\n\n"

            # Call duration in seconds, handling possible missing values
            # duration = row['length_in_sec'] if pd.notna(row['length_in_sec']) else "Unknown"
            # line_content += f"**Duration:** {duration} seconds\n\n"

            # Lead name and ID, checking availability
            first_name = row['first_name'] if pd.notna(row['first_name']) else "Unknown"
            lead_id = row['lead_id'] if pd.notna(row['lead_id']) else "Unknown"
            line_content += f"**Lead Name/ID:** {first_name} ({lead_id})\n\n"

            # Location of the call (city and state), with checks for available values
            city = row['city'] if pd.notna(row['city']) else "Unknown"
            state = row['state'] if pd.notna(row['state']) else "Unknown"
            line_content += f"**Location:** {city} ({state})\n\n"

            # Company name, handling missing values
            company = row['last_name'] if pd.notna(row['last_name']) else "Unknown"
            line_content += f"**Company:** {company}\n\n"

            # Infor about the calification and transcript
            line_content += f"\n{row['qualification']}\n"
            line_content += f"\n{transcript}\n"

            # Add a page break after each row
            if index < len(df) - 1:
                line_content += "\n<div class='page-break'></div>\n"

            
            # Append this line to the overall markdown content
            markdown_content += line_content
    
    if markdown_content != "":

        # Delete the last page break
        print(markdown_content)
        # Convert Markdown content to HTML
        html_content = markdown2.markdown(markdown_content)

        # Read and add CSS to HTML
        with open(css_path, 'r') as css_file:
            css_content = css_file.read()
        
        # Convert HTML content to PDF using WeasyPrint
        html = HTML(string=html_content)
        css = CSS(string=css_content)

        # Generate PDF with CSS
        html.write_pdf(output_pdf_path, stylesheets=[css])
# Usage example:
# Assuming `df` is your DataFrame
# df_to_pdf(df, 'output.pdf', 'path/to/styles.css')
