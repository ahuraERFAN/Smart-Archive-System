# 📁 Smart Archive System

A desktop-based Smart Archive Management System developed with **Python** and **PyQt5** that provides document management, OCR processing, role-based authentication, and ticket management.

---

## ✨ Features

### 🔐 Authentication & Authorization
- Secure user login
- Password hashing using PBKDF2 (SHA-256)
- Role-based access control
    - User
    - Staff
    - Manager

---

### 👤 User Panel

Users can:

- Upload new documents
- View submitted documents
- Check document status
- Open archived files
- Submit support tickets for documents
- View ticket history and staff responses

---

### 👨‍💼 Staff Panel

Staff members can:

- Review pending documents
- Open uploaded files
- Run OCR on scanned documents
- Extract structured information automatically
- Approve or reject documents
- Manage user tickets
- Send responses to submitted tickets

---

### 🏢 Manager Panel

Managers have access to:

- Dashboard overview
- User management interface
- Archive statistics
- Administrative controls

---

## 🔍 OCR Engine

The project includes an OCR module capable of:

- Reading Persian and English text
- Image preprocessing
- Extracting structured fields such as:

- Full Name
- National ID
- Date
- Phone Number
- Case Number

The extracted information is stored in JSON format for future processing.

---

## ✍️ Signature Extraction

Automatic signature detection from scanned documents using OpenCV image processing techniques.

---

## 🗄 Database

SQLite database containing:

### Users

- Full name
- National ID
- Username
- Password hash
- Role
- Creation date

### Documents

- Title
- Description
- File path
- OCR result
- Extracted JSON
- Signature path
- Status
- Reviewer information

### Tickets

- User messages
- Staff responses
- Status tracking

### Archive Keys

Unique archive key generation and storage.

---

## 🔒 Security

- PBKDF2 password hashing
- Random salt generation
- Secure password verification
- Role-based authorization

---

## 🛠 Technologies

- Python 3
- PyQt5
- SQLite
- OpenCV
- EasyOCR
- JSON
- PBKDF2 (SHA-256)

---

## 📂 Project Structure

```
auth/
database/
manager_panel/
ocr_engine/
staff_panel/
storage/
tickets/
user_panel/
utils/
```

---

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/yourusername/smart-archive-system.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

---

## 📸 Screenshots

### Login

(Add screenshot)

### User Dashboard

(Add screenshot)

### Staff OCR Review

(Add screenshot)

### Manager Dashboard

(Add screenshot)

---

## 📌 Future Improvements

- AI-based document classification
- Automatic document categorization
- Advanced OCR model
- REST API
- Cloud storage support
- Elasticsearch integration
- Digital signature verification

---

## 👨‍💻 Author

**Erfan Mirzazadeh**

Computer Engineering Student | Python Developer | AI Researcher

GitHub:
https://github.com/yourusername
