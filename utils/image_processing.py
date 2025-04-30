import io
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import rembg
import os

def remove_background(input_path, output_path, bg_color=None):
    """
    Remove background from an image and optionally replace with a color
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        bg_color: Background color in hex format (e.g., '#FF0000') or None/transparent for transparent
    """
    with open(input_path, 'rb') as f:
        img_data = f.read()
    
    # Remove background with rembg
    output_data = rembg.remove(img_data)
    
    # If a background color is specified and it's not "transparent", apply it
    if bg_color and bg_color.lower() != "transparent":
        img = Image.open(io.BytesIO(output_data)).convert("RGBA")
        background = Image.new("RGBA", img.size, bg_color)
        background.paste(img, (0, 0), img)
        background.save(output_path)
    else:
        # Save with transparent background
        with open(output_path, 'wb') as f:
            f.write(output_data)

def enhance_image_quality(input_path, output_path):
    """
    Enhance image quality with a single click
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
    """
    img = Image.open(input_path)
    
    # Preserve the original mode
    original_mode = img.mode
    
    # Convert to RGB if needed for enhancements (but preserve RGBA if that's the original)
    if original_mode == 'RGBA':
        # For RGBA images, we need to separate the alpha channel
        r, g, b, a = img.split()
        rgb_img = Image.merge('RGB', (r, g, b))
        
        # Apply enhancements to the RGB channels
        rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.2)
        rgb_img = ImageEnhance.Brightness(rgb_img).enhance(1.1)
        rgb_img = ImageEnhance.Sharpness(rgb_img).enhance(1.5)
        rgb_img = ImageEnhance.Color(rgb_img).enhance(1.2)
        
        # Apply sharpening
        rgb_img = rgb_img.filter(ImageFilter.SHARPEN)
        
        # Split the enhanced RGB image
        r, g, b = rgb_img.split()
        
        # Merge back with the original alpha channel
        img = Image.merge('RGBA', (r, g, b, a))
    else:
        # For RGB or other modes, apply enhancements directly
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Brightness(img).enhance(1.1)
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        img = ImageEnhance.Color(img).enhance(1.2)
        img = img.filter(ImageFilter.SHARPEN)
    
    # Determine the format based on extension and transparency
    ext = os.path.splitext(output_path)[1].lower()
    if original_mode == 'RGBA' and ext == '.jpg':
        # If output should be jpg but image has transparency, convert to RGB
        img = img.convert('RGB')
    
    # Save with the appropriate format
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
    
    # Determine the output format based on the extension
    ext = os.path.splitext(output_path)[1].lower()
    
    if ext in ('.jpg', '.jpeg'):
        # JPEG doesn't support transparency, convert if needed
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(output_path, format='JPEG', quality=int(quality), optimize=True)
    elif ext == '.png':
        # For PNG, use optimize only
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

def apply_filter(input_path, output_path, filter_type):
    """
    Apply various filter effects to image
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        filter_type: Type of filter to apply ('sepia', 'vintage', 'cool', 'warm', etc.)
    """
    img = Image.open(input_path)
    
    # Preserve alpha channel if present
    has_alpha = 'A' in img.mode
    alpha = None
    
    if has_alpha:
        # Extract alpha channel
        alpha = img.split()[3]
    
    # Convert to RGB for consistent processing
    img = img.convert('RGB')
    
    if filter_type == 'sepia':
        # Apply sepia filter
        sepia_filter = (
            1.2, 0.87, 0.54,  # R
            0.66, 0.86, 0.47,  # G
            0.2, 0.43, 0.8   # B
        )
        img = img.convert('RGB', sepia_filter)
    
    elif filter_type == 'vintage':
        # Vintage effect (slight sepia + vignette)
        sepia_light = (
            1.1, 0.75, 0.39,  # R
            0.58, 0.9, 0.35,  # G
            0.18, 0.38, 0.85   # B
        )
        img = img.convert('RGB', sepia_light)
        
        # Add contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Add vignette
        width, height = img.size
        mask = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(mask)
        for i in range(15):
            box_x = int(width * i/30)
            box_y = int(height * i/30)
            box_w = width - 2 * box_x
            box_h = height - 2 * box_y
            draw.rectangle([(box_x, box_y), (box_x + box_w, box_y + box_h)], 
                           fill=255 - i * 8)
        img = Image.composite(img, Image.new('RGB', img.size, (60, 35, 20)), mask)
    
    elif filter_type == 'cool':
        # Cool temperature filter (blue tint)
        cool_filter = (
            0.8, 0.1, 0.1,  # R
            0.1, 0.9, 0.1,  # G
            0.1, 0.1, 1.2   # B
        )
        img = img.convert('RGB', cool_filter)
    
    elif filter_type == 'warm':
        # Warm temperature filter (yellow/red tint)
        warm_filter = (
            1.2, 0.1, 0.1,  # R
            0.1, 1.0, 0.1,  # G
            0.1, 0.1, 0.7   # B
        )
        img = img.convert('RGB', warm_filter)
    
    elif filter_type == 'grayscale':
        # Grayscale
        img = ImageOps.grayscale(img)
        img = img.convert('RGB')
    
    elif filter_type == 'high_contrast':
        # High contrast B&W
        img = ImageOps.grayscale(img)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        img = img.convert('RGB')
    
    # Reapply alpha channel if needed
    if has_alpha and alpha is not None:
        r, g, b = img.split()
        img = Image.merge('RGBA', (r, g, b, alpha))
    
    # Handle transparency for JPEG files
    ext = os.path.splitext(output_path)[1].lower()
    if img.mode == 'RGBA' and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    
    img.save(output_path)
