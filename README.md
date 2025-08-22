# Credit Intelligence Dashboard: Local Setup Guide

This guide will walk you through the process of setting up and running the Credit Intelligence Dashboard locally. The application consists of a **Python Flask backend** that connects to a **MongoDB Atlas database**, and a **React frontend** that displays the data.

---

## Prerequisites

You'll need the following installed on your system:

- **Python 3.x**: For the Flask backend.  
- **Node.js & npm**: For the React frontend.  
- **MongoDB Atlas**: A cloud-based database account.  
- **A tool like curl or Postman**: To manually trigger the initial data update.  

---

## Step 1: MongoDB Atlas Setup

1. **Network Access**:  
   In your MongoDB Atlas dashboard, navigate to **Network Access** and add a new IP address.  
   For development, you can add `0.0.0.0/0` to allow access from anywhere, but be aware this is **not secure for production**.

2. **Get Connection String**:  
   - Go to your cluster.  
   - Click the **Connect** button.  
   - Choose **Connect your application**.  
   - Copy the connection string.

---

## Step 2: Backend Setup (Python)

1. **Navigate to the backend project directory** in your terminal.

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
