# Local AI Server

## 🎯 Goal
The goal of this project is to create a local AI server that can be used to hosting files saved in local computer, manage local files, and run small local AI LLM and agents.

## 📝 Prerequisites
1. **Python** (3.8 or higher)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
   
2. **pip** (Python package installer)
   - Usually comes with Python installation
   - To verify, run: `python -m pip --version`
   - If not installed, follow [pip installation guide](https://pip.pypa.io/en/stable/installation/)

3. **Git**
   - Download from [git-scm.com](https://git-scm.com/downloads)

## 🛠 Tech Stack
- FastAPI
- Uvicorn
- Python
- Git

## 🚀 Installation
### In Clarify repository By script
You can run the below code in Calrify repository to install the local-ai-server. first cd to the clarify repo folder. Then run the below code:
- Windows: Run `install.bat`
- Mac/Linux: Run `install.sh`

### In Local-AI-Server repository manually
1️⃣ Create a Virtual Environment
Run this in your local-ai-server folder:
```bash
python3 -m venv venv
```
This creates a virtual environment named venv.

2️⃣ Activate the Virtual Environment
For macOS/Linux:
```bash
source venv/bin/activate
```
For Windows (if needed in future):
```bash
venv\Scripts\activate
```
You should see something like (venv) in your terminal prompt, meaning it's activated.

3️⃣ Install Dependencies from requirements.txt
Now, install all the required dependencies inside the virtual environment:
```bash
pip install -r requirements.txt
```

4️⃣ Run the FastAPI Server

```bash
uvicorn server:app --reload
```

## 📦 Usage
The server will start automatically after installation at `http://localhost:8000`

## 📝 License
This project is licensed under the MIT License





