import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request
import google.generativeai as genai
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import http.client
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv  # Import dotenv to load environment variables

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Get Gemini API key from environment
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-pro"

# --- SMTP2Go Configuration ---
SMTP2GO_USERNAME = os.getenv('SMTP2GO_USERNAME')  # Get SMTP2Go username from environment
SMTP2GO_PASSWORD = os.getenv('SMTP2GO_PASSWORD')  # Get SMTP2Go password from environment
SMTP2GO_SERVER = 'mail.smtp2go.com'
SMTP2GO_PORT = 2525  # You can also use 8025, 587, or 25
FROM_EMAIL = os.getenv('FROM_EMAIL')  # Get sender email from environment

# --- Keywords ---
KEYWORDS = [
    'Services', 'Web design', 'Web Development', 'SEO agency',
    'Ads Agency', 'Digital marketing agency', 'Agency', 'Website creation'
]

# --- Custom Retry Session ---
def create_retry_session(retries=3, backoff_factor=0.5):
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],  # Include 429 for rate limiting
        backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

# --- Scrape Website ---
def scrape_website(url, retry_session):
    headers_list = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
             'Accept-Encoding': 'gzip, deflate',
        },
        {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
             'Accept-Encoding': 'gzip, deflate',
        }
    ]
    
    for headers in headers_list:
        try:
            response = retry_session.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ')
            return text
        except requests.exceptions.RequestException as e:
            continue # Try next header
    
    return f"Error scraping {url}: Failed after multiple retries and headers."

# --- Analyze with Gemini API ---
def analyze_content_with_gemini(content):
    prompt = f"""
        Analyze the following text and determine if the website belongs to an agency
        providing digital services such as website creation, branding, SEO, digital marketing,
        or similar offerings.

        Provide a professional and concise explanation for your decision, using a narrative
        style. Do not use bulleted lists. Focus on providing an overall assessment of
        why the website qualifies or does not qualify as an agency. Be sure to mention the type
        of services offered. Avoid being repetitive; focus on giving a clear rationale. Respond
        with either 'Eligible' or 'Not Eligible', followed by your professional explanation.

        Text:
        {content[:2000]}  # Limit input size to avoid API token limits
        """

    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        return result
    except Exception as e:
        return f"Error with Gemini API: {e}"

# --- Send Email Function (SMTP2Go) ---
def send_email(to_email, subject, body):
    try:
        # Create the email message
        msg = MIMEMultipart('alternative')  # Use 'alternative' instead of 'mixed'
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email


        # Attach only the HTML version of the email with correct tags
        html_body = f"""
        <html>
          <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
          </head>
          <body>
           {body}
          </body>
        </html>
        """
        html_message = MIMEText(html_body, 'html')
        msg.attach(html_message)


        # Connect to SMTP2Go server and send the email
        mailServer = smtplib.SMTP(SMTP2GO_SERVER, SMTP2GO_PORT)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(SMTP2GO_USERNAME, SMTP2GO_PASSWORD)
        mailServer.sendmail(FROM_EMAIL, to_email, msg.as_string())
        mailServer.close()

        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

# --- Main Process ---
def process_agency(url, retry_session):
    # Step 1: Scrape the website
    website_content = scrape_website(url, retry_session)
    if "Error" in website_content:
        return None, website_content

    # Step 2: Analyze with Gemini API
    gemini_result = analyze_content_with_gemini(website_content)

    # Step 3: Improved Decision Logic
    lines = gemini_result.splitlines()
    first_line = lines[0].strip().lower()  # Analyze the first line for decision
    if "eligible" in first_line and "not" not in first_line:
        decision = "Eligible"
    elif "not eligible" in first_line or "not" in first_line:
        decision = "Not Eligible"
    else:
        decision = "Uncertain"

    # Extract reasoning from the remaining text
    reasoning = " ".join(line.strip() for line in lines[1:]).strip()

    return decision, reasoning

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    decision = None
    reasoning = None
    error = None
    email_status = None

    if request.method == 'POST':
        url = request.form['url']
        recipient_email = request.form.get('recipient_email')  # Get recipient email from form

        if not url:
            error = "Please enter a valid URL."
        else:
            retry_session = create_retry_session()
            result = process_agency(url, retry_session)
            if result and isinstance(result, tuple) and len(result) == 2:
                decision, reasoning = result

                # Save results to CSV
                data = {"URL": [url], "Decision": [decision], "Reasoning": [reasoning]}
                df = pd.DataFrame(data)
                df.to_csv("agency_decisions.csv", mode='a', index=False, header=False)

                # If the user clicked the "Send Email" button and provided an email
                if 'send_email' in request.form and recipient_email:
                    if decision == "Eligible":
                        email_subject = "Welcome to Our Platform!"
                        email_body = f"Congratulations! Your agency has been approved. {reasoning}"
                    else:
                        email_subject = "Application Rejected"
                        email_body = reasoning

                    # Send email to the provided recipient email
                    email_status = send_email(recipient_email, email_subject, email_body)

    return render_template('index2.html', decision=decision, reasoning=reasoning, error=error, email_status=email_status)


if __name__ == '__main__':
    app.run(debug=True)