# COVID-19 Vaccine Scheduler

A command-line scheduling system for managing **patients, caregivers, vaccines, and appointments**.  
Developed as part of **CSE414: Introduction to Database Systems** coursework (HW6).

---

## Features

- **User Management**
  - Create patient and caregiver accounts with password validation  
    *(must include upper/lowercase, number, and special character)*  
  - Login/logout for both patients and caregivers  

- **Vaccine Management**
  - Add doses for authorized vaccines (e.g., Pfizer, Moderna, J&J)  
  - Track available stock in the database  

- **Scheduling**
  - Caregivers upload availability by date  
  - Patients search available caregivers and vaccines  
  - Patients reserve appointments (system randomly assigns an available caregiver)  
  - Automatic updates to vaccine stock and caregiver schedule  

- **Appointments**
  - Show upcoming appointments for logged-in users  
  - Cancel appointments (restores vaccine dose and caregiver availability)  

---

## Directory Structure

CSE414-vaccine-scheduler-python/
│
├── hw6/
│ └── vaccine-scheduler-python-master/
│ ├── src/
│ │ ├── main/
│ │ │ └── scheduler/
│ │ │ ├── Scheduler.py # Main entry point
│ │ │ ├── model/ # Vaccine, Patient, Caregiver classes
│ │ │ ├── db/ # Database connection manager
│ │ │ └── util/ # Salt & hash utilities
---

## Usage

1. **Setup the database**
   - Ensure a SQL Server database is running and seeded with:
     - `Patients`
     - `Caregivers`
     - `Vaccines`
     - `Availabilities`
     - `Appointments`

2. **Run the scheduler**
   ```bash
   python Scheduler.py
