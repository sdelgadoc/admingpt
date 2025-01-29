# AdminGPT: Your AI Administrative Assistant Agent, powered by OpenAI's Assistant Framework  🚀

AdmiGPT is an AI-powered administrative assistant, harnessing the power of OpenAI's Assistant framework to seamlessly integrate with your email and calendar. Similar to Microsoft's Copilot, only better, it's designed to be your ultimate productivity partner, AdmiGPT offers an array of advanced features, making your administrative tasks simpler, faster, and more efficient.

[![Twitter Follow](https://img.shields.io/twitter/follow/santiagodc?style=social)](https://twitter.com/santiagodc)
[![GitHub Repo stars](https://img.shields.io/github/stars/sdelgadoc/AdminGPT?style=social)](https://github.com/sdelgadoc/AdminGPT/stargazers)

## 🌟 Key Features
- 📧 Email Summarization & Highlight Action Items: Efficiently summarize long emails and pinpoint critical action items, streamlining your workflow.
- 🤖 Intelligent Meeting Proposals: Automatically understand meeting proposals in emails and check your availability.
- 📅 Advanced Calendar Management: View your appointments and find free times, all within the context of your day.
- ✍️ Automated Email Drafting & Sending: Draft and send responses on your behalf, enhancing efficiency and professionalism.
- 🔄 Seamless Email & Calendar Integration: Coordinate email and calendar to automatically respond to meeting requests, suggesting new times if you're unavailable, and send meeting invites as needed.

## 📢 We Need Your Feedback!
Help shape the future of AdminGPT! Participate in our [feature prioritization poll](https://github.com/sdelgadoc/AdminGPT/discussions/1) and tell us what features you would like to see next. Your input is vital in guiding the development of AdminGPT. [Take the poll now!](https://github.com/sdelgadoc/AdminGPT/discussions/1)

## 🔧 Installation

Follow these steps to setup AdminGPT on your system:

### 1. Clone the Repository
To clone the repository to your local machine, use the following command in your terminal:

`git clone https://github.com/sdelgadoc/AdminGPT.git`

This will create a local copy of the repository.

### 2. Install Required Dependencies
Install the necessary dependencies by running:

`pip install -r requirements.txt`

This command installs all the packages listed in requirements.txt, ensuring the project runs correctly.

### 3. Generate an OpenAI API key
Follow the instructions as per the [OpenAI API Quickstart](https://platform.openai.com/docs/quickstart?context=python)

### 4. Generate your Microsoft Graph credentials
To use this toolkit, you need to set up your credentials explained in the [Microsoft Graph authentication and authorization overview](https://learn.microsoft.com/en-us/graph/auth/). Once you've received a CLIENT_ID and CLIENT_SECRET, you can input them as environmental variables below. You can also use the authentication instructions from the [O365 Python library documentation](https://o365.github.io/python-o365/latest/getting_started.html#oauth-setup-pre-requisite).

## 🧪 Testing

Test AdminGPT by summarizing a recent email from a particular sender, the most simple functionality.

### Run the AdminGPT command line interface (CLI)
1. Set the folling authentication environmental variables:
   - OPENAI_API_KEY: The OpenAI API key for authentication
   - CLIENT_ID: The Microsoft Graph client ID for authentication
   - CLIENT_SECRET: The Microsoft Graph client secret for authentication

2. Run the CLI using:

   `python admingtp_cli.py`

   If the assistant is running correctly, you should see the following on the command line

   `Hello, [YOUR NAME]. How can I help you?`

   `Enter your request here:`

## 🏗 Deploy Django Application Locally

To deploy the Django application locally, follow these steps:

### 1. Follow the Installation and Testing Steps Above
Make sure you have completed all installation steps and tested AdminGPT’s basic functionality.

### 2. Create an Environment Variable File
Create a file in the root directory called `.env` (note the leading dot) and include the following environment variables with your corresponding values:

```
OPENAI_API_KEY=[Your OpenAI API Key]
CLIENT_ID=[Your Client ID]
CLIENT_SECRET=[Your Client Secret]
SECRET_KEY=[Your Django application's secret key]
```

### 3. Run the Django Migrations
Navigate to the project folder and run the migrations:

```bash
python manage.py migrate
```

### 4. Start the Local Django Server
To run the local server using self-signed certificates (for HTTPS):

```bash
python manage.py runserver_plus --cert-file localhost.crt --key-file localhost.key
```

### 5. Authenticate and Generate an Authentication Token
In your browser, go to:

```
https://127.0.0.1:8000/authenticate/
```

> **Note**: Your browser may warn that your connection is not private because you are using self-generated certificates. You can safely proceed.

1. Make sure you are logged into your Microsoft account.  
2. Complete the Microsoft authentication workflow.  
3. If you are redirected to the [AdminGPT GitHub page](https://github.com/sdelgadoc/AdminGPT), the authentication flow has worked correctly.

### 6. Test the Functionality
Send yourself an email with the following content:

```
Subject: Test
Body: 
Hi Monica, can you write a limerick describing the theme of all the meetings I have this week?
```

Then, in your browser, visit:

```
https://127.0.0.1:8000/process-email/
```

If you receive an email from **Monica** performing the requested task, everything is working as expected!

## 🏗 Deploy Django Application to Heroku

To deploy the Django application to Heroku, follow these steps:

### 1. Follow the Installation and Testing Steps Above
Ensure you have completed all installation steps and tested AdminGPT’s basic functionality locally.

### 2. Set Up a New Heroku Application
1. Log in to your [Heroku account](https://heroku.com) and create a new app on the Heroku Dashboard.
2. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) on your computer if you haven’t already.

### 3. Configure Environment Variables on Heroku
1. Navigate to the **Settings** tab of your Heroku app.
2. Click “Reveal Config Vars” and add the following environment variables:
   - `OPENAI_API_KEY`
   - `CLIENT_ID`
   - `CLIENT_SECRET`
   - `SECRET_KEY`
   - `HEROKU_HOST_NAME` (Set this variable to your application's host name, e.g.: admingpt-1a2b3c4d5e.herokuapp.com)

### 4. Configure Static Files for Heroku
1. Run the following command locally to collect static files:
   ```bash
   python manage.py collectstatic
   ```

### 5. Deploy to Heroku
1. Log in to Heroku from your terminal:
   ```bash
   heroku login
   ```
2. Add Heroku as a Git remote:
   ```bash
   heroku git:remote -a your-heroku-app-name
   ```
3. Deploy your code to Heroku:
   ```bash
   git push heroku main
   ```

### 6. Create a Postgres Database Plan
Set up a Postgres database for your Heroku app:

```bash
heroku addons:create heroku-postgresql:essential-0
```

### 7. Run Migrations on Heroku
After deploying, apply your database migrations:

```bash
heroku run python manage.py migrate
```

### 8. Add the Authentication Callback to the Redirect URI
1. Log in to the [Microsoft Entra Admin Center](https://entra.microsoft.com/).
2. Navigate to **Identity > Applications > App registrations** and select your application.
3. Add a redirect URI:
   - In the application overview, click **Add a redirect URI**.
   - Select **Web** as the platform.
   - Add the following redirect URI:
     ```
     https://your-heroku-app-name.herokuapp.com/authenticate_callback/
     ```
   - Click **Save**.

### 9. Authenticate and Generate an Authentication Token
1. Open your browser and visit:
   ```
   https://your-heroku-app-name.herokuapp.com/authenticate/
   ```
   > **Note**: Your browser may warn that the connection is not private. You can safely proceed.
2. Ensure you are logged into your Microsoft account.
3. Complete the Microsoft authentication workflow.
4. If redirected to the [AdminGPT GitHub page](https://github.com/sdelgadoc/AdminGPT), the authentication was successful.

### 10. Test the Functionality
1. Send yourself an email with the following content:
   ```
   Subject: Test
   Body: 
   Hi Monica, can you write a limerick describing the theme of all the meetings I have this week?
   ```
2. In your browser, visit:
   ```
   https://your-heroku-app-name.herokuapp.com/process-email/
   ```
3. If you receive an email from **Monica** performing the requested task, everything is working as expected! 

## 📖 Documentation
Below are documentation resources to help you learn more about AdminGPT, how it was developed, and how to use it.

- [Getting Started Tutorial Notebook:](https://github.com/sdelgadoc/admingpt/blob/main/admingpt_project/o365_tutorial.ipynb) A step-by-step guide to running AdminGPT, and how it's implemented
   - You can find the tutorial notebook [here](https://github.com/sdelgadoc/admingpt/blob/main/admingpt_project/o365_tutorial.ipynb) in this repo. 

## ❓ Frequently Asked Questions
Here are some common questions and answers about AdminGPT:

- ***Q:*** Is this really better than Microsoft's Copilot?
   - ***A:*** I think so, but you decide! Run the repo and let me know.
- ***Q:*** How do I reset my OpenAI API key in AdminGPT?
   - ***A:*** Follow the steps outlined in the API key section of the documentation.
- ***Q:*** Can AdminGPT integrate with other email providers?
   - ***A:*** Currently, AdminGPT is designed to work with Microsfot Outlook email services, but additional providers can be added.
- ***Q:*** What are the system requirements for AdminGPT?
   - ***A:*** AdminGPT requires Python 3.x and a stable internet connection.
