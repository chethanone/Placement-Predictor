#!/usr/bin/env python
# Script to remove null bytes from views.py

with open('predictor/views.py', 'rb') as f:
    content = f.read()

# Remove null bytes
cleaned_content = content.replace(b'\x00', b'')

with open('predictor/views.py', 'wb') as f:
    f.write(cleaned_content)

print("Null bytes removed from views.py")
