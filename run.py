#.\venv\Scripts\Activate.ps1
from app import create_app, db
# 'Post' has been removed from this import
from app.models import User, Donation, NGO

# Create the Flask app instance
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Makes these items available in the 'flask shell' command
    for easy testing in the terminal.
    """
    # 'Post' has been removed from this dictionary
    return {
        'db': db,
        'User': User,
        'Donation': Donation,
        'NGO': NGO
    }

if __name__ == '__main__':
    # Runs the application
    # debug=True automatically reloads the server when you save a file
    # We set host='0.0.0.0' to make it accessible, but this is optional.
    app.run(debug=True, host='0.0.0.0', port=5000)