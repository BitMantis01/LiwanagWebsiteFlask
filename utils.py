from PIL import Image, ImageDraw, ImageFont
import io
import base64
import hashlib
import colorsys

def generate_avatar(username, size=64):
    """
    Generate a 64x64 circular avatar based on username
    """
    # Create a hash from username to get consistent colors
    username_hash = hashlib.md5(username.encode()).hexdigest()
    
    # Extract RGB values from hash
    r = int(username_hash[0:2], 16)
    g = int(username_hash[2:4], 16) 
    b = int(username_hash[4:6], 16)
    
    # Adjust colors to ensure good contrast and pleasant appearance
    # Convert to HSV for better color manipulation
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    # Ensure good saturation and value
    s = max(0.4, min(0.8, s))  # Saturation between 40-80%
    v = max(0.6, min(0.9, v))  # Value between 60-90%
    
    # Convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    background_color = (int(r*255), int(g*255), int(b*255))
    
    # Create image
    img = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Get initials (first letter of username)
    initials = username[0].upper() if username else '?'
    
    # Try to load a font, fallback to default if not available
    try:
        # You can customize the font path based on your system
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Calculate text color (white or dark based on background brightness)
    brightness = (background_color[0] * 299 + background_color[1] * 587 + background_color[2] * 114) / 1000
    text_color = (255, 255, 255) if brightness < 128 else (0, 0, 0)
    
    # Get text size and position
    if font:
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = size // 3
        text_height = size // 3
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    # Draw the initial
    draw.text((text_x, text_y), initials, fill=text_color, font=font)
    
    # Create circular mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size, size), fill=255)
    
    # Apply circular mask
    circular_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    circular_img.paste(img, (0, 0))
    circular_img.putalpha(mask)
    
    # Convert to base64
    buffer = io.BytesIO()
    circular_img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def create_chart_colors():
    """
    Generate a consistent color palette for charts
    """
    return {
        'primary': '#2563eb',
        'secondary': '#3b82f6', 
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'info': '#06b6d4',
        'light': '#f1f5f9',
        'dark': '#1e293b'
    }
