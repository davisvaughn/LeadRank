# Lead Manager Application

## Overview
The Lead Manager Application is a desktop GUI built using Python's Tkinter library for managing and ranking sales leads. This application lets you add, delete, and view detailed information for each lead while leveraging an AI-assisted ranking system. The AI functionality assigns a numerical score, creates a brief summary, and generates custom copy texts (for email, SMS, and call scripts) for each lead.

## Features
- **Lead Management:**  
  - Add and delete leads.
  - View lead details including phone number, email, and communication threads.
- **AI Ranking:**  
  - Copy a payload of lead data and instructions to your clipboard.
  - Use an external AI service (e.g., ChatGPT) to return:
    - An `ai_score` (between -100 and 100).
    - A brief 1–2 sentence summary.
    - AI-generated copy texts for Email, SMS, and Call Script.
  - Update each lead with the returned values.
- **Generated Copy Functions:**  
  - Display and copy AI-generated email, SMS, and call script texts using dedicated buttons.
- **Data Persistence:**  
  - All lead data (including AI-generated scores, summaries, and copy texts) is saved locally in a JSON file (`leads_data.json`), so your data remains available between sessions.

## Requirements
- **Python 3.x**
- **Tkinter** (typically included with Python installations)
- An external AI service (manual integration via copy/paste for generating AI rankings and copy texts)

## Installation and Setup
1. **Download or Clone** the repository to your local machine.
2. Ensure Python 3.x is installed. If not, download it from [Python.org](https://www.python.org/).
3. No additional third-party libraries are required since the project uses standard libraries (Tkinter and JSON).

## Running the Application
1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Run the application with:
   ```bash
   python lead_manager.py
