# Fitness Club Management System

A comprehensive PyQt6-based application for managing fitness club operations including client registration, membership management, attendance tracking, class scheduling, and reporting.

## Features

- **Client Registration**: Register new clients with personal information, medical restrictions, and fitness goals
- **Membership Management**: Create membership types and sell memberships with discounts
- **Attendance Tracking**: Track client check-ins and check-outs by zone (gym, pool, group classes)
- **Class Schedule Management**: Create and manage group classes with trainers and schedules
- **Class Enrollment**: Enroll clients in group classes with capacity management
- **Personal Training**: Book personal training sessions and maintain training journals
- **Reports & Analytics**: Generate comprehensive reports on attendance, revenue, trainer performance, and client activity

## Requirements

- Python 3.8+
- PyQt6 6.6.1
- MySQLdb 1.2.5
- MySQL Server 5.7+

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create MySQL database:
```bash
mysql -u root -p < script.sql
```

3. Update database credentials in `database.py` if needed:
```python
db = DatabaseConnection(
    host='localhost',
    user='root',
    password='your_password',
    database='fitness_club'
)
```

## Running the Application

```bash
python main.py
```

## Database Schema

The application uses the following main tables:

- **clients**: Client information and registration details
- **membership_types**: Available membership packages
- **memberships**: Client membership purchases
- **attendance**: Client check-in/check-out records
- **trainers**: Trainer information
- **group_classes**: Group class definitions
- **class_schedule**: Weekly class schedules
- **class_enrollments**: Client enrollment in classes
- **personal_training_sessions**: Personal training bookings
- **training_journal**: Exercise records for personal training

## Module Structure

- `main.py`: Main application entry point
- `database.py`: Database connection and query execution
- `ui/client_registration.py`: Client registration module
- `ui/membership_management.py`: Membership and subscription management
- `ui/attendance_tracking.py`: Attendance tracking and access control
- `ui/class_schedule.py`: Class schedule management
- `ui/class_enrollment.py`: Class enrollment system
- `ui/personal_training.py`: Personal training management
- `ui/reports.py`: Reports and analytics

## Usage

### Registering a Client
1. Navigate to "Clients" tab
2. Fill in client information
3. Click "Register Client"

### Selling a Membership
1. Navigate to "Memberships" tab
2. Create membership types or select existing ones
3. Enter client ID and select membership type
4. Click "Sell Membership"

### Recording Attendance
1. Navigate to "Attendance" tab
2. Enter client ID and select zone
3. Click "Check In" or "Check Out"

### Managing Classes
1. Navigate to "Classes" tab
2. Create new classes with trainer assignment
3. Add schedules for recurring classes

### Enrolling in Classes
1. Navigate to "Enrollment" tab
2. Select client, schedule, and date
3. Click "Enroll"

### Personal Training
1. Navigate to "Personal Training" tab
2. Book sessions with trainers
3. Add exercises to training journal

### Viewing Reports
1. Navigate to "Reports" tab
2. Select report type and date range
3. Click "Generate Report"

## Notes

- Ensure MySQL server is running before starting the application
- Client IDs and membership IDs are auto-generated
- Membership validity is checked automatically during check-in
- Class capacity is enforced during enrollment
- All timestamps are recorded in the database for audit purposes
