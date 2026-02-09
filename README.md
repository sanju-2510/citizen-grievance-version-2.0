# Citizen Grievance & Welfare System

A comprehensive multilingual web application for managing citizen grievances and accessing welfare schemes in Tamil Nadu.

## 🌟 Features

### Core Functionality
- **Multilingual Support**: English, Tamil (தமிழ்), Telugu (తెలుగు), Malayalam (മലയാളം), Hindi (हिन्दी)
- **Voice Input/Output**: Speech-to-text and text-to-speech in all supported languages
- **AI-Powered Analysis**: Automatic sector detection and priority assignment
- **Real-time Tracking**: Track complaint status with unique IDs
- **Community Feed**: View grievances grouped by pincode
- **Welfare Schemes**: Browse Tamil Nadu government welfare programs

### User Features
- Voice-enabled grievance registration
- Address and description input via speech
- Document upload (images/PDFs) as evidence
- SMS notifications via Twilio integration
- Multilingual chatbot assistant
- Responsive dark-mode UI with glassmorphism

### Admin Features
- Dashboard with complaint statistics
- Cluster-based complaint views
- Status update management
- Priority filtering

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **NLTK** - Natural language processing
- **Twilio** - SMS notifications

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript** - Dynamic functionality
- **Web Speech API** - Voice features
- **Particles.js** - Interactive background

### Database
- SQLite (Development)
- Schema includes Users, Complaints, and Clusters

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Modern web browser (Chrome/Edge recommended for voice features)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/varshethanivashini2937/citizen-griveance-and-welfare-system-.git
cd citizen-griveance-and-welfare-system-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```python
python
>>> from app import db, app
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## 📱 Usage

### For Citizens
1. **Sign Up/Login**: Create an account or login
2. **File Grievance**: 
   - Use voice input or type your complaint
   - Upload supporting documents
   - AI automatically detects sector and priority
3. **Track Status**: Use your unique complaint ID
4. **View Welfare Schemes**: Browse available government programs
5. **Chatbot**: Get help in your preferred language

### For Administrators
1. Login with admin credentials
2. Access admin dashboard
3. View and manage complaints
4. Update complaint status
5. Monitor clusters and statistics

## 🗂️ Project Structure

```
final prototype/
├── app.py                  # Main Flask application
├── models.py               # Database models
├── nlp_utils.py           # NLP utilities
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   ├── js/
│   │   └── main.js        # Frontend logic, translations
│   └── uploads/           # Evidence file storage
└── templates/
    ├── base.html          # Base template
    ├── index.html         # Landing page
    ├── login.html         # Login page
    ├── signup.html        # Registration page
    ├── dashboard.html     # User dashboard
    ├── admin.html         # Admin panel
    ├── track.html         # Complaint tracking
    └── welfare.html       # Welfare schemes
```

## 🌐 Supported Languages

- **English** (en)
- **Tamil** (ta) - தமிழ்
- **Telugu** (te) - తెలుగు
- **Malayalam** (ml) - മലയാളം
- **Hindi** (hi) - हिन्दी

All UI elements, voice features, and chatbot responses support these languages.

## 🔧 Configuration

### Twilio SMS (Optional)
Update credentials in `app.py`:
```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_number'
```

### Database
Default: SQLite (`grievance.db`)
To use PostgreSQL/MySQL, update `SQLALCHEMY_DATABASE_URI` in `app.py`

## 📊 Key Features Detail

### Voice Recognition
- Real-time speech-to-text in native languages
- Error handling for microphone access, network issues
- Language-specific voice selection

### NLP Analysis
- Keyword-based sector detection (Roads, Water, Electricity, etc.)
- Priority classification (High/Medium/Low)
- Cluster ID generation from pincode and sector

### Welfare Schemes
Organized by categories:
- Education (Breakfast Scheme, Laptop Scheme, Scholarships)
- Health (Insurance, Medical Kits)
- Social Security (Pensions for elderly, widows)
- Housing
- Women & Child Welfare

## 🎨 Design Features

- Modern glassmorphism UI
- Animated particle background
- Responsive design for all devices
- Dark blue color scheme (#1a237e, #3f51b5)
- Smooth transitions and hover effects

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is developed for educational and governmental purposes.

## 👥 Authors

- Varshetha Nivashini

## 🙏 Acknowledgments

- Tamil Nadu Government for welfare scheme information
- Google Fonts (Inter)
- Font Awesome for icons
- Particles.js for background effects

## 📞 Support

For issues or questions, please open an issue on GitHub or contact the development team.

---

**Note**: This is a prototype system. For production deployment, ensure proper security measures, environment variables for credentials, and scalable database solutions.
