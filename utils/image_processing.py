import io
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageColor
import rembg
import os

def remove_background(input_image, output_path, bg_color=None):
    """
    Remove background from an image and optionally replace with a color.
    
    Args:
        input_image: Path to input image or PIL Image object
        output_path: Path to save output image
        bg_color: Background color (hex string, color name, or RGB tuple), or None/'transparent' for transparent
    """
    # Accept both file path and PIL Image
    if isinstance(input_image, Image.Image):
        with io.BytesIO() as buf:
            input_image.save(buf, format='PNG')
            img_data = buf.getvalue()
    else:
        with open(input_image, 'rb') as f:
            img_data = f.read()
    
    # Remove background with rembg
    output_data = rembg.remove(img_data)
    img = Image.open(io.BytesIO(output_data)).convert("RGBA")
    
    # If a background color is specified and it's not "transparent", apply it
    if bg_color and str(bg_color).lower() != "transparent":
        # Parse color (accepts hex, color name, or tuple)
        try:
            if isinstance(bg_color, tuple):
                color = bg_color
            else:
                color = ImageColor.getrgb(bg_color)
        except Exception:
            color = (255, 255, 255, 255)  # fallback to white
        
        # If color is RGB, add alpha
        if len(color) == 3:
            color = (*color, 255)
        background = Image.new("RGBA", img.size, color)
        background.paste(img, (0, 0), img)
        background.save(output_path)
    else:
        # Save with transparent background
        img.save(output_path)

def enhance_image_quality(input_path, output_path):
    """
    Enhance image quality without changing colors or lighting
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
    """
    img = Image.open(input_path)
    original_mode = img.mode

    if original_mode == 'RGBA':
        # Handle RGBA images
        r, g, b, a = img.split()
        rgb_img = Image.merge('RGB', (r, g, b))
        
        # Apply only sharpening for quality enhancement
        rgb_img = rgb_img.filter(ImageFilter.SHARPEN)
        rgb_img = ImageEnhance.Sharpness(rgb_img).enhance(1.3)
        
        # Split and merge back with alpha
        r, g, b = rgb_img.split()
        img = Image.merge('RGBA', (r, g, b, a))
    else:
        # Apply quality enhancement
        img = img.filter(ImageFilter.SHARPEN)
        img = ImageEnhance.Sharpness(img).enhance(1.3)
    
    # Handle format conversion if needed
    ext = os.path.splitext(output_path)[1].lower()
    if original_mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    
    # Save with maximum quality
    if ext in ('.jpg', '.jpeg'):
        img.save(output_path, quality=95, optimize=True)
    else:
        img.save(output_path)

def auto_adjust(input_path, output_path):
    """
    Automatically adjust image settings
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
    """
    img = Image.open(input_path)
    original_mode = img.mode

    if original_mode == 'RGBA':
        # Handle RGBA images
        r, g, b, a = img.split()
        rgb_img = Image.merge('RGB', (r, g, b))
        
        # Apply auto adjustments
        rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.2)
        rgb_img = ImageEnhance.Brightness(rgb_img).enhance(1.1)
        rgb_img = ImageEnhance.Color(rgb_img).enhance(1.2)
        
        # Split and merge back with alpha
        r, g, b = rgb_img.split()
        img = Image.merge('RGBA', (r, g, b, a))
    else:
        # Apply auto adjustments
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Brightness(img).enhance(1.1)
        img = ImageEnhance.Color(img).enhance(1.2)
    
    # Handle format conversion if needed
    ext = os.path.splitext(output_path)[1].lower()
    if original_mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    
    img.save(output_path)

def resize_image(input_path, output_path, width, height):
    """
    Resize image to specified dimensions
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        width: Target width
        height: Target height
    """
    img = Image.open(input_path)
    img = img.resize((int(width), int(height)), Image.LANCZOS)
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def rotate_image(input_path, output_path, angle):
    """
    Rotate image by specified angle
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        angle: Rotation angle in degrees
    """
    img = Image.open(input_path)
    img = img.rotate(-float(angle), expand=True, resample=Image.BICUBIC)
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def flip_image(input_path, output_path, direction):
    """
    Flip image horizontally or vertically
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        direction: 'horizontal' or 'vertical'
    """
    img = Image.open(input_path)
    
    if direction == 'horizontal':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif direction == 'vertical':
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def adjust_brightness(input_path, output_path, factor):
    """
    Adjust image brightness
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        factor: Brightness factor (1.0 is original, < 1.0 darkens, > 1.0 brightens)
    """
    img = Image.open(input_path)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(float(factor))
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def adjust_contrast(input_path, output_path, factor):
    """
    Adjust image contrast
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        factor: Contrast factor (1.0 is original, < 1.0 decreases, > 1.0 increases)
    """
    img = Image.open(input_path)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(float(factor))
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def adjust_saturation(input_path, output_path, factor):
    """
    Adjust image saturation
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        factor: Saturation factor (1.0 is original, < 1.0 decreases, > 1.0 increases)
    """
    img = Image.open(input_path)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(float(factor))
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def adjust_hue(input_path, output_path, shift):
    """
    Adjust image hue
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        shift: Hue shift in degrees (0-360)
    """
    # OpenCV works better for hue adjustment
    img = cv2.imread(input_path)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Shift the hue
    shift_float = float(shift)
    img_hsv[:, :, 0] = (img_hsv[:, :, 0] + shift_float) % 180
    
    # Convert back to BGR and save
    img_result = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, img_result)

def adjust_vibrance(input_path, output_path, factor):
    """
    Adjust image vibrance - increases saturation more on less saturated colors
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        factor: Vibrance factor (1.0 is original, < 1.0 decreases, > 1.0 increases)
    """
    # Use OpenCV for vibrance
    img = cv2.imread(input_path)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    
    # Calculate average saturation
    avg_sat = np.mean(img_hsv[:, :, 1])
    
    # Apply vibrance adjustment (boost less saturated pixels more)
    factor_float = float(factor) - 1.0
    if factor_float != 0:
        mask = (255 - img_hsv[:, :, 1]) / 255.0
        img_hsv[:, :, 1] += mask * img_hsv[:, :, 1] * factor_float
        
    # Clip values to valid range
    img_hsv[:, :, 1] = np.clip(img_hsv[:, :, 1], 0, 255)
    
    # Convert back to BGR and save
    img_result = cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, img_result)

def compress_image(input_path, output_path, quality):
    """
    Compress image with specified quality

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        quality: JPEG quality (0-100)
    """
    img = Image.open(input_path)
    ext = os.path.splitext(output_path)[1].lower()

    if ext in ('.jpg', '.jpeg'):
        # JPEG doesn't support transparency, convert if needed
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        # Use optimize and progressive for better compression
        img.save(
            output_path,
            format='JPEG',
            quality=max(1, min(int(quality), 95)),  # Clamp to 1-95
            optimize=True,
            progressive=True
        )
    elif ext == '.png':
        # For PNG, quantize if possible for smaller size, then optimize
        if img.mode in ('RGBA', 'RGB'):
            # Quantize to 256 colors if not already palette
            img_quant = img.convert('P', palette=Image.ADAPTIVE, colors=256)
            img_quant.save(output_path, format='PNG', optimize=True)
        else:
            img.save(output_path, format='PNG', optimize=True)
    else:
        # Default fallback - handle transparency for other formats
        if img.mode == 'RGBA' and ext not in ('.png', '.tiff', '.webp'):
            img = img.convert('RGB')
        img.save(output_path, quality=int(quality))

def apply_black_white(input_path, output_path):
    """
    Convert image to black and white
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
    """
    img = Image.open(input_path)
    
    # Convert to grayscale
    img = img.convert('L')
    
    # Convert back to RGB for consistent handling
    img = img.convert('RGB')
    
    # Determine if output should be PNG based on extension
    ext = os.path.splitext(output_path)[1].lower()
    if ext == '.png' and 'A' in Image.open(input_path).mode:
        # If input had alpha and output is PNG, we need to preserve alpha
        original = Image.open(input_path)
        if original.mode == 'RGBA':
            r, g, b, a = original.split()
            img.putalpha(a)
    
    img.save(output_path)

def apply_blur(input_path, output_path, amount=5):
    """
    Apply blur effect to image
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        amount: Blur radius (higher = more blur)
    """
    img = Image.open(input_path)
    
    # Preserve alpha channel if present
    has_alpha = 'A' in img.mode
    
    # Apply Gaussian blur
    if has_alpha:
        # Process RGB and A channels separately
        r, g, b, a = img.split()
        rgb = Image.merge('RGB', (r, g, b))
        
        # Apply blur to RGB channels
        blurred_rgb = rgb.filter(ImageFilter.GaussianBlur(radius=float(amount)))
        
        # Recombine with alpha
        r, g, b = blurred_rgb.split()
        img = Image.merge('RGBA', (r, g, b, a))
    else:
        img = img.filter(ImageFilter.GaussianBlur(radius=float(amount)))
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def apply_sharpen(input_path, output_path, amount=1.5):
    """
    Apply sharpening effect to image
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        amount: Sharpening factor (higher = more sharp)
    """
    img = Image.open(input_path)
    
    # Preserve alpha channel if present
    has_alpha = 'A' in img.mode
    
    if has_alpha:
        # Process RGB and A channels separately
        r, g, b, a = img.split()
        rgb = Image.merge('RGB', (r, g, b))
        
        # Apply sharpening filter
        enhancer = ImageEnhance.Sharpness(rgb)
        sharpened_rgb = enhancer.enhance(float(amount))
        
        # Recombine with alpha
        r, g, b = sharpened_rgb.split()
        img = Image.merge('RGBA', (r, g, b, a))
    else:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(float(amount))
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)

def apply_filter(input_path, output_path, filter_type, intensity=100):
    """
    Apply various filter effects to image with intensity control
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        filter_type: Type of filter to apply
        intensity: Filter intensity (0-100)
    """
    img = Image.open(input_path)
    
    # Preserve alpha channel if present
    has_alpha = 'A' in img.mode
    alpha = None
    if has_alpha:
        alpha = img.split()[3]
    
    # Convert to RGB for consistent processing
    img = img.convert('RGB')
    
    # Calculate blend factor from intensity (0-100)
    # Reverse the blend calculation so higher intensity means stronger filter
    blend = 1 - ((100 - intensity) / 100.0)  # New calculation

    # Define filter matrices (3x4 matrices = 12 elements each)
    filter_matrices = {
        'sepia': [
            0.393, 0.769, 0.189, 0,
            0.349, 0.686, 0.168, 0,
            0.272, 0.534, 0.131, 0
        ],
        'cool': [
            0.8, 0.1, 0.1, 0,
            0.1, 0.9, 0.1, 0,
            0.1, 0.1, 1.2, 0
        ],
        'warm': [
            1.2, 0.1, 0.1, 0,
            0.1, 1.0, 0.1, 0,
            0.1, 0.1, 0.7, 0
        ],
        'vintage': [
            0.9, 0.5, 0.1, 0,
            0.3, 0.8, 0.1, 0,
            0.2, 0.3, 0.7, 0
        ],
        'dramatic': [
            1.5, -0.2, -0.2, 0,
            -0.2, 1.5, -0.2, 0,
            -0.2, -0.2, 1.5, 0
        ],
        'cinema': [
            1.1, -0.1, 0.1, 0,
            0.0, 1.1, 0.1, 0,
            -0.1, 0.1, 1.0, 0
        ],
        'chrome': [
            1.2, -0.1, -0.1, 0,
            -0.1, 1.2, -0.1, 0,
            -0.1, -0.1, 1.2, 0
        ],
        'fade': [
            0.95, 0.05, 0.05, 0.1,
            0.05, 0.95, 0.05, 0.1,
            0.05, 0.05, 0.95, 0.1
        ]
    }

    if filter_type in filter_matrices:
        # Get the filter matrix
        filter_matrix = filter_matrices[filter_type]
        
        # Identity matrix for blending
        identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]
        
        # Blend between identity and filter matrix
        matrix = [
            (f * blend + i * (1 - blend))
            for f, i in zip(filter_matrix, identity)
        ]
        
        # Apply the blended matrix
        img = img.convert('RGB', matrix)
    
    elif filter_type == 'grayscale':
        # Special handling for grayscale
        gray = img.convert('L')
        if blend < 1:
            img = Image.blend(img, gray.convert('RGB'), blend)
        else:
            img = gray.convert('RGB')
    
    elif filter_type == 'invert':
        # Special handling for invert
        inv = ImageOps.invert(img)
        if blend < 1:
            img = Image.blend(img, inv, blend)
        else:
            img = inv

    elif filter_type == 'high_contrast':
        # High contrast with blend
        enhancer = ImageEnhance.Contrast(img)
        contrast_img = enhancer.enhance(2.0)
        if blend < 1:
            img = Image.blend(img, contrast_img, blend)
        else:
            img = contrast_img

    # Reapply alpha channel if needed
    if has_alpha and alpha is not None:
        r, g, b = img.split()
        img = Image.merge('RGBA', (r, g, b, alpha))
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    img.save(output_path)
