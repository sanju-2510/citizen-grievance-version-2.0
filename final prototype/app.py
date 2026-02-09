import os
import random
import string
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
from models import db, User, Complaint, Cluster
from nlp_utils import detect_sector, detect_priority, get_cluster_id
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
CORS(app)

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(name='Admin Official', email='admin@gov.in', phone='0000000000', password='admin', role='admin')
        db.session.add(admin)
        db.session.commit()

from twilio.rest import Client

# Twilio Configuration - Use environment variables for security
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'your_account_sid_here')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'your_auth_token_here')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+1234567890')

def send_sms(to, body):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # Ensure number has country code, default to +91 if missing
        if not to.startswith('+'):
            to = '+91' + to
        
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        print(f"[SMS SENT] To: {to}, SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[SMS FAILED] Error: {e}")
        return False

def generate_complaint_id():
    return 'CG' + ''.join(random.choices(string.digits, k=8))

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(email=data.get('email'), password=data.get('password')).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return jsonify({'success': True, 'role': user.role})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'success': False, 'message': 'Email already exists'})
        
        new_user = User(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            password=data.get('password'),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True})
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    complaints = Complaint.query.filter_by(user_id=user_id).all()
    
    public_feed = Complaint.query.all()
    
    return render_template('dashboard.html', user=user, complaints=complaints, public_feed=public_feed)

@app.route('/welfare')
def welfare():
    return render_template('welfare.html')

@app.route('/track-page')
def track_page():
    return render_template('track.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    complaints = Complaint.query.all()
    stats = {
        'total': len(complaints),
        'high': len([c for c in complaints if c.priority == 'High']),
        'pending': len([c for c in complaints if c.status != 'Resolved']),
        'resolved': len([c for c in complaints if c.status == 'Resolved'])
    }
    return render_template('admin_dashboard.html', complaints=complaints, stats=stats)

# --- API ENDPOINTS ---

@app.route('/api/analyze', methods=['POST'])
def analyze_complaint():
    description = request.json.get('description', '')
    sector = detect_sector(description)
    priority = detect_priority(description)
    return jsonify({
        'sector': sector,
        'priority': priority
    })

@app.route('/api/submit-grievance', methods=['POST'])
def submit_grievance():
    data = request.form
    complaint_id = generate_complaint_id()
    sector = data.get('target_sector') or detect_sector(data.get('description'))
    priority = detect_priority(data.get('description'))
    cluster_id = get_cluster_id(data.get('pincode'), sector)
    phone_number = data.get('phone')
    
    evidence_path = None
    if 'evidence' in request.files:
        file = request.files['evidence']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            evidence_path = file_path

    new_complaint = Complaint(
        complaint_id=complaint_id,
        user_id=session.get('user_id'),
        citizen_name=data.get('name'),
        phone=phone_number,
        aadhaar=data.get('aadhaar'),
        address=data.get('address'),
        pincode=data.get('pincode'),
        description=data.get('description'),
        sector=sector,
        priority=priority,
        cluster_id=cluster_id,
        evidence_path=evidence_path
    )
    
    # Handle Clustering/Escalation
    cluster = Cluster.query.filter_by(cluster_id=cluster_id).first()
    if cluster:
        cluster.complaint_count += 1
        if cluster.complaint_count > 5:
            new_complaint.priority = 'High'
    else:
        new_cluster = Cluster(cluster_id=cluster_id, pincode=data.get('pincode'), sector=sector)
        db.session.add(new_cluster)

    db.session.add(new_complaint)
    db.session.commit()

    # Real SMS Notification
    sms_body = f"Grievance Registered. ID: {complaint_id}. Sector: {sector}. We will resolve this soon."
    send_sms(phone_number, sms_body)

    return jsonify({
        'success': True, 
        'complaint_id': complaint_id,
        'message': f'Grievance registered. SMS sent to {phone_number}. Your ID is {complaint_id}'
    })

@app.route('/api/verify-phone', methods=['POST'])
def verify_phone():
    phone = request.json.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Phone number required'})
    
    # In a real app, generate and store OTP. Here just sending verification message.
    verification_code = ''.join(random.choices(string.digits, k=4))
    sms_body = f"Your Verification Code is: {verification_code}. Do not share this with anyone."
    
    if send_sms(phone, sms_body):
        return jsonify({'success': True, 'message': 'Verification code sent!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send SMS'})
@app.route('/api/track/<complaint_id>')
def track_complaint(complaint_id):
    complaint = Complaint.query.filter_by(complaint_id=complaint_id).first()
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'})
    
    return jsonify({
        'success': True,
        'details': {
            'id': complaint.complaint_id,
            'name': complaint.citizen_name,
            'phone': complaint.phone,
            'aadhaar': complaint.aadhaar,
            'sector': complaint.sector,
            'priority': complaint.priority,
            'status': complaint.status,
            'date': complaint.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

@app.route('/api/public-grievances')
def public_grievances():
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    grouped = {}
    
    for c in complaints:
        pin = c.pincode or 'Unknown'
        if pin not in grouped: grouped[pin] = []
        
        grouped[pin].append({
            'id': c.complaint_id,
            'sector': c.sector,
            'description': c.description,
            'status': c.status,
            'date': c.created_at.strftime('%Y-%m-%d'),
            'priority': c.priority
        })
    
    return jsonify({'success': True, 'data': grouped})

@app.route('/api/update-status', methods=['POST'])
def update_status():
    if session.get('role') != 'admin': return jsonify({'success': False})
    data = request.json
    complaint = Complaint.query.filter_by(complaint_id=data.get('id')).first()
    if complaint:
        complaint.status = data.get('status')
        db.session.commit()
        # Mock SMS on update
        print(f"[SMS GATEWAY] Sending to {complaint.phone}: Your grievance {complaint.complaint_id} status updated to {complaint.status}.")
        return jsonify({'success': True})
    return jsonify({'success': False})

CHAT_RESPONSES = {
    'en': {
        'track': 'Please provide your Complaint ID to track.',
        'file': 'You can file a grievance by clicking the "File a Grievance" button on your dashboard.',
        'greet': 'Hello! I am your Citizen Welfare Assistant. How can I help you today?',
        'welcome': 'You are welcome! My pleasure',
        'need_help': 'Do you need any other help? I am here to assist you!',
        'bye': 'Goodbye! Take care. Feel free to reach out anytime!',
        'yes': 'Great! How can I assist you further?',
        'no': 'No problem! Let me know if you need anything else.',
        'default': 'I can help with filing grievances, tracking complaints, or welfare schemes.'
    },
    'ta': {
        'track': 'கண்காணிக்க உங்கள் புகார் எண்னை வழங்கவும்.',
        'file': 'உங்கள் முகப்புத் திரையில் "புகார் பதிவு செய்" என்ற பட்டனை அழுத்தி புகார் அளிக்கலாம்.',
        'greet': 'வணக்கம்! 👋 நான் உங்கள் நல உதவியாளர். உங்களுக்கு எப்படி உதவ முடியும்?',
        'welcome': 'நல்வரவு! என் மகிழ்ச்சி 😊',
        'need_help': 'வேறு ஏதாவது உதவி தேவையா? நான் இங்கே இருக்கிறேன்! 😊',
        'bye': 'விடைபெறுகிறேன்! கவனமாக இருங்கள். எப்போது வேண்டுமானாலும் தொடர்பு கொள்ளுங்கள்! 👋',
        'yes': 'நல்லது! மேலும் எப்படி உதவ முடியும்?',
        'no': 'பரவாயில்லை! வேறு ஏதாவது தேவைப்பட்டால் தெரியப்படுத்துங்கள்.',
        'default': 'புகார் பதிவு செய்யவும், புகாரைக் கண்காணிக்கவும் நான் உதவ முடியும்.'
    },
    'te': {
        'track': 'దయచేసి మీ ఫిర్యాదు ID ని అందించండి.',
        'file': 'మీ డ్యాష్‌బోర్డ్‌లోని "ఫిర్యాదు చేయండి" బటన్‌పై క్లిక్ చేయడం ద్వారా మీరు ఫిర్యాదు చేయవచ్చు.',
        'greet': 'నమస్కారం! 👋 నేను మీ పౌర సంక్షేమ సహాయకుడిని. నేను మీకు ఎలా సహాయపడగలను?',
        'welcome': 'స్వాగతం! నా ఆనందం 😊',
        'need_help': 'మీకు ఇంకా ఏదైనా సహాయం కావాలా? నేను ఇక్కడే ఉన్నాను! 😊',
        'bye': 'వీడ్కోలు! జాగ్రత్తగా ఉండండి. ఎప్పుడైనా సంప్రదించండి! 👋',
        'yes': 'మంచిది! నేను మరింత ఎలా సహాయపడగలను?',
        'no': 'సరే! మీకు ఇంకా ఏమైనా కావాలంటే చెప్పండి.',
        'default': 'నేను ఫిర్యాదులను దాఖలు చేయడంలో, ట్రాక్ చేయడంలో లేదా సంక్షేమ పథకాల గురించి సహాయపడగలను.'
    },
    'ml': {
        'track': 'ട്രാക്ക് ചെയ്യാൻ നിങ്ങളുടെ പരാതി ഐഡി നൽകുക.',
        'file': 'നിങ്ങളുടെ ഡാഷ്ബോർഡിലെ "പരാതി നൽകുക" ബട്ടൺ ക്ലിക്ക് ചെയ്ത് നിങ്ങൾക്ക് പരാതി നൽകാം.',
        'greet': 'നമസ്കാരം! 👋 ഞാൻ നിങ്ങളുടെ ക്ഷേമ സഹായിയാണ്. എനിക്ക് എങ്ങനെ സഹായിക്കാനാകും?',
        'welcome': 'സ്വാഗതം! എന്റെ സന്തോഷം 😊',
        'need_help': 'മറ്റെന്തെങ്കിലും സഹായം വേണോ? ഞാൻ ഇവിടെയുണ്ട്! 😊',
        'bye': 'വിട! ശ്രദ്ധിക്കുക. എപ്പോൾ വേണമെങ്കിലും ബന്ധപ്പെടുക! 👋',
        'yes': 'നല്ലത്! കൂടുതൽ എങ്ങനെ സഹായിക്കാം?',
        'no': 'കുഴപ്പമില്ല! മറ്റെന്തെങ്കിലും വേണമെങ്കിൽ അറിയിക്കുക.',
        'default': 'പരാതികൾ നൽകുന്നതിനും, പരാതികൾ ട്രാക്ക് ചെയ്യുന്നതിനും എനിക്ക് സഹായിക്കാനാകും.'
    },
    'hi': {
        'track': 'कृपया ट्रैक करने के लिए अपनी शिकायत आईडी प्रदान करें।',
        'file': 'आप अपने डैशबोर्ड पर "शिकायत दर्ज करें" बटन पर क्लिक करके शिकायत दर्ज कर सकते हैं।',
        'greet': 'नमस्ते! 👋 मैं आपका नागरिक कल्याण सहायक हूँ। मैं आपकी कैसे मदद कर सकता हूँ?',
        'welcome': 'स्वागत है! मेरी खुशी 😊',
        'need_help': 'क्या आपको कोई और मदद चाहिए? मैं यहाँ हूँ! 😊',
        'bye': 'अलविदा! ख्याल रखें। कभी भी संपर्क करें! 👋',
        'yes': 'बढ़िया! मैं और कैसे मदद कर सकता हूँ?',
        'no': 'कोई बात नहीं! अगर कुछ और चाहिए तो बताएँ।',
        'default': 'मैं शिकायत दर्ज करने और ट्रैक करने में आपकी मदद कर सकता हूँ।'
    }
}

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    message = data.get('message', '').lower()
    lang = data.get('lang', 'en')
    
    responses = CHAT_RESPONSES.get(lang, CHAT_RESPONSES['en'])
    
    # Multilingual keyword patterns
    greet_keywords = ['hello', 'hi', 'hlo', 'hey', 'namaste', 'vanakkam', 'నమస్కారం', 'வணக்கம்', 'നമസ്കാരം', 'नमस्ते']
    thank_keywords = ['thank', 'thanks', 'tnx', 'thx', 'നന്ദി', 'ధన్యవాదాలు', 'நன்றி', 'धन्यवाद']
    ok_keywords = ['ok', 'okay', 'fine', 'alright', 'good', 'సరే', 'சரி', 'ശരി', 'ठीक', 'अच्छा']
    bye_keywords = ['bye', 'goodbye', 'see you', 'talk later', 'వెళ్తున్నాను', 'போகிறேன்', 'പോകുന്നു', 'जाता हूं']
    yes_keywords = ['yes', 'yeah', 'yep', 'sure', 'అవును', 'ஆம்', 'അതെ', 'हाँ', 'जी']
    no_keywords = ['no', 'nope', 'nah', 'కాదు', 'இல்லை', 'ഇല്ല', 'नहीं']
    
    # Check message against patterns
    if any(keyword in message for keyword in greet_keywords):
        reply = responses['greet']
    elif any(keyword in message for keyword in thank_keywords):
        reply = responses['welcome']
    elif any(keyword in message for keyword in ok_keywords):
        reply = responses['need_help']
    elif any(keyword in message for keyword in bye_keywords):
        reply = responses['bye']
    elif any(keyword in message for keyword in yes_keywords):
        reply = responses['yes']
    elif any(keyword in message for keyword in no_keywords):
        reply = responses['no']
    elif 'track' in message or 'status' in message or 'tracking' in message:
        reply = responses['track']
    elif 'file' in message or 'submit' in message or 'complaint' in message or 'grievance' in message:
        reply = responses['file']
    else:
        reply = responses['default']
        
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)

