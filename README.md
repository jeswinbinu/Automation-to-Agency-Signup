# Agency Eligibility Checker

This Flask application determines the eligibility of a website as a digital services agency using web scraping and analysis with the Gemini API. It also facilitates sending notifications via email using SMTP2Go.

## Features

- **Web Scraping**: Extracts content from a given website URL.
- **Content Analysis**: Uses the Gemini API to analyze website content and determine eligibility as a digital services agency.
- **Email Notifications**: Sends email notifications about the eligibility decision using SMTP2Go.
- **CSV Logging**: Logs decisions and reasons to a CSV file.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/agency-eligibility-checker.git
    cd agency-eligibility-checker
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages** using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the root directory of your project and add the following environment variables:
    ```plaintext
    GEMINI_API_KEY=your_gemini_api_key_here
    SMTP2GO_USERNAME=your_smtp2go_username_here
    SMTP2GO_PASSWORD=your_smtp2go_password_here
    FROM_EMAIL=your_sender_email_here
    ```

## Usage

1. **Run the Flask application**:
    ```bash
    python app2.py
    ```

2. **Open your web browser** and go to `http://localhost:5000`.

3. **Enter a website URL** to check its eligibility as a digital services agency.

4. **Optionally, enter an email address** to receive the decision via email.

## Configuration

- **Gemini API**: Ensure you have a valid API key for the Gemini API and it's set in your `.env` file.
- **SMTP2Go**: Ensure you have valid credentials for SMTP2Go and they are set in your `.env` file.
- **CSV Logging**: Decisions and reasoning are logged in the `agency_decisions.csv` file. Make sure this file is writable.

## Demo
[Demo](https://github.com/jeswinbinu/Automation-to-Agency-Signup/blob/master/Demo.mkv)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

