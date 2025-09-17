
# Hotel Management System 🏨  

The **Hotel Management System** is built with **Python Flask**, providing features for online room booking, payment processing, customer management, and business reporting.  
The project aims to optimize hotel operations, enhance customer experience, and support staff/administrators in making data-driven decisions.  

## System Architecture
<p align="center">
  <img src="https://github.com/Eel-Aig-gYuh/Hotel_App/blob/main/assert/archiSys.png"/>
</p>

---

For a full system analysis, design diagrams, and use case specifications, please refer to the project report:
[Hotel Management System Report (DOCX)](https://github.com/Eel-Aig-gYuh/Hotel_App/blob/main/assert/CNPM%20Nhom%2002%20Quan%20ly%20Thue%20Phong.docx)

---

## 📑 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation & Run](#-installation--run)
- [Database Schema](#-database-schema)
- [Team Members](#-team-members)

---

## 🚀 Features
- **Customer**
  - Register / Login  
  - Search and book rooms (online/offline)  
  - Pay online via Stripe or at the front desk  
  - Update personal profile  
  - Leave reviews for rooms and services  

- **Staff**
  - Confirm customer check-in  
  - Manage bookings and invoices  
  - Generate reports and statistics on revenue & room usage  

- **Administrator**
  - Manage users and staff  
  - Update hotel policies (check-in/out time, deposit rules, etc.)  

---

## 🛠️ Tech Stack
- **Backend:** Python 3.x, Flask  
- **Database:** MySQL / SQLite (configurable in `__init__.py`)  
- **Core Libraries:** Flask-SQLAlchemy, Flask-Login, Stripe API, …  
- **Frontend:** HTML, CSS, Bootstrap, Jinja2 templates  

---

## ⚙️ Installation & Run

1. **Clone the project & open with PyCharm (or any IDE):**  
   ```bash
   git clone <repository-link>
   cd hotel-management
   ```

2. **Create virtual environment:**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Configure database:**  
   - Create a database with the same name as configured in `__init__.py`.

4. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize database schema & sample data:**  
   ```bash
   python models.py
   ```

6. **Run the project:**  
   ```bash
   python index.py
   ```
   Access via: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)  

---

## 📊 Database Schema
Main entities include:  
- `User`, `Staff`, `Customer` – user and staff management  
- `Hotel`, `Room`, `RoomType` – hotel and room management  
- `Booking`, `Bill`, `BillDetail` – booking and billing  
- `Service`, `Comment`, `Rule` – services, feedback, and hotel policies  

(See detailed schema in the system design report.)  

---

## 📌 Team Members
- **2251010040 - Le Gia Huy**  
- **2251050057 - Nguyen Phong Phu**  
