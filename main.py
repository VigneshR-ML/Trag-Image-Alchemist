import os
import logging
import uuid
import stripe
import shutil
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, storage
from google.cloud import storage as gcs
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
    apply_filter,
    auto_adjust
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
CORS(app)

# Define paths for local storage as fallback
UPLOAD_FOLDER = '/tmp/uploads'
PUBLIC_FOLDER = os.path.join('static', 'uploads')
PUBLIC_URL_PREFIX = '/static/uploads/'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PUBLIC_FOLDER, exist_ok=True)

# Configure file upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Configure GCS settings
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'trag-image-alchemist.firebasestorage.app')  # <-- match your Firebase bucket
use_gcs = True  # Set this to False to force local storage

# Initialize Firebase Admin SDK with service account
try:
    cred = credentials.Certificate('firebase-config.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': BUCKET_NAME
    })
    storage_client = gcs.Client.from_service_account_json('firebase-config.json')
    bucket = storage_client.bucket(BUCKET_NAME)
    logging.info("Successfully initialized GCS with service account")
except Exception as e:
    logging.error(f"Failed to initialize GCS: {str(e)}")
    use_gcs = False

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(original_filename):
    """Generate a unique filename while preserving extension"""
    if not original_filename:
        return f"{uuid.uuid4()}.jpg"
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    return f"{uuid.uuid4()}.{ext}"

# Storage operation functions with fallback
def store_file(file_obj, destination_filename=None):
    """Store file using GCS or local filesystem with fallback"""
    if not file_obj:
        raise ValueError("No file provided")
        
    # Generate unique filename if not provided
    if not destination_filename:
        destination_filename = generate_filename(file_obj.filename)
        
    # Save locally first (needed for upload)
    local_path = os.path.join(UPLOAD_FOLDER, destination_filename)
    file_obj.save(local_path)
    
    # Always upload to GCS if available
    try:
        gcs_path = f'uploads/{destination_filename}'
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        blob.make_public()
        url = f'https://storage.googleapis.com/{BUCKET_NAME}/{gcs_path}'
        os.remove(local_path)
        return {'path': gcs_path, 'url': url, 'storage': 'gcs'}
    except Exception as e:
        logging.error(f"GCS upload failed: {str(e)}")
        raise RuntimeError("Failed to upload to Firebase Storage")

def retrieve_file(file_path, output_path):
    """Retrieve file from GCS only"""
    if not file_path:
        raise ValueError("No file path provided")
    if file_path.startswith('uploads/'):
        try:
            blob = bucket.blob(file_path)
            blob.download_to_filename(output_path)
            return True
        except Exception as e:
            logging.error(f"Error retrieving from GCS: {str(e)}")
            return False
    else:
        logging.error("Only GCS storage is supported for retrieval.")
        return False

def delete_file(file_path):
    """Delete file from GCS only"""
    if not file_path:
        return
    if file_path.startswith('uploads/'):
        try:
            blob = bucket.blob(file_path)
            blob.delete()
        except Exception as e:
            logging.error(f"Error deleting from GCS: {str(e)}")
    else:
        logging.error("Only GCS storage is supported for deletion.")

def process_and_store(input_path, operation, params=None):
    """Process image and store the result"""
    if params is None:
        params = {}
        
    # Generate output filename
    output_filename = generate_filename(os.path.basename(input_path))
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    # Process the image
    if operation == 'remove_background':
        background_color = params.get('color', None)
        remove_background(input_path, output_path, background_color)
    elif operation == 'enhance':
        enhance_image_quality(input_path, output_path)
    elif operation == 'auto_adjust':
        auto_adjust(input_path, output_path)
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
        raise ValueError(f"Unknown operation: {operation}")
        
    # Always upload processed image to GCS
    try:
        gcs_path = f'uploads/{output_filename}'
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(output_path)
        blob.make_public()
        url = f'https://storage.googleapis.com/{BUCKET_NAME}/{gcs_path}'
        os.remove(output_path)  # Clean up local file
        return {'path': gcs_path, 'url': url, 'storage': 'gcs'}
    except Exception as e:
        logging.error(f"GCS upload failed: {str(e)}")
        raise RuntimeError("Failed to upload processed image to Firebase Storage")

# Routes
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
        try:
            # Store the file (either GCS or local fallback)
            result = store_file(file)
            
            # Store file paths in session
            session['original_image'] = result['path']
            session['current_image'] = result['path']
            session['storage_type'] = result['storage']
            
            return jsonify({
                'success': True,
                'filename': os.path.basename(result['path']),
                'url': result['url']
            })
            
        except Exception as e:
            logging.error(f"Error in file upload: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
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
        
        # Download current image to temp location
        current_path = session['current_image']
        temp_input = os.path.join(UPLOAD_FOLDER, f'input_{os.path.basename(current_path)}')
        
        if not retrieve_file(current_path, temp_input):
            return jsonify({'error': 'Could not retrieve the image'}), 500
        
        # Process the image and store the result
        result = process_and_store(temp_input, operation, params)
        
        # Update session with new image path
        session['current_image'] = result['path']
        session['storage_type'] = result['storage']
        
        # Clean up temp file
        if os.path.exists(temp_input):
            os.remove(temp_input)
        
        return jsonify({
            'success': True,
            'url': result['url']
        })
    
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_image():
    if 'original_image' in session and 'current_image' in session:
        original_path = session['original_image']
        # Always use GCS URL
        url = f'https://storage.googleapis.com/{BUCKET_NAME}/{original_path}'
        session['current_image'] = original_path
        session['storage_type'] = 'gcs'
        return jsonify({
            'success': True,
            'url': url
        })
    return jsonify({'error': 'No original image found'}), 400

@app.route('/download', methods=['GET'])
def download_image():
    if 'current_image' not in session:
        return jsonify({'error': 'No image to download'}), 400
    current_path = session['current_image']
    url = f'https://storage.googleapis.com/{BUCKET_NAME}/{current_path}'
    return jsonify({
        'success': True,
        'url': url
    })

@app.route('/static/uploads/<filename>')
def serve_upload(filename):
    """Serve files from the uploads directory"""
    return send_from_directory(PUBLIC_FOLDER, filename)

@app.route('/health')
def health_check():
    storage_status = "GCS" if use_gcs else "Local Storage"
    return jsonify({
        "status": "healthy",
        "storage": storage_status
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    app.run(host=host, port=port, debug=True)