import os
import base64
import time 
import requests 
from flask import render_template, flash, redirect, url_for, request, Blueprint, current_app, send_from_directory
from app import db
from app.models import User, Donation, NGO
from app.forms import LoginForm, RegistrationForm, DonationForm
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from sqlalchemy import desc
from werkzeug.utils import secure_filename 
from datetime import datetime 

bp = Blueprint('main', __name__)

# --- NEW HELPER FUNCTION FOR AI ---
def get_ai_grade(image_path):
    """
    Sends an image to the Gemini API and returns its grade.
    """
    # 1. Read image and encode to base64
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading image: {e}")
        return "N/A" # Return "Not Available" if image can't be read

    # 2. Set up the API call
    # IMPORTANT: Do not put your real API key here.
    # We leave it blank, and the environment will provide it.
    api_key = "" 
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # This is the prompt we send to the AI
    system_prompt = "You are a clothing grader for a recycling charity. Analyze the image and classify it into one of two categories. Respond with ONLY the text 'Grade A' or 'Grade B/C'."
    user_prompt = "Grade this clothing based on its condition. 'Grade A' means like-new, wearable, no stains, and no holes. 'Grade B/C' means visibly worn, stained, torn, or only good for recycling."

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg", # We'll assume jpeg/png
                            "data": image_data
                        }
                    }
                ]
            }
        ]
    }

    # 3. Make the API request
    try:
        # We use exponential backoff (retries) for reliability
        for n in range(3): # Try up to 3 times
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                grade = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'N/A').strip()
                # Clean up the response, just in case
                if "Grade A" in grade:
                    return "Grade A"
                elif "Grade B/C" in grade:
                    return "Grade B/C"
                else:
                    return "N/A" # AI gave an unexpected answer
            
            # Simple exponential backoff
            time.sleep((2 ** n)) 
            
        print(f"API Error after retries: {response.status_code} {response.text}")
        return "N/A" # Failed after retries

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "N/A"


@bp.route('/')
@bp.route('/index')
def index():
    """Home page."""
    total_diverted = db.session.query(db.func.sum(Donation.estimated_weight_kg)).scalar() or 0.0
    return render_template('index.html',
                           title='Home',
                           total_diverted=total_diverted)

# --- THIS IS THE UPDATED DONATE ROUTE ---
@bp.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    """Donation page (clothes and money) with AI image grading."""
    form = DonationForm()
    form.ngo_id.choices = [(ngo.id, ngo.name) for ngo in NGO.query.order_by(NGO.name).all()]
    
    if form.validate_on_submit():
        donation_type = form.donation_type.data
        
        # --- Initialize AI-related variables ---
        saved_filename = None
        ai_grade = None

        if donation_type == 'Money':
            donation = Donation(
                donation_type=donation_type,
                amount=float(form.amount.data),
                currency=form.currency.data,
                description=form.description.data,
                user_id=current_user.id,
                ngo_id=form.ngo_id.data
                # image_filename and grade remain NULL
            )
            db.session.add(donation)
            
        else: # This handles 'Clothes' and 'Other'
            
            # --- NEW IMAGE HANDLING LOGIC ---
            image_file = form.image.data
            if image_file:
                # 1. Save the file
                filename = secure_filename(image_file.filename)
                # Ensure unique filename to avoid overwrites
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                try:
                    image_file.save(save_path)
                    saved_filename = unique_filename
                    
                    # 2. Call the AI for grading
                    flash('Image uploaded! Analyzing grade...')
                    ai_grade = get_ai_grade(save_path)
                    flash(f'AI has graded your donation: {ai_grade}')

                except Exception as e:
                    print(f"Error saving file: {e}")
                    flash('There was an error saving your image.', 'error')
            # --- END OF IMAGE LOGLOGIC ---

            donation = Donation(
                donation_type=donation_type,
                estimated_weight_kg=float(form.estimated_weight_kg.data),
                description=form.description.data,
                user_id=current_user.id,
                ngo_id=form.ngo_id.data,
                image_filename=saved_filename, # Save the filename
                grade=ai_grade                  # Save the AI's grade
            )
            
            user = User.query.get(current_user.id)
            user.total_waste_diverted_kg = (user.total_waste_diverted_kg or 0.0) + float(form.estimated_weight_kg.data)
            
            db.session.add(donation)
            db.session.add(user)

        db.session.commit()
        
        flash('Thank you for your donation! It has been logged.')
        return redirect(url_for('main.profile'))
    
    return render_template('donate.html', title='Donate', form=form)
# --- END OF UPDATED DONATE ROUTE ---


@bp.route('/find_ngo')
def find_ngo():
    """Page to find nearby NGOs/centers in Chennai."""
    ngos = NGO.query.all()
    return render_template('find_ngo.html', title='Find Centers', ngos=ngos)

@bp.route('/leaderboard')
def leaderboard():
    """Top donators page."""
    
    # Query for Top Waste Donators (by kg)
    top_waste_donators = User.query.order_by(User.total_waste_diverted_kg.desc()).limit(10).all()
    
    # Query for Top Money Donators
    top_money_donators = db.session.query(
        User.username,
        db.func.sum(Donation.amount).label('total_donated')
    ).join(Donation, User.id == Donation.user_id)\
     .filter(Donation.donation_type == 'Money')\
     .group_by(User.username)\
     .order_by(desc('total_donated'))\
     .limit(10).all()

    return render_template('leaderboard.html', 
                           title='Top Donators', 
                           top_waste_donators=top_waste_donators,
                           top_money_donators=top_money_donators)

@bp.route('/articles')
def articles():
    """Static page for articles and resources."""
    return render_template('articles.html', title='Articles')

@bp.route('/recycling-process')
def recycling_process():
    """Page detailing the textile recycling process."""
    return render_template('recycling_process.html', title='Recycling Process')

@bp.route('/events')
def events():
    """Future events page."""
    return render_template('events.html', title='Future Events')

@bp.route('/profile')
@login_required
def profile():
    """User profile page showing their stats."""
    user_donations = current_user.donations.order_by(Donation.timestamp.desc()).all()
    return render_template('profile.html', title='My Profile', donations=user_donations)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
        
    return render_template('register.html', title='Register', form=form)


# --- THIS IS THE NEW ROUTE TO SERVE IMAGES ---
@bp.route('/uploads/<path:filename>')
@login_required
def get_uploaded_file(filename):
    """Serves uploaded files from the UPLOAD_FOLDER."""
    # This securely sends the file from the folder specified in your config
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return "File not found.", 404