# Here in this file, we are writing the logic to add custom CSS & font in out project

# Imports Python’s built-in OS module. Used here to check if the CSS file exists on disk (os.path.exists(file_path)).
import os
import streamlit as st
import base64
# Imports Python’s base64 encoding module. It is often helpful if you want to embed images, fonts, or other assets directly into CSS/HTML by encoding them.
 
import streamlit.components.v1 as components
# streamlit.components.v1 is a module that lets you embed or build custom frontend components inside Streamlit apps.
# These components can be:
# Static HTML/JS snippets (like embedding an iframe, widget, or chart).
# Custom-built React/JS apps that communicate with Streamlit’s Python backend.
# When you import it as components, you gain access to functions like components.html() and components.declare_component().



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




# This function is a custom style injector for Streamlit’s WebRTC component.
def inject_webrtc_styles():
    font_path = os.path.join(os.getcwd(), "static", "AdobeClean.otf")
    
    if not os.path.exists(font_path):
        return

    with open(font_path, "rb") as font_file:
        encoded_font = base64.b64encode(font_file.read()).decode()


    # Uses components.html() to insert a <script> block  i.e JavaScript logic into the Streamlit app.
    # The script runs immediately (IIFE — Immediately Invoked Function Expression).
    components.html(
    f"""
        <script>
        (function patchWebRTCStyles() {{
            // Function to inject custom styles into a given iframe
            function injectIntoIframe(iframe) {{
                try {{
                    // Get the iframe's document object
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    if (!doc || !doc.head) return;    // If no document/head, exit

                    // Prevent duplicate injection by checking if style already exists
                    if (doc.head.querySelector('#webrtc-custom-styles')) return;

                    //  Create a <style> element
                    const style = doc.createElement('style');
                    style.id = 'webrtc-custom-styles';    // Assign an ID for tracking

                    // Define CSS rules including custom font and button styling
                    style.textContent = `
                        @font-face {{
                            font-family: 'AdobeClean';
                            src: url('data:font/otf;base64,{encoded_font}') format('opentype');
                            font-weight: 100 900;
                            font-style: normal;
                        }}
                        .MuiButtonBase-root,
                        .MuiButton-root,
                        .MuiButton-contained,
                        .MuiButton-text {{
                            border-radius: 0 !important;             
                            font-family: 'AdobeClean', sans-serif !important; 
                            letter-spacing: 0.05em !important;        
                        }}
                    `;

                    //  Append the style element to the iframe's <head>
                    doc.head.appendChild(style);
                }} catch (e) {{
                    // Log warning if injection fails
                    console.warn('[patcher] could not inject:', e);
                }}
            }}

            // Function to find all WebRTC iframes and patch them
            function findAndPatch() {{
                const parentDoc = window.parent.document;    //  Get parent document
                const iframes = parentDoc.querySelectorAll('iframe');   // Find all iframes

                // Loop through each iframe
                iframes.forEach(iframe => {{
                    //  Only target iframes related to WebRTC
                    if (iframe.src && iframe.src.includes('webrtc')) {{
                        //  If iframe is already loaded, inject immediately
                        if (iframe.contentDocument && iframe.contentDocument.readyState === 'complete') {{
                            injectIntoIframe(iframe);
                        }} else {{
                            // Otherwise, wait until iframe finishes loading
                            iframe.addEventListener('load', () => injectIntoIframe(iframe));
                        }}
                    }}
                }});
            }}

            // Run the patching process immediately
            findAndPatch();
        }})();
        </script>
    """,
    height=0,  # No visible height since this is just injecting styles
)

