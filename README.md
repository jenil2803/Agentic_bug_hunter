Agentic Bug Hunter

This program detects bugs in C++ code using AI.

How to run:

Step 1: Create virtual environment

python -m venv venv

Step 2: Activate virtual environment

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

Step 3: Install requirements

pip install -r requirements.txt

Step 4: Add your API keys

Open the .env file and paste your keys:  (!!! We have already used the perfect API keys in our env, so no need to change !!!)

HUGGINGFACE_API_KEY=paste_your_key_here
GROQ_API_KEY=paste_your_key_here



[!!! DELETE THE OLD OUTPUT.CSV FILE, THEN ONLY THE CODE WILL RUN !!!]




Step 5: Run the program

python run.py

The results will be saved in output/output.csv

That's it.

Team members:
Soham - Bug detector
Vedant - Bug explainer
Jenil - Database
Diti - API server
