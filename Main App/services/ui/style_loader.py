# Here in this file, we are writing the logic to add custom CSS & font in out project

# Imports Python’s built-in OS module. Used here to check if the CSS file exists on disk (os.path.exists(file_path)).
import os
import streamlit as st
import base64
# Imports Python’s base64 encoding module. It is often helpful if you want to embed images, fonts, or other assets directly into CSS/HTML by encoding them.
 

def load_css(file_path):
    # Checks if the given CSS file actually exists at the specified path. Prevents errors if the file is missing.
    if os.path.exists(file_path):
        # Opens the CSS file in read mode. f.read() will load the entire CSS file content as a string.
        with open(file_path) as f:
            # Injects the CSS into the Streamlit app using Markdown rendering.
            # Wrapping the CSS inside <style> ... </style> tags tells the browser to treat it as CSS.
            # unsafe_allow_html=True is required because Streamlit normally sanitizes HTML for safety. This flag allows raw HTML/CSS injection.
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



def inject_local_font(font_path, font_name):
    # First check if the font file actually exists at the given path
    if not os.path.exists(font_path):
        return
    

    with open(font_path, "rb") as f:
        # Read the raw bytes of the font file
        font_bytes = f.read()
        
        # Encode those bytes into a Base64 string
        # Base64 encoding allows binary data (like fonts) to be embedded directly into CSS/HTML
        encoded = base64.b64encode(font_bytes).decode()


    # Here ext means extension, fmt means format & mime means MIME Typetext, image, video, etc)
    ext = os.path.splitext(font_path)[1].lstrip(".")
    # Extracts the file extension from the font file path. Example: "Manrope-Regular.otf" → "otf".
    # .splitext() returns a tuple (filename, extension). [1] picks the extension.
    # .lstrip(".") removes the leading dot.
    
    fmt = {"otf": "opentype"}.get(ext, ext)
    # Defines the format string for CSS. CSS expects "opentype" for .otf fonts.
    # For other extensions (like .ttf), it just uses the extension itself.
    # Example: If ext = "otf" → fmt = "opentype". And If ext = "ttf" → fmt = "ttf".
    
    mime = {"otf": "font/otf"}.get(ext, f"font/{ext}")
    # Defines the MIME type for the font. MIME tells the browser what kind of file it is.
    # Example: If ext = "otf" → mime = "font/otf". If ext = "ttf" → mime = "font/ttf".

    # Injects CSS into the Streamlit app. The CSS block defines a custom font-face
    st.markdown(f"""
        <style>
        @font-face {{
            font-family: '{font_name}';
            src: url('data:{mime};base64,{encoded}') format('{fmt}');
            font-weight: 100 900;
            font-style: normal;
        }}
        </style>
    """, unsafe_allow_html=True)

    # @font-face :- A CSS rule that lets you define and load custom fonts. Once defined, you can use the font anywhere in your app with font-family.

    # src: url('data:{mime};base64,{encoded}') format('{fmt}') :-
    # src tells the browser where to load the font from.
    # Instead of linking to an external file, you’re embedding the font directly as a Base64-encoded string.
    # {mime} → The MIME type of the font (e.g., font/otf, font/ttf).
    # {encoded} → The Base64-encoded font data (binary converted to text).
    # format('{fmt}') → The font format (e.g., opentype, truetype).


