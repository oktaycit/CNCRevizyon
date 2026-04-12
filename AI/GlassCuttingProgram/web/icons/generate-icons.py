#!/usr/bin/env python3
"""
GlassCutting Pro - Icon Generator
Generates PNG icons for the Chrome App
"""

import os
import sys

def create_simple_icon(size, filename):
    """Create a simple PNG icon using basic PNG encoding"""
    # This is a minimal PNG generator for placeholder icons
    # For production use, use PIL/Pillow or similar
    
    import struct
    import zlib
    
    def png_chunk(chunk_type, data):
        chunk_len = struct.pack('>I', len(data))
        chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
        return chunk_len + chunk_type + data + chunk_crc
    
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    width = size
    height = size
    bit_depth = 8
    color_type = 2  # RGB
    compression = 0
    filter_method = 0
    interlace = 0
    
    ihdr_data = struct.pack('>IIBBBBB', width, height, bit_depth, color_type, 
                           compression, filter_method, interlace)
    ihdr_chunk = png_chunk(b'IHDR', ihdr_data)
    
    # IDAT chunk (image data)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Filter type: None
        for x in range(width):
            # Create gradient blue background
            r = int(25 + (x / width) * 20)  # #1976D2 variant
            g = int(118 - (y / height) * 20)  # #1976D2 variant
            b = int(210 - (x / width) * 20)  # #1976D2 variant
            raw_data += bytes([r, g, b])
    
    compressed = zlib.compress(raw_data, 9)
    idat_chunk = png_chunk(b'IDAT', compressed)
    
    # IEND chunk
    iend_chunk = png_chunk(b'IEND', b'')
    
    # Write PNG file
    with open(filename, 'wb') as f:
        f.write(signature + ihdr_chunk + idat_chunk + iend_chunk)
    
    print(f"Created: {filename} ({size}x{size})")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    print("GlassCutting Pro - Icon Generator")
    print("=" * 40)
    
    for size in sizes:
        filename = os.path.join(script_dir, f'icon{size}.png')
        create_simple_icon(size, filename)
    
    print("=" * 40)
    print("✅ All icons generated successfully!")
    print("\nNote: These are placeholder icons.")
    print("For production icons, use the generate-icons.html file in a browser")
    print("or create custom icons with a graphics editor.")

if __name__ == '__main__':
    main()
