# 🔥 Manual Firebase Authentication Setup Guide

## Step 1: Create Firebase Project & Service Account

### 1.1 Firebase Console Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or select existing project `hershield-8eef0`
3. Enable **Realtime Database**:
   - Go to "Realtime Database" in left sidebar
   - Click "Create Database"
   - Choose "Start in test mode" for now
   - Select region (us-central1 recommended)

### 1.2 Generate Service Account Key
1. Go to **Project Settings** (gear icon)
2. Click **Service accounts** tab
3. Click **Generate new private key**
4. Download the JSON file
5. Rename it to `serviceAccountKey.json`
6. Place it in your HerShield project root directory

### 1.3 Database Rules (Optional - for testing)
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

## Step 2: Manual Key Validation

The downloaded key should look like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
}
```

## Step 3: Test Connection

Run the test script to verify connection:
```bash
python test_firebase_connection.py
```