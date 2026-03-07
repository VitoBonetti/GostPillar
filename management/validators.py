from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size_kb = 2048 # 2 MB limit
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"File size cannot exceed {max_size_kb / 1024} MB.")