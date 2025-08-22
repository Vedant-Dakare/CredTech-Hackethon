# Credit Intelligence Dashboard: Local Setup Guide

This guide will walk you through the process of setting up and running the Credit Intelligence Dashboard locally. The application consists of a Python Flask backend that connects to a MongoDB Atlas database, and a React frontend that displays the data.

---

### Prerequisites

You'll need the following installed on your system:

* **Python 3.x:** For the Flask backend.
* **Node.js & npm:** For the React frontend.
* **MongoDB Atlas:** A cloud-based database account.
* **A tool like `curl` or Postman:** To manually trigger the initial data update.

---

### Step 1: MongoDB Atlas Setup

First, ensure your MongoDB Atlas cluster is correctly configured.

1.  **Network Access:** In your MongoDB Atlas dashboard, navigate to **Network Access** and add a new IP address. For development, you can add `0.0.0.0/0` to allow access from anywhere, but be aware this is not secure for production.
2.  **Get Connection String:** Go to your cluster, click the **Connect** button, choose **Connect your application**, and copy the connection string.

---

### Step 2: Backend Setup (Python)

Navigate to your backend project directory in your terminal.

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the Virtual Environment:**
    * On Windows:
        ```bash
        venv\Scripts\activate
        ```
    * On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install Dependencies:**
    ```bash
    pip install Flask pymongo yfinance flask-cors pandas numpy python-dotenv
    ```

4.  **Create the `config.py` File:**
    Create a new file named `config.py` in the same directory as your `app.py` file. Replace `<your_connection_string>` with the string you copied from MongoDB Atlas.

    ```python
    import os

    class Config:
        MONGO_URI = os.getenv("MONGO_URI", "<your_connection_string>")
    ```

    > **Note:** For security, it's best practice to use a `.env` file and `python-dotenv`. If you do this, create a file named `.env` and add `MONGO_URI=<your_connection_string>` to it. Then, your `config.py` would look like this:
    >
    > ```python
    > import os
    > from dotenv import load_dotenv
    >
    > load_dotenv() # Load environment variables from .env
    >
    > class Config:
    >     MONGO_URI = os.getenv("MONGO_URI")
    > ```

5.  **Run the Backend Server:**
    ```bash
    python app.py
    ```
    Your backend server should now be running on `http://localhost:5000`.

---

### Step 3: Frontend Setup (React)

Open a **new terminal window** and navigate to your React project directory.

1.  **Install Node Dependencies:**
    ```bash
    npm install
    ```

2.  **Run the Frontend App:**
    ```bash
    npm start
    ```
    This will start the React development server. Your dashboard should open automatically in your browser, usually at `http://localhost:3000`.

---

### Step 4: Triggering the Data Update

When you first run the app, the database will be empty, and the dashboard won't have any data to display. You need to manually trigger the first data fetch.

1.  With both the backend and frontend servers running, open a third terminal window.
2.  Execute the following `curl` command to send a POST request to your backend's update endpoint:
    ```bash
    curl -X POST http://localhost:5000/api/update_data
    ```
    You should see a message in your backend terminal confirming that the data update was successful. The dashboard will automatically update once the data is available.

---