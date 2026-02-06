# EduGamify - Gamified E-Learning Platform

A complete gamified learning management system with role-based access control, achievements, leaderboards, and interactive educational games.

## Features

### Authentication & User Management
- **Login System**: Secure credential-based authentication
- **Separate Registration Page**: Role selection for students and teachers
- **Password Recovery**: Token-based password reset flow
- **Role-Based Access**: Admin, Teacher, and Student roles with specific permissions

### Student Features
- Profile picture upload and management
- Course enrollment and access to learning materials
- Assignment submission with file uploads
- Educational game participation with score tracking
- Badge collection based on points earned
- Achievement tracking
- Leaderboard access to view rankings
- Points system for all activities

### Teacher Features
- Create and manage courses
- Upload coursework materials and notes (with file support)
- Create assignments with due dates and point values
- View student submissions
- Grade submissions and provide feedback
- View enrolled students per course
- Access to leaderboard data

### Admin Features
- Complete user management (create, update, delete, role changes)
- Course oversight and management
- Badge system configuration
- Educational game management
- Platform-wide statistics dashboard
- System-wide content control

### Gamification System
- **Points**: Earned through activities, assignments, and games
- **Badges**: Unlocked when reaching point thresholds
- **Leaderboard**: Real-time rankings of top students
- **Achievements**: Track milestones and accomplishments
- **Educational Games**: Interactive activities with score tracking

## Technology Stack

**Backend:**
- Flask 3.0.0 (Python web framework)
- MySQL (Database)
- SQLAlchemy (ORM)
- bcrypt (Password hashing)
- Flask-CORS (Cross-origin support)

**Frontend:**
- Pure HTML5/CSS3/JavaScript
- No external JavaScript frameworks
- Responsive design
- Modern gradient-based UI

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
cd /path/to/gamified-elearning-system
```

### Step 2: Set Up MySQL Database
```bash
mysql -u root -p < database/schema.sql
```

This creates the `gamified_elearning` database with all required tables.

### Step 3: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Configure Environment
Create a `.env` file in the `backend/` directory:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost/gamified_elearning
FLASK_DEBUG=True
```

Replace `your_password` with your MySQL root password.

**Security Note**: Set `FLASK_DEBUG=False` in production environments.

### Step 5: Run the Application
```bash
cd backend
python app.py
```

The application will be available at `http://localhost:5000`

## Default Access

### Creating an Admin Account
1. Register as a teacher or student through the registration page
2. Manually update the user's role in the database:
```sql
UPDATE users SET role='admin' WHERE username='your_username';
```

### Test Accounts
After running the app, create accounts through the registration page:
- **Students**: Select "Student" role during registration
- **Teachers**: Select "Teacher" role during registration
- **Admin**: Create any account and manually change role to 'admin' in database

## Application Structure

```
gamified-elearning-system/
├── backend/
│   ├── app.py              # Flask application & configuration
│   ├── models.py           # SQLAlchemy database models
│   ├── routes.py           # API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── forgot-password.html # Password recovery
│   ├── student-dashboard.html
│   ├── teacher-dashboard.html
│   └── admin-dashboard.html
├── database/
│   └── schema.sql          # MySQL database schema
├── uploads/               # File storage (created automatically)
│   ├── profiles/          # Profile pictures
│   ├── coursework/        # Course materials
│   └── submissions/       # Assignment submissions
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/signin` - Login
- `POST /api/auth/signout` - Logout
- `GET /api/auth/whoami` - Get current user
- `POST /api/auth/request-reset` - Request password reset
- `POST /api/auth/finalize-reset` - Complete password reset

### Profile
- `PUT /api/profile/modify` - Update profile
- `POST /api/profile/avatar-upload` - Upload profile picture

### Courses
- `GET /api/modules/list` - Get user's courses
- `POST /api/modules/establish` - Create course (teacher/admin)
- `GET /api/modules/details/<id>` - Get course details
- `POST /api/modules/join/<id>` - Enroll in course (student)
- `GET /api/modules/roster/<id>` - Get course students (teacher/admin)

### Materials & Assignments
- `GET /api/modules/<id>/resources` - Get course materials
- `POST /api/modules/<id>/resource-upload` - Upload material (teacher/admin)
- `GET /api/modules/<id>/tasks` - Get assignments
- `POST /api/modules/<id>/task-create` - Create assignment (teacher/admin)
- `POST /api/tasks/<id>/deliver` - Submit assignment (student)
- `GET /api/tasks/<id>/responses` - View submissions (teacher/admin)
- `PUT /api/responses/<id>/evaluate` - Grade submission (teacher/admin)

### Gamification
- `GET /api/rankings/top-performers` - Get leaderboard
- `GET /api/trophies/catalog` - Get all badges
- `GET /api/trophies/mine` - Get user's badges
- `GET /api/milestones/mine` - Get user's achievements
- `GET /api/activities/catalog` - Get all games
- `POST /api/activities/<id>/participate` - Record game play (student)
- `GET /api/activities/<id>/records` - Get game high scores

### Admin
- `GET /api/admin/person-list` - Get all users
- `DELETE /api/admin/person-remove/<id>` - Delete user
- `PUT /api/admin/person-role-change/<id>` - Change user role
- `POST /api/admin/trophy-create` - Create badge
- `POST /api/admin/activity-create` - Add game

## Usage Guide

### For Students
1. **Register**: Create account with student role
2. **Set Profile**: Upload profile picture (optional during registration or later)
3. **Enroll**: Browse and join courses
4. **Learn**: Access course materials and notes
5. **Complete**: Submit assignments before due dates
6. **Play**: Participate in educational games
7. **Compete**: Track progress on leaderboard
8. **Collect**: Earn badges based on points

### For Teachers
1. **Register**: Create account with teacher role
2. **Create**: Set up courses with descriptions
3. **Upload**: Share materials and notes with students
4. **Assign**: Create assignments with deadlines and point values
5. **Review**: View student submissions
6. **Grade**: Provide feedback and assign points
7. **Monitor**: Track student progress and class roster

### For Admins
1. **Login**: Access admin dashboard
2. **Manage Users**: Create, modify, or remove accounts
3. **Oversee Courses**: View and manage all courses
4. **Configure Badges**: Set up achievement system
5. **Add Games**: Integrate educational activities
6. **Monitor**: View platform-wide statistics

## Security Features

- **Password Hashing**: bcrypt with salt rounds
- **Session Management**: Secure server-side sessions
- **Role-Based Access**: Endpoint protection by role
- **File Upload Validation**: Secure filename handling
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **CORS Configuration**: Controlled cross-origin requests

## Development Notes

- All frontend pages are standalone HTML files
- No external CSS or JS libraries used
- Responsive design with CSS Grid and Flexbox
- RESTful API architecture
- Modular backend structure
- File uploads stored in `/uploads` directory
- Session persistence across browser restarts

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running
- Check database credentials in configuration
- Ensure `gamified_elearning` database exists

### File Upload Failures
- Check `uploads/` directory permissions
- Verify file size limits (16MB default)
- Ensure proper file types

### Login Problems
- Clear browser cache and cookies
- Check if user exists in database
- Verify password was hashed correctly

## Future Enhancements

- Email integration for password reset
- Real-time notifications
- Video content support
- Discussion forums
- Mobile app version
- Advanced analytics dashboard
- Integration with external learning tools

## License

This project is created for educational purposes.

## Support

For issues or questions, please check the troubleshooting section or review the code comments in the source files.
