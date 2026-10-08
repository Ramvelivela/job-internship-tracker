# Job & Internship Tracker

A full-stack web application designed to help students and job seekers manage, organize, and track their job and internship applications in one place.

## 🚀 Live Demo

[Job & Internship Tracker](https://job-internship-tracker-5aq1.onrender.com)

## ✨ Features

### 🔐 Authentication
- User registration and login
- Login using username or email
- Secure password hashing
- Change password
- Forgot password and password reset
- Session-based authentication

### 💼 Job Management
- Add new job applications
- Edit job details
- Delete jobs with confirmation
- View detailed job information
- Search jobs
- Filter jobs by application status
- Filter jobs by date
- Track application dates
- Track deadlines
- Track interview dates
- Track follow-up dates
- Add notes to applications
- Add and manage application links

### 🎓 Internship Management
- Add new internships
- Edit internship details
- Delete internships with confirmation
- View detailed internship information
- Search internships
- Filter internships by status
- Filter internships by date
- Track deadlines
- Track interviews
- Track follow-ups
- Add notes
- Store internship application links

### 📊 Dashboard
- Total applications overview
- Applied applications count
- Interview count
- Selected applications count
- Rejected applications count
- Search and filtering
- Professional notification system
- Mark notifications as read
- Responsive dashboard design

### 👤 Profile Management
- Personal details
- Educational qualifications
- Job preferences
- Profile settings
- Change password
- Profile completion tracking

### 🎓 Education
- Degree and branch
- College / university
- Graduation year
- CGPA
- Intermediate / 12th college and percentage
- SSC / 10th school and percentage

### 📄 Resume Management
- Upload existing resume
- View uploaded resume
- Delete resume
- Build resume directly inside the application
- Add professional summary
- Add skills
- Add projects
- Add certifications
- Add achievements
- Generate ATS-friendly PDF resume
- Preview resume before downloading
- Download resume as PDF

### 🎨 UI & Experience
- Professional responsive interface
- Mobile-friendly layout
- Light and dark theme support
- Modern login and registration pages
- Confirmation modals
- Notification panel
- Clean dashboard interface

## 🛠️ Technologies Used

- **Python**
- **Flask**
- **SQLite** — local development
- **PostgreSQL** — production database
- **HTML5**
- **CSS3**
- **JavaScript**
- **Jinja2**
- **ReportLab**
- **Gunicorn**
- **Render** — deployment

## 📁 Project Structure

```text
job-internship-tracker/
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── add_job.html
│   ├── edit_job.html
│   ├── add_internship.html
│   ├── edit_internship.html
│   ├── job_details.html
│   ├── internship_details.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── personal_details.html
│   ├── qualifications.html
│   ├── job_preferences.html
│   ├── profile_settings.html
│   ├── change_password.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── resume.html
│   ├── build_resume.html
│   └── resume_preview.html
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
└── README.md