WEEK 1 – Gemini API Integration
Aim
To connect a Python application with Google's Gemini API and generate AI responses using user-provided prompts.

Technologies Used
Python
Google Gemini API
Google GenAI SDK
Environment Variables (.env)
Tools Used
Python
Visual Studio Code
Gemini API
Folder Structure
WEEK1/
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
Installation Steps
Install Python on your system.

Open the WEEK1 folder in VS Code.

Create a virtual environment (optional):

python -m venv myenv
Activate the virtual environment:
myenv\Scripts\activate
Install the required packages:
pip install -r requirements.txt
Create a .env file and add your Gemini API key:
GEMINI_API_KEY=your_api_key_here
Note: Never upload your actual API key to GitHub.

Execution Steps
Run the following command in the terminal:

python main.py
The program connects to the Gemini API.
Enter a prompt or question.
The prompt is sent to the Gemini model.
The Gemini model processes the prompt.
The model generates an AI response.
The response is displayed in the terminal.
Expected Output
The program displays an AI-generated response based on the prompt entered by the user.

Example:

Input:

What is Artificial Intelligence?
Output:

Artificial Intelligence is a branch of computer science
that enables machines to perform tasks that normally
require human intelligence.
Result
Successfully connected a Python application with Google's Gemini API and generated AI responses using user-provided prompts.
