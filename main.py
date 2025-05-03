import os
import logging
import uuid
import stripe
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename
from utils.image_processing import (
    remove_background, 
    enhance_image_quality, 
    resize_image, 
    rotate_image, 
    flip_image,
    adjust_brightness, 
    adjust_contrast, 
    adjust_saturation, 
    adjust_hue,
    adjust_vibrance,
    compress_image,
    apply_black_white,
    apply_blur,
    apply_sharpen,
    apply_filter
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


port = int(os.environ.get("PORT", 8080))
host = "0.0.0.0"
# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
CORS(app)

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
logging.debug(f"Stripe configured with API key: {'*' * (len(os.environ.get('STRIPE_SECRET_KEY', '')) - 4) + os.environ.get('STRIPE_SECRET_KEY', '')[-4:] if os.environ.get('STRIPE_SECRET_KEY') else 'Not set'}")

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Make sure uploads directory has proper permissions
try:
    os.chmod(UPLOAD_FOLDER, 0o755)
except Exception as e:
    logging.warning(f"Could not set permissions on upload folder: {str(e)}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Clear upload folder on startup
try:
    for file in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    logging.info(f"Cleared upload folder: {UPLOAD_FOLDER}")
except Exception as e:
    logging.error(f"Error clearing upload folder: {str(e)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/editor')
def editor():
    return render_template('index.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/success')
def success():
    # Stripe checkout success page
    session_id = request.args.get('session_id')
    if session_id:
        logging.debug(f"Success with session ID: {session_id}")
        # In a production app, you'd verify the session and update user's subscription status
    return render_template('success.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # Get the domain
        domain_url = os.environ.get('REPLIT_DEV_DOMAIN', request.host_url.rstrip('/'))
        if not domain_url.startswith('http'):
            domain_url = f"http://{domain_url}"
        
        logging.debug(f"Domain URL: {domain_url}")
        
        # Map frontend price IDs to actual Stripe price IDs
        # In a production app, these would be stored in a database
        price_mapping = {
            'price_pro_monthly': os.environ.get('STRIPE_PRICE_PRO', 'price_1OCKZDCiJgPd76i1C0RFkRVN'),
            'price_enterprise_monthly': os.environ.get('STRIPE_PRICE_ENTERPRISE', 'price_1OCKZ7CiJgPd76i14tQfJY7v')
        }
        
        data = request.json
        price_id = data.get('priceId')
        
        # Map to actual Stripe price ID
        stripe_price_id = price_mapping.get(price_id)
        
        if not stripe_price_id:
            return jsonify({'error': 'Invalid price ID'}), 400
            
        # Create Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f"{domain_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain_url}/pricing",
            automatic_tax={'enabled': True},
        )
        
        return jsonify({'id': checkout_session.id})
    
    except Exception as e:
        logging.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Create a unique filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Store the filepath in the session
        session['original_image'] = filepath
        session['current_image'] = filepath
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'url': f'/static/uploads/{filename}'
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/process', methods=['POST'])
def process_image():
    try:
        data = request.json
        operation = data.get('operation')
        params = data.get('params', {})
        
        logging.debug(f"Processing image. Operation: {operation}, Params: {params}")
        
        if 'current_image' not in session:
            logging.error("No image in session to process")
            return jsonify({'error': 'No image to process'}), 400
        
        input_path = session['current_image']
        
        # Generate a new filename for the processed image
        # Always use .png for operations that may result in transparency
        input_ext = input_path.rsplit('.', 1)[1].lower()
        
        # Use PNG for operations that might result in transparency
        if operation == 'remove_background' or (input_ext in ['png'] and operation in ['enhance', 'rotate', 'flip']):
            output_filename = str(uuid.uuid4()) + '.png'
        else:
            output_filename = str(uuid.uuid4()) + '.' + input_ext
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Process image based on operation
        if operation == 'remove_background':
            background_color = params.get('color', None)
            logging.debug(f"Removing background with color: {background_color}")
            remove_background(input_path, output_path, background_color)
        
        elif operation == 'enhance':
            enhance_image_quality(input_path, output_path)
        
        elif operation == 'resize':
            width = params.get('width')
            height = params.get('height')
            resize_image(input_path, output_path, width, height)
        
        elif operation == 'rotate':
            angle = params.get('angle', 90)
            rotate_image(input_path, output_path, angle)
        
        elif operation == 'flip':
            direction = params.get('direction', 'horizontal')
            flip_image(input_path, output_path, direction)
        
        elif operation == 'brightness':
            factor = params.get('factor', 1.0)
            adjust_brightness(input_path, output_path, factor)
        
        elif operation == 'contrast':
            factor = params.get('factor', 1.0)
            adjust_contrast(input_path, output_path, factor)
        
        elif operation == 'saturation':
            factor = params.get('factor', 1.0)
            adjust_saturation(input_path, output_path, factor)
        
        elif operation == 'hue':
            factor = params.get('factor', 0)
            adjust_hue(input_path, output_path, factor)
        
        elif operation == 'vibrance':
            factor = params.get('factor', 1.0)
            adjust_vibrance(input_path, output_path, factor)
        
        elif operation == 'compress':
            quality = params.get('quality', 85)
            compress_image(input_path, output_path, quality)
            
        # Filter and effect operations
        elif operation == 'bw':
            apply_black_white(input_path, output_path)
            
        elif operation == 'blur':
            amount = params.get('amount', 5)
            apply_blur(input_path, output_path, amount)
            
        elif operation == 'sharpen':
            amount = params.get('amount', 1.5)
            apply_sharpen(input_path, output_path, amount)
            
        elif operation == 'filter':
            filter_type = params.get('type', 'none')
            intensity = int(params.get('intensity', 100))
            apply_filter(input_path, output_path, filter_type, intensity)
        
        else:
            return jsonify({'error': f'Unknown operation: {operation}'}), 400
        
        # Update the current image in the session
        session['current_image'] = output_path
        
        return jsonify({
            'success': True,
            'url': f'/static/uploads/{output_filename}'
        })
    
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_image():
    if 'original_image' in session and 'current_image' in session:
        session['current_image'] = session['original_image']
        return jsonify({
            'success': True,
            'url': session['original_image'].replace('static/', '/static/')
        })
    return jsonify({'error': 'No original image found'}), 400

@app.route('/download', methods=['GET'])
def download_image():
    if 'current_image' not in session:
        return jsonify({'error': 'No image to download'}), 400
    
    return jsonify({
        'success': True,
        'url': session['current_image'].replace('static/', '/static/')
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
