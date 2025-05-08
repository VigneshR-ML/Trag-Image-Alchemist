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
        save_image_with_format_compatibility(background, output_path)
    else:
        # Save with transparent background
        save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

def adjust_hue(input_path, output_path, shift):
    """
    Adjust image hue
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
        shift: Hue shift in degrees (0-360)
    """
    # Load the image with PIL first to check format
    pil_img = Image.open(input_path)
    has_alpha = 'A' in pil_img.mode
    
    # OpenCV works better for hue adjustment
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED if has_alpha else cv2.IMREAD_COLOR)
    
    if has_alpha:
        # Split into BGR and Alpha
        bgr = img[:, :, :3]
        alpha = img[:, :, 3]
        
        # Convert BGR to HSV
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        
        # Shift the hue
        shift_float = float(shift)
        hsv[:, :, 0] = (hsv[:, :, 0] + shift_float) % 180
        
        # Convert back to BGR
        bgr_adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Merge back with alpha
        img_adjusted = cv2.merge([bgr_adjusted[:, :, 0], 
                                  bgr_adjusted[:, :, 1], 
                                  bgr_adjusted[:, :, 2], 
                                  alpha])
        
        # Save with PIL to preserve alpha
        pil_output = Image.fromarray(cv2.cvtColor(img_adjusted, cv2.COLOR_BGRA2RGBA))
        save_image_with_format_compatibility(pil_output, output_path)
    else:
        # For non-alpha images, use the original approach
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Shift the hue
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
    # Load the image with PIL first to check format
    pil_img = Image.open(input_path)
    has_alpha = 'A' in pil_img.mode
    
    # Use OpenCV for vibrance
    if has_alpha:
        # Load with alpha channel
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        # Split channels
        b, g, r, a = cv2.split(img)
        bgr = cv2.merge([b, g, r])
        
        # Process only BGR channels
        img_hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Apply vibrance adjustment
        factor_float = float(factor) - 1.0
        if factor_float != 0:
            mask = (255 - img_hsv[:, :, 1]) / 255.0
            img_hsv[:, :, 1] += mask * img_hsv[:, :, 1] * factor_float
            
        # Clip values to valid range
        img_hsv[:, :, 1] = np.clip(img_hsv[:, :, 1], 0, 255)
        
        # Convert back to BGR
        bgr_result = cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # Merge back with alpha
        img_result = cv2.merge([bgr_result[:, :, 0], 
                               bgr_result[:, :, 1], 
                               bgr_result[:, :, 2], 
                               a])
        
        # Save with PIL to preserve alpha
        pil_output = Image.fromarray(cv2.cvtColor(img_result, cv2.COLOR_BGRA2RGBA))
        save_image_with_format_compatibility(pil_output, output_path)
    else:
        # Non-alpha processing
        img = cv2.imread(input_path)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Apply vibrance adjustment
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
    
    # Ensure quality is within valid range
    quality_val = max(1, min(int(quality), 95))
    
    save_image_with_format_compatibility(img, output_path, quality=quality_val)

def apply_black_white(input_path, output_path):
    """
    Convert image to black and white
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
    """
    img = Image.open(input_path)
    has_alpha = 'A' in img.mode
    
    if has_alpha:
        # Extract alpha channel
        alpha = img.split()[3]
        
        # Convert to grayscale
        gray = img.convert('L')
        
        # Create new RGBA image
        result = Image.new('RGBA', img.size)
        
        # Fill RGB channels with grayscale
        for i in range(3):
            result.paste(gray, (0, 0), gray)
        
        # Add alpha channel back
        result.putalpha(alpha)
    else:
        # Simple grayscale conversion
        result = img.convert('L')
    
    save_image_with_format_compatibility(result, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

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
    
    save_image_with_format_compatibility(img, output_path)

def save_image_with_format_compatibility(img, output_path, quality=95):
    """
    Save image with format compatibility handling.
    Converts RGBA to RGB if saving as JPEG.
    
    Args:
        img: PIL Image object
        output_path: Path to save the image
        quality: Quality for lossy formats (0-100)
    """
    try:
        ext = os.path.splitext(output_path)[1].lower()
        
        # Make a copy to avoid modifying the original
        img_copy = img.copy()
        
        if ext in ['.jpg', '.jpeg']:
            # Handle RGBA to RGB conversion for JPEG
            if img_copy.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', img_copy.size, (255, 255, 255))
                # Paste the image with alpha as mask
                background.paste(img_copy, mask=img_copy.split()[3])
                # Save the result
                background.save(output_path, format='JPEG', quality=quality, optimize=True)
            else:
                # Ensure RGB mode for JPEG
                img_copy = img_copy.convert('RGB')
                img_copy.save(output_path, format='JPEG', quality=quality, optimize=True)
                
        elif ext == '.png':
            # PNG supports all color modes
            img_copy.save(output_path, format='PNG', optimize=True)
            
        elif ext == '.webp':
            # WebP supports both RGB and RGBA
            img_copy.save(output_path, format='WEBP', quality=quality)
            
        elif ext == '.gif':
            # GIF with potential palette optimizations
            if img_copy.mode not in ['P', 'RGB', 'RGBA']:
                img_copy = img_copy.convert('RGBA')
            img_copy.save(output_path, format='GIF')
            
        else:
            # Default fallback
            if img_copy.mode == 'RGBA':
                img_copy.save(output_path + '.png', format='PNG')
            else:
                img_copy = img_copy.convert('RGB')
                img_copy.save(output_path + '.jpg', format='JPEG', quality=quality, optimize=True)
                
    except Exception as e:
        # If there's any error, try a more aggressive approach
        try:
            # Force convert to RGB and save as JPEG
            img_rgb = img.convert('RGB')
            img_rgb.save(output_path, format='JPEG', quality=quality)
        except Exception as e2:
            # If still failing, attempt to save with a new name as PNG
            try:
                new_path = os.path.splitext(output_path)[0] + "_fallback.png"
                img.save(new_path, format='PNG')
                # If successful, rename the file to the original intended name
                import shutil
                shutil.move(new_path, output_path)
            except Exception as e3:
                # If all else fails, raise the original error
                raise e
    
def get_appropriate_extension(operation, input_path=None):
    """
    Determine the appropriate extension based on the operation
    
    Args:
        operation: The image operation to be performed
        input_path: Original image path
        
    Returns:
        String with appropriate extension (without dot) or None
    """
    # Operations that should always use PNG for transparency
    if operation in ['remove_background']:
        return 'png'
    
    # Check if input path has an extension we should preserve
    if input_path:
        ext = os.path.splitext(input_path)[1].lower()
        if ext:
            return ext[1:]  # Remove the dot
    
    # Default to none (use original or fallback)
    return None