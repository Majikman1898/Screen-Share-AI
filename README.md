# AI Screen Reader

A Windows desktop application that captures your screen via a global hotkey, sends the image to OpenAI's GPT-4o (or other vision-capable models), and reads the response aloud using text-to-speech.

## Features

*   **Global Hotkey:** Capture your screen instantly from any application.
*   **AI Analysis:** Uses OpenAI's powerful vision models to describe your screen or answer questions about it.
*   **Text-to-Speech:** Automatically reads the AI's response aloud.
*   **Context Awareness:** Option to maintain conversation history for context-aware responses.
*   **GUI Interface:** Easy-to-use interface to manage settings and view logs.

## Prerequisites

*   **Operating System:** Windows is recommended.
    *   *Note for Linux/Mac users:* The `keyboard` library may require root/sudo permissions (e.g., `sudo python main.py`) to intercept global hotkeys.
*   **Python:** Python 3.7 or higher.
*   **OpenAI API Key:** You need a valid API key from [OpenAI Platform](https://platform.openai.com/).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create and activate a virtual environment (optional but recommended):**
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **Linux/Mac:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```

2.  **Configure Settings:**
    *   **OpenAI API Key:** Paste your API key into the "OpenAI API Key" field.
    *   **Model:** Select the model you wish to use (e.g., `gpt-4o`).
    *   **Hotkey:** The default hotkey is `ctrl+alt+s`. You can change this in the "Hotkey" field and click "Set Hotkey".

3.  **Start Listening:**
    *   Click the **Start Listening** button. The status bar will change to "Listening for hotkey...".

4.  **Capture Screen:**
    *   Press your configured hotkey (e.g., `Ctrl` + `Alt` + `S`).
    *   The application will capture the current screen content, send it to the AI, and the AI's response will be read aloud and displayed in the log.

## Troubleshooting

*   **Hotkey not working:**
    *   Ensure the application is running and "Listening".
    *   If on Linux, try running with `sudo`.
    *   Ensure no other application is blocking the hotkey.
*   **Audio not playing:**
    *   Check your system volume.
    *   Ensure `pyttsx3` drivers are correctly installed for your OS.
*   **OpenAI Error:**
    *   Check that your API key is correct and has credits/billing enabled.
    *   Ensure you have access to the selected model (e.g. GPT-4o).
