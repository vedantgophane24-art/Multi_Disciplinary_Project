from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Optional, NumberRange
from app.models import User

# --- New Imports for File Uploads ---
from flask_wtf.file import FileField, FileAllowed, FileSize
# ------------------------------------


class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Form for new user registration."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class DonationForm(FlaskForm):
    """Form for logging a new donation (clothes or money)."""
    
    # Dropdown for donation type
    donation_type = SelectField('Donation Type', 
        choices=[
            ('Clothes', 'Clothes'),
            ('Money', 'Money'),
            ('Other', 'Other')
        ], 
        validators=[DataRequired()],
        # ID for our JavaScript to find
        id='donation_type_select'
    )

    # Dropdown for NGO
    ngo_id = SelectField('Collection Center', 
        validators=[DataRequired(message="Please select a center.")],
        coerce=int # Store the choice as an integer (the NGO's ID)
    )

    # --- Clothes-specific fields ---
    estimated_weight_kg = DecimalField('Estimated Weight (kg)', 
        validators=[Optional()], # No longer required
        places=2,
        description="Enter the total weight of your donation."
    )
    
    # --- Money-specific fields ---
    amount = DecimalField('Amount', 
        validators=[Optional(), NumberRange(min=0)], 
        places=2,
        description="Enter the amount you donated."
    )
    currency = SelectField('Currency', 
        choices=[
            ('INR', 'INR (Indian Rupee)'),
            ('USD', 'USD (US Dollar)'),
            ('EUR', 'EUR (Euro)'),
            ('GBP', 'GBP (British Pound)'),
            ('JPY', 'JPY (Japanese Yen)'),
            ('CAD', 'CAD (Canadian Dollar)'),
            ('AUD', 'AUD (Australian Dollar)'),
            ('CHF', 'CHF (Swiss Franc)'),
            ('SGD', 'SGD (Singapore Dollar)'),
            ('NZD', 'NZD (New Zealand Dollar)'),
        ], 
        validators=[Optional()]
    )
    
    # --- NEW IMAGE UPLOAD FIELD ---
    image = FileField('Upload Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed!'),
        FileSize(max_size=5 * 1024 * 1024, message='File must be 5MB or less.') # 5MB max size
    ])
    # ----------------------------------

    # --- Shared fields ---
    description = TextAreaField('Description', 
        validators=[Optional()]
    )
    submit = SubmitField('Log My Donation')