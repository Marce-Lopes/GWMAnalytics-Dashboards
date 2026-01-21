
import base64

def get_base64_image(image_path):
    """Get base64 encoding of an image file"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return None


def format_number(value):
    """
    Format number to K notation if >= 1000.
    Examples: 
        743 -> 743
        1340 -> 1.34k
    """
    if not isinstance(value, (int, float)):
        return str(value)
        
    if value >= 1000:
        return f"{value/1000:.2f}k"
    return str(value)


def get_normalized_weekday(date_obj):
    """
    Return a string representing the 'Nth Weekday' of the month.
    e.g. '1st Monday', '2nd Friday', etc.
    """
    day = date_obj.day
    weekday = date_obj.strftime('%A') # Monday, Tuesday...
    # Calculate N (1st, 2nd, 3rd, 4th, 5th)
    n = (day - 1) // 7 + 1
    
    suffix = "th"
    if n == 1: suffix = "st"
    elif n == 2: suffix = "nd"
    elif n == 3: suffix = "rd"
    
    return f"{n}{suffix} {weekday}"
