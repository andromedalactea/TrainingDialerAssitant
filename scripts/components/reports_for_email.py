# Third Party imports
import markdown2
from weasyprint import HTML, CSS
from io import BytesIO  # Import BytesIO para trabajar en memoria

def generate_pdf_report(calls_info: list, css_path: str) -> bytes:
    """
    Converts the calls info into a PDF using Markdown formatting and applies a CSS style.
    Returns the PDF as a bytes object.

    Parameters:
    calls_info (list): A list of calls data (dictionaries) with information to include in the report.
    css_path (str): The path to the CSS file for styling the PDF.

    Returns:
    Bytes string containing the PDF.
    """
    # Initialize an empty string to store the entire markdown content
    markdown_content = ""

    # Iterate through each call in the calls_info list
    for index, call in enumerate(calls_info):
        # Extract information safely using .get(), with default values in case the field is missing
        call_id = call.get('call_id', 'Unknown Call ID')
        reference = call.get('reference', 'No reference')
        duration = call.get('duration', 'Unknown duration')
        calification = call.get('calification', 'No calification provided')
        transcript_content = call.get('transcript', 'No transcript available')

        # Transform transcript to markdown (with default text if missing)
        transcript = f"<div class='transcript-box'><pre><code>Transcript:\n\n{transcript_content}\n</code></pre></div>"

        # Create the markdown content for each call
        line_content = f"# EVALUATION FOR THE CALL {reference} ({call_id})\n"

        
        # Add calification and transcript (both using .get() with fallbacks)
        line_content += calification
        line_content += f"\n{transcript}\n"

        # Add a page break after each call, except the last one
        if index < len(calls_info) - 1:
            line_content += "\n<div class='page-break'></div>\n"

        # Append to overall markdown content
        markdown_content += line_content
    
    if markdown_content:
        # Convert Markdown content to HTML
        html_content = markdown2.markdown(markdown_content)

        # Read and add CSS to HTML
        with open(css_path, 'r') as css_file:
            css_content = css_file.read()

        # Create a buffer to store the PDF in memory (BytesIO)
        pdf_buffer = BytesIO()

        # Convert HTML content to PDF using WeasyPrint, writing to pdf_buffer
        html = HTML(string=html_content)
        css = CSS(string=css_content)
        html.write_pdf(pdf_buffer, stylesheets=[css])

        # Move the buffer cursor to the beginning, since it's been written to.
        pdf_buffer.seek(0)

        # Return the bytes content of the PDF
        return pdf_buffer.getvalue()