# AdminGPT: Your AI-Powered Administrative Assistant, powered by OpenAI's Assistant Framework  🚀

AdmiGPT is an AI-powered administrative assistant, harnessing the power of OpenAI's Assistant framework to seamlessly integrate with your email and calendar. Similar to Microsoft's Copilot, only better, it's designed to be your ultimate productivity partner, AdmiGPT offers an array of advanced features, making your administrative tasks simpler, faster, and more efficient.

[![Twitter Follow](https://img.shields.io/twitter/follow/santiagodc?style=social)](https://twitter.com/santiagodc)
[![GitHub Repo stars](https://img.shields.io/github/stars/sdelgadoc/AdminGPT?style=social)](https://github.com/sdelgadoc/AdminGPT/stargazers)

## 🌟 Key Features

- 📧 Email Summarization & Highlight Action Items: Efficiently summarize long emails and pinpoint critical action items, streamlining your workflow.
- 🤖 Intelligent Meeting Proposals: Automatically understand meeting proposals in emails and check your availability.
- 📅 Advanced Calendar Management: View your appointments and find free times, all within the context of your day.
- ✍️ Automated Email Drafting & Sending: Draft and send responses on your behalf, enhancing efficiency and professionalism.
- 🔄 Seamless Email & Calendar Integration: Coordinate email and calendar to automatically respond to meeting requests, suggesting new times if you're unavailable, and send meeting invites as needed.

Unlock the full potential of your email and calendar management with AdminGPT and revolutionize your email and calendar experience today! 🚀

## 🔧 Installation

Follow these steps to setup AutoGPT on your system, or if you want to get started more quickly, click on the link below to run Github Codespaces and skipt steps 1 and 2:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sdelgado/AdminGPT)

### 1. Clone the Repository
To clone the repository to your local machine, use the following command in your terminal:

`git clone https://github.com/sdelgadoc/AdminGPT.git`

This will create a local copy of the repository.

### 2. Install Required Dependencies
After cloning the repository, navigate to the AdminGPT directory using:

`cd AdminGPT`

Then, install the necessary dependencies by running:

`pip install -r requirements.txt`

This command installs all the packages listed in requirements.txt, ensuring the project runs correctly.

### 3. Generate an OpenAI API key
Follow the instructions as per the [OpenAI API Quickstart](https://platform.openai.com/docs/quickstart?context=python)

### 4. Generate your Microsoft Graph credentials
To use this toolkit, you need to set up your credentials explained in the [Microsoft Graph authentication and authorization overview](https://learn.microsoft.com/en-us/graph/auth/). Once you've received a CLIENT_ID and CLIENT_SECRET, you can input them as environmental variables below. You can also use the authentication instructions from the [O365 Python library documentation](https://o365.github.io/python-o365/latest/getting_started.html#oauth-setup-pre-requisite).

## 🧪 Test the Auto-GPT Email Plugin

Test AdminGPT by summarizing a recent email from a particular sender, the most simple functionality.

### Run the AdminGPT command line interface (CLI)**
1. Set the folling authentication environmental variables:
   - CLIENT_NAME: The name of the person who will be using this assistant
   - CLIENT_EMAIL: The email of the person who will be using this assistant
   - OPENAI_API_KEY: The OpenAI API key for authentication
   - CLIENT_ID: The Microsoft Graph client ID for authentication
   - CLIENT_SECRET: The Microsoft Graph client secret for authentication

2. Navigate to the AdminGPT directory using:

   `cd AdminGPT`

3. Run the CLI using:

   `python admingtp.py`

   If the assistant is running correctly, you should see the following on the command line

   `How can I help you?`

   `Enter your request here:`

## 📖 Documentation
Below are documentation resources to help you learn more about AdminGPT, how it was developed, and how to use it.

- Getting Started Notebook: A step-by-step guide to running AdminGPT, and how it's implemented
   - You can find the tutorial notebook [here](https://github.com/sdelgadoc/AdminGPT/blob/main/o365_tutorial.ipynb) in this repo. 

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
