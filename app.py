from flask import Flask, render_template, request, jsonify, send_file, session, send_from_directory, url_for
import logging
from flask_session import Session
import os
import base64
import requests
import json
import re
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime, timedelta
import shutil
import time
from threading import Thread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PP-StructureV3 API Configuration
API_URL = "https://wfk3ide9lcd0x0k9.aistudio-app.com/layout-parsing"
TOKEN = "031c87b3c44d16aa4adf6928bcfa132e23393afc"

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'xls', 'xlsx'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('flask_session', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_session_files():
    """Clean up all uploaded and extracted files for current session"""
    session_id = session.get('session_id')
    if session_id:
        session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        session_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        
        if os.path.exists(session_upload_dir):
            shutil.rmtree(session_upload_dir)
        if os.path.exists(session_output_dir):
            shutil.rmtree(session_output_dir)

def cleanup_old_files(hours=24):
    """Clean up files and directories older than specified hours"""
    cutoff_time = time.time() - (hours * 3600)
    cleaned = {'uploads': 0, 'outputs': 0, 'sessions': 0}
    
    # Clean old upload directories
    for session_dir in os.listdir(app.config['UPLOAD_FOLDER']):
        dir_path = os.path.join(app.config['UPLOAD_FOLDER'], session_dir)
        if os.path.isdir(dir_path) and os.path.getmtime(dir_path) < cutoff_time:
            try:
                shutil.rmtree(dir_path)
                cleaned['uploads'] += 1
                logger.info(f"Cleaned old upload directory: {session_dir}")
            except Exception as e:
                logger.error(f"Error cleaning upload directory {session_dir}: {e}")
    
    # Clean old output directories
    for session_dir in os.listdir(app.config['OUTPUT_FOLDER']):
        dir_path = os.path.join(app.config['OUTPUT_FOLDER'], session_dir)
        if os.path.isdir(dir_path) and os.path.getmtime(dir_path) < cutoff_time:
            try:
                shutil.rmtree(dir_path)
                cleaned['outputs'] += 1
                logger.info(f"Cleaned old output directory: {session_dir}")
            except Exception as e:
                logger.error(f"Error cleaning output directory {session_dir}: {e}")
    
    # Clean old flask session files
    session_dir = 'flask_session'
    if os.path.exists(session_dir):
        for session_file in os.listdir(session_dir):
            file_path = os.path.join(session_dir, session_file)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    cleaned['sessions'] += 1
                    logger.info(f"Cleaned old session file: {session_file}")
                except Exception as e:
                    logger.error(f"Error cleaning session file {session_file}: {e}")
    
    return cleaned

def cleanup_other_sessions(current_session_id):
    """Clean up all sessions EXCEPT the current one"""
    cleaned = {'uploads': 0, 'outputs': 0, 'sessions': 0}
    
    # Clean other session upload directories
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for session_dir in os.listdir(app.config['UPLOAD_FOLDER']):
            if session_dir != current_session_id:
                dir_path = os.path.join(app.config['UPLOAD_FOLDER'], session_dir)
                if os.path.isdir(dir_path):
                    try:
                        shutil.rmtree(dir_path)
                        cleaned['uploads'] += 1
                        logger.info(f"Cleaned other session upload directory: {session_dir}")
                    except Exception as e:
                        logger.error(f"Error cleaning upload directory {session_dir}: {e}")
    
    # Clean other session output directories
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        for session_dir in os.listdir(app.config['OUTPUT_FOLDER']):
            if session_dir != current_session_id:
                dir_path = os.path.join(app.config['OUTPUT_FOLDER'], session_dir)
                if os.path.isdir(dir_path):
                    try:
                        shutil.rmtree(dir_path)
                        cleaned['outputs'] += 1
                        logger.info(f"Cleaned other session output directory: {session_dir}")
                    except Exception as e:
                        logger.error(f"Error cleaning output directory {session_dir}: {e}")
    
    # Keep flask session files - they are needed for active sessions
    # Only clean files older than 24 hours
    session_dir = 'flask_session'
    if os.path.exists(session_dir):
        cutoff_time = time.time() - (24 * 3600)
        for session_file in os.listdir(session_dir):
            file_path = os.path.join(session_dir, session_file)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    cleaned['sessions'] += 1
                    logger.info(f"Cleaned old session file: {session_file}")
                except Exception as e:
                    logger.error(f"Error cleaning session file {session_file}: {e}")
    
    return cleaned

def cleanup_all_sessions():
    """Clean up ALL session data (aggressive cleanup on startup)"""
    cleaned = {'uploads': 0, 'outputs': 0, 'sessions': 0}
    
    # Clean ALL upload directories
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for session_dir in os.listdir(app.config['UPLOAD_FOLDER']):
            dir_path = os.path.join(app.config['UPLOAD_FOLDER'], session_dir)
            if os.path.isdir(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    cleaned['uploads'] += 1
                    logger.info(f"Cleaned upload directory: {session_dir}")
                except Exception as e:
                    logger.error(f"Error cleaning upload directory {session_dir}: {e}")
    
    # Clean ALL output directories
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        for item in os.listdir(app.config['OUTPUT_FOLDER']):
            dir_path = os.path.join(app.config['OUTPUT_FOLDER'], item)
            if os.path.isdir(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    cleaned['outputs'] += 1
                    logger.info(f"Cleaned output directory: {item}")
                except Exception as e:
                    logger.error(f"Error cleaning output directory {item}: {e}")
    
    # Clean ALL flask session files
    session_dir = 'flask_session'
    if os.path.exists(session_dir):
        for session_file in os.listdir(session_dir):
            file_path = os.path.join(session_dir, session_file)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    cleaned['sessions'] += 1
                    logger.info(f"Cleaned session file: {session_file}")
                except Exception as e:
                    logger.error(f"Error cleaning session file {session_file}: {e}")
    
    return cleaned

def periodic_cleanup():
    """Run cleanup periodically in background"""
    while True:
        time.sleep(3600)  # Run every hour
        try:
            cleaned = cleanup_old_files(hours=24)
            logger.info(f"Periodic cleanup: {cleaned}")
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")

@app.before_request
def before_request():
    """Initialize session and ensure session directories exist"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['uploaded_files'] = []
        
        # Clean up ALL other sessions when new session starts (aggressive)
        try:
            cleaned = cleanup_all_sessions()
            if any(cleaned.values()):
                logger.info(f"New session startup - cleaned all old sessions: {cleaned}")
        except Exception as e:
            logger.error(f"Error in new session cleanup: {e}")
    else:
        # For existing sessions, clean other sessions periodically
        try:
            cleaned = cleanup_other_sessions(session['session_id'])
            if any(cleaned.values()):
                logger.info(f"Existing session cleanup (removed other sessions): {cleaned}")
        except Exception as e:
            logger.error(f"Error in existing session cleanup: {e}")
    
    # Create session-specific directories
    session_id = session['session_id']
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], session_id), exist_ok=True)
    os.makedirs(os.path.join(app.config['OUTPUT_FOLDER'], session_id), exist_ok=True)

@app.route('/')
def index():
    """Home page with upload functionality"""
    # Clean up other sessions on every page load
    try:
        session_id = session.get('session_id')
        if session_id:
            cleaned = cleanup_other_sessions(session_id)
            if any(cleaned.values()):
                logger.info(f"Page load cleanup (removed other sessions): {cleaned}")
    except Exception as e:
        logger.error(f"Error in page load cleanup: {e}")
    
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        session_id = session['session_id']
        
        # Create unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session_id, unique_filename)
        
        file.save(filepath)
        
        # Add to uploaded files list
        uploaded_files = session.get('uploaded_files', [])
        file_info = {
            'id': str(uuid.uuid4()),
            'original_name': filename,
            'unique_name': unique_filename,
            'filepath': filepath,
            'upload_time': datetime.now().isoformat(),
            'status': 'uploaded'
        }
        uploaded_files.append(file_info)
        session['uploaded_files'] = uploaded_files
        
        return jsonify({
            'success': True,
            'file_id': file_info['id'],
            'filename': filename,
            'message': 'File uploaded successfully'
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/files', methods=['GET'])
def get_uploaded_files():
    """Get list of uploaded files"""
    return jsonify({'files': session.get('uploaded_files', [])})

@app.route('/delete-file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a specific uploaded file"""
    uploaded_files = session.get('uploaded_files', [])
    file_to_delete = None
    
    for file_info in uploaded_files:
        if file_info['id'] == file_id:
            file_to_delete = file_info
            break
    
    if file_to_delete:
        # Delete physical file
        if os.path.exists(file_to_delete['filepath']):
            os.remove(file_to_delete['filepath'])
        
        # Remove from session
        uploaded_files.remove(file_to_delete)
        session['uploaded_files'] = uploaded_files
        
        return jsonify({'success': True, 'message': 'File deleted'})
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up all session files"""
    cleanup_session_files()
    session['uploaded_files'] = []
    return jsonify({'success': True, 'message': 'All files cleaned up'})

@app.route('/preprocess/<file_id>', methods=['POST'])
def preprocess_file(file_id):
    """Preprocess PDF to detect and stitch tables"""
    from utils.pdf_processor import PDFProcessor
    
    uploaded_files = session.get('uploaded_files', [])
    file_info = None
    
    for f in uploaded_files:
        if f['id'] == file_id:
            file_info = f
            break
    
    if not file_info:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        processor = PDFProcessor()
        result = processor.preprocess_pdf(file_info['filepath'], session['session_id'])

        # Convert local output paths to URLs that the frontend can fetch
        session_id = session['session_id']
        # stitched_image
        stitched_local = result.get('stitched_image')
        if stitched_local:
            # stitched_local is like outputs/<session_id>/preprocessing/stitched_table.jpg
            stitched_rel = os.path.relpath(stitched_local, os.path.join(app.config['OUTPUT_FOLDER'], session_id))
            result['stitched_image_url'] = url_for('serve_output', session_id=session_id, filename=stitched_rel)

        # thumbnails
        thumbs = result.get('thumbnails', [])
        thumb_urls = []
        for t in thumbs:
            thumb_local = t.get('path')
            if thumb_local:
                thumb_rel = os.path.relpath(thumb_local, os.path.join(app.config['OUTPUT_FOLDER'], session_id))
                t['path_url'] = url_for('serve_output', session_id=session_id, filename=thumb_rel)
            thumb_urls.append(t)

        result['thumbnails'] = thumb_urls

        # Update file status
        file_info['status'] = 'preprocessed'
        file_info['preprocessed_data'] = result
        session.modified = True

        return jsonify({
            'success': True,
            'result': result,
            'message': 'Preprocessing completed'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/outputs/<session_id>/<path:filename>')
def serve_output(session_id, filename):
    """Serve files from the outputs directory for the given session."""
    base_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    # Security: prevent path traversal by resolving real path
    full_path = os.path.realpath(os.path.join(base_dir, filename))
    if not full_path.startswith(os.path.realpath(base_dir)):
        return jsonify({'error': 'Invalid file path'}), 400
    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404
    # send_from_directory expects directory and filename relative to it
    rel_dir = os.path.dirname(filename)
    rel_file = os.path.basename(filename)
    return send_from_directory(os.path.join(app.config['OUTPUT_FOLDER'], session_id, rel_dir), rel_file)

@app.route('/extract/<file_id>', methods=['POST'])
def extract_table(file_id):
    """Extract table using PP-StructureV3 API"""
    uploaded_files = session.get('uploaded_files', [])
    file_info = None
    
    for f in uploaded_files:
        if f['id'] == file_id:
            file_info = f
            break
    
    if not file_info:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Read file and encode to base64
        with open(file_info['filepath'], 'rb') as file:
            file_bytes = file.read()
            file_data = base64.b64encode(file_bytes).decode('ascii')
        
        # Determine file type
        file_extension = file_info['original_name'].rsplit('.', 1)[1].lower()
        file_type = 0 if file_extension == 'pdf' else 1
        
        headers = {
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "file": file_data,
            "fileType": file_type,
            "useDocPreprocessor": False,
            "useSealRecognition": True,
            "useTableRecognition": True,
            "useFormulaRecognition": True,
            "useChartRecognition": False,
            "useRegionDetection": True,
            "formatBlockContent": True,
            "useTextlineOrientation": False,
            "useDocOrientationClassify": False,
            "visualize": True
        }
        
        try:
            # set a reasonable timeout
            response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
        except requests.exceptions.RequestException as re:
            logger.exception('Request to PP-StructureV3 API failed')
            return jsonify({'error': 'Request error', 'details': str(re)}), 502

        # Log status and small preview of response for debugging
        logger.info('PP-StructureV3 response status: %s', response.status_code)
        logger.info('PP-StructureV3 response content-type: %s', response.headers.get('Content-Type', 'unknown'))
        resp_text = None
        try:
            resp_text = response.text[:2000]
            logger.info('PP-StructureV3 response body (truncated): %s', resp_text)
        except Exception:
            pass

        # Check if response is HTML (error page)
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            logger.error('API returned HTML instead of JSON - likely an error page or invalid endpoint')
            return jsonify({
                'error': 'API returned HTML instead of JSON',
                'status_code': response.status_code,
                'content_type': content_type,
                'body_preview': resp_text,
                'hint': 'Check API_URL and TOKEN are correct'
            }), 502

        if response.status_code == 200:
            try:
                result = response.json().get("result")
            except Exception as je:
                logger.exception('Failed to decode JSON from PP-StructureV3 response')
                return jsonify({'error': 'Invalid JSON from API', 'status_code': response.status_code, 'body': resp_text}), 502

            # Save results
            session_id = session['session_id']
            output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id, file_id)
            images_dir = os.path.join(output_dir, 'imgs')
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(images_dir, exist_ok=True)

            # Download and save images from API response
            for i, res in enumerate(result.get("layoutParsingResults", [])):
                # Save markdown
                md_filename = os.path.join(output_dir, f"doc_{i}.md")
                
                # Check for images in markdown
                markdown_data = res.get("markdown", {})
                markdown_text = markdown_data.get("text", "")
                images_dict = markdown_data.get("images", {})
                
                # Download images and replace URLs with local paths
                for img_path, img_url in images_dict.items():
                    try:
                        img_response = requests.get(img_url, timeout=30)
                        if img_response.status_code == 200:
                            # Save image locally
                            local_img_path = os.path.join(images_dir, os.path.basename(img_path))
                            with open(local_img_path, 'wb') as img_file:
                                img_file.write(img_response.content)
                            
                            # Create URL-safe path for serving
                            relative_img_path = f"imgs/{os.path.basename(img_path)}"
                            local_url = url_for('serve_output', session_id=session_id, filename=f"{file_id}/{relative_img_path}")
                            
                            # Replace remote URL with local URL in markdown
                            markdown_text = markdown_text.replace(img_path, local_url)
                            
                            logger.info(f'Downloaded image: {img_path} -> {local_img_path}')
                    except Exception as e:
                        logger.error(f'Failed to download image {img_url}: {str(e)}')
                
                # Also update block_content in prunedResult if it exists
                pruned_result = res.get("prunedResult", {})
                parsing_res_list = pruned_result.get("parsing_res_list", [])
                for block in parsing_res_list:
                    if block.get("block_content"):
                        block_content = block["block_content"]
                        # Replace image paths in block content
                        for img_path, img_url in images_dict.items():
                            relative_img_path = f"imgs/{os.path.basename(img_path)}"
                            local_url = url_for('serve_output', session_id=session_id, filename=f"{file_id}/{relative_img_path}")
                            block_content = block_content.replace(img_path, local_url)
                        block["block_content"] = block_content
                
                # Save updated markdown
                with open(md_filename, "w") as md_file:
                    md_file.write(markdown_text)

            # Update file status
            file_info['status'] = 'extracted'
            file_info['extraction_result'] = result
            file_info['output_dir'] = output_dir
            session.modified = True

            return jsonify({
                'success': True,
                'result': result,
                'message': 'Extraction completed successfully'
            })
        else:
            # Try to parse body for helpful details
            err_body = None
            try:
                err_body = response.json()
            except Exception:
                err_body = resp_text

            logger.error('PP-StructureV3 API returned error %s: %s', response.status_code, err_body)
            return jsonify({'error': 'API error', 'status_code': response.status_code, 'body': err_body}), 502
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stitch-tables/<file_id>', methods=['POST'])
def stitch_tables(file_id):
    """Stitch tables from multiple pages, keeping only one header and removing duplicates"""
    uploaded_files = session.get('uploaded_files', [])
    file_info = None
    
    for f in uploaded_files:
        if f['id'] == file_id:
            file_info = f
            break
    
    if not file_info:
        return jsonify({'error': 'File not found'}), 404
    
    if 'extraction_result' not in file_info:
        return jsonify({'error': 'Please extract the tables first'}), 400
    
    try:
        result = file_info['extraction_result']
        layout_parsing_results = result.get('layoutParsingResults', [])
        
        # Extract all tables from all pages
        all_tables = []
        main_header = None
        
        for page_idx, layout_result in enumerate(layout_parsing_results):
            pruned_result = layout_result.get('prunedResult', {})
            parsing_res_list = pruned_result.get('parsing_res_list', [])
            
            for block in parsing_res_list:
                if block.get('block_label') == 'table' and block.get('block_content'):
                    table_html = block['block_content']
                    
                    # Parse the table to extract header and rows
                    import re
                    from html.parser import HTMLParser
                    
                    # Extract table rows
                    tbody_match = re.search(r'<tbody>(.*?)</tbody>', table_html, re.DOTALL)
                    if tbody_match:
                        tbody_content = tbody_match.group(1)
                        rows = re.findall(r'<tr>(.*?)</tr>', tbody_content, re.DOTALL)
                        
                        if rows:
                            # First row is typically the header
                            first_row = rows[0]
                            
                            # Check if this is a header row (contains <th> or looks like a header)
                            is_header = '<th>' in first_row or any(header_text in first_row.lower() for header_text in ['si.no', 'item', 'description', 'qty', 'unit', 'rate', 'amount', 'price'])
                            
                            if main_header is None and is_header:
                                # Store the main header from the first table
                                main_header = first_row
                                # Add all rows including header for first table
                                all_tables.extend(rows)
                            else:
                                # For subsequent tables, skip the header if it matches
                                start_idx = 0
                                if is_header and len(rows) > 1:
                                    # Skip header row and any empty rows
                                    for idx, row in enumerate(rows):
                                        row_text = re.sub(r'<[^>]+>', '', row).strip()
                                        if not row_text or is_header_row(row):
                                            start_idx = idx + 1
                                        else:
                                            break
                                
                                # Add data rows only
                                all_tables.extend(rows[start_idx:])
        
        if not all_tables:
            return jsonify({'error': 'No tables found to stitch'}), 400
        
        # Build the stitched table HTML
        stitched_html = '''
<div style="text-align: center;">
    <html>
        <body>
            <table border="1">
                <tbody>
'''
        
        for row in all_tables:
            stitched_html += f'                    <tr>{row}</tr>\n'
        
        stitched_html += '''                </tbody>
            </table>
        </body>
    </html>
</div>
'''
        
        # Save stitched table
        session_id = session['session_id']
        output_dir = file_info.get('output_dir', os.path.join(app.config['OUTPUT_FOLDER'], session_id, file_id))
        os.makedirs(output_dir, exist_ok=True)
        
        stitched_filename = os.path.join(output_dir, 'stitched_table.html')
        with open(stitched_filename, 'w') as f:
            f.write(stitched_html)
        
        # Update file info
        file_info['stitched_table'] = {
            'html': stitched_html,
            'filepath': stitched_filename,
            'row_count': len(all_tables)
        }
        session.modified = True
        
        logger.info(f'Stitched {len(all_tables)} rows from {len(layout_parsing_results)} pages')
        
        return jsonify({
            'success': True,
            'stitched_html': stitched_html,
            'row_count': len(all_tables),
            'page_count': len(layout_parsing_results),
            'message': f'Successfully stitched {len(all_tables)} rows from {len(layout_parsing_results)} pages'
        })
        
    except Exception as e:
        logger.exception('Error stitching tables')
        return jsonify({'error': str(e)}), 500

def is_header_row(row_html):
    """Check if a row is likely a header row"""
    row_text = re.sub(r'<[^>]+>', '', row_html).strip().lower()
    header_keywords = ['si.no', 'item', 'description', 'qty', 'unit', 'rate', 'amount', 'price', 'total', 'image', 'ref']
    return any(keyword in row_text for keyword in header_keywords)

@app.route('/costing', methods=['GET', 'POST'])
def costing():
    """Costing card functionality"""
    if request.method == 'GET':
        return render_template('costing.html')
    
    # Apply costing factors
    data = request.json
    file_id = data.get('file_id')
    factors = data.get('factors', {})
    table_data = data.get('table_data')  # Get table data from DOM
    
    try:
        from utils.costing_engine import CostingEngine
        engine = CostingEngine()
        result = engine.apply_factors(file_id, factors, session, table_data)
        
        return jsonify({
            'success': True,
            'result': result,
            'message': 'Costing applied successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-offer/<file_id>', methods=['POST'])
def generate_offer(file_id):
    """Generate offer with costing factors"""
    try:
        from utils.offer_generator import OfferGenerator
        generator = OfferGenerator()
        result = generator.generate(file_id, session)
        
        return jsonify({
            'success': True,
            'file_path': result,
            'message': 'Offer generated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-presentation/<file_id>', methods=['POST'])
def generate_presentation(file_id):
    """Generate technical presentation"""
    try:
        data = request.json or {}
        format_type = data.get('format', 'pdf')
        
        from utils.presentation_generator import PresentationGenerator
        generator = PresentationGenerator()
        result = generator.generate(file_id, session, format_type)
        
        return jsonify({
            'success': True,
            'file_path': result,
            'message': f'Presentation generated successfully as {format_type.upper()}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-mas/<file_id>', methods=['POST'])
def generate_mas(file_id):
    """Generate Material Approval Sheets"""
    try:
        from utils.mas_generator import MASGenerator
        generator = MASGenerator()
        result = generator.generate(file_id, session)
        
        return jsonify({
            'success': True,
            'file_path': result,
            'message': 'MAS generated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/value-engineering/<file_id>', methods=['POST'])
def value_engineering(file_id):
    """Generate value-engineered alternatives"""
    data = request.json
    budget_option = data.get('budget_option', 'medium')
    
    try:
        from utils.value_engineering import ValueEngineer
        engineer = ValueEngineer()
        result = engineer.generate_alternatives(file_id, budget_option, session)
        
        return jsonify({
            'success': True,
            'alternatives': result,
            'message': 'Alternatives generated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_type>/<file_id>', methods=['GET'])
def download(file_type, file_id):
    """Download generated files"""
    format_type = request.args.get('format', 'pdf')
    
    try:
        from utils.download_manager import DownloadManager
        manager = DownloadManager()
        file_path = manager.prepare_download(file_id, file_type, format_type, session)
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/extracted/<file_id>', methods=['GET'])
def download_extracted(file_id):
    """Download extracted table data as Excel"""
    format_type = request.args.get('format', 'excel')
    
    try:
        import pandas as pd
        from io import BytesIO
        
        # Get file info
        uploaded_files = session.get('uploaded_files', [])
        file_info = None
        
        for f in uploaded_files:
            if f['id'] == file_id:
                file_info = f
                break
        
        if not file_info or 'extraction_result' not in file_info:
            return jsonify({'error': 'Extraction result not found'}), 404
        
        extraction_result = file_info['extraction_result']
        
        # Create Excel file
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        for page_idx, layout_result in enumerate(extraction_result.get('layoutParsingResults', [])):
            markdown_text = layout_result.get('markdown', {}).get('text', '')
            
            # Try to parse HTML tables from markdown
            if '<table' in markdown_text:
                try:
                    # Use pandas to read HTML tables
                    tables = pd.read_html(markdown_text)
                    for table_idx, df in enumerate(tables):
                        sheet_name = f"Page{page_idx+1}_Table{table_idx+1}"[:31]  # Excel sheet name limit
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                except Exception as e:
                    logger.error(f"Error parsing HTML table: {e}")
                    # Fallback: create a sheet with raw text
                    df = pd.DataFrame({'Extracted Text': [markdown_text]})
                    sheet_name = f"Page{page_idx+1}"[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # No HTML tables, save as text
                df = pd.DataFrame({'Extracted Text': [markdown_text]})
                sheet_name = f"Page{page_idx+1}"[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        writer.close()
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"extracted_{file_info['original_name'].rsplit('.', 1)[0]}.xlsx"
        )
    except Exception as e:
        logger.exception('Error generating Excel download')
        return jsonify({'error': str(e)}), 500

@app.route('/download/stitched/<file_id>', methods=['GET'])
def download_stitched(file_id):
    """Download stitched table as Excel"""
    format_type = request.args.get('format', 'excel')
    
    try:
        import pandas as pd
        from io import BytesIO
        
        # Get file info
        uploaded_files = session.get('uploaded_files', [])
        file_info = None
        
        for f in uploaded_files:
            if f['id'] == file_id:
                file_info = f
                break
        
        if not file_info or 'stitched_table' not in file_info:
            return jsonify({'error': 'Stitched table not found. Please stitch tables first.'}), 404
        
        stitched_html = file_info['stitched_table']['html']
        
        # Create Excel file
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        try:
            # Use pandas to read the stitched HTML table
            tables = pd.read_html(stitched_html)
            if tables:
                df = tables[0]
                df.to_excel(writer, sheet_name='Stitched_Table', index=False)
            else:
                return jsonify({'error': 'No table found in stitched data'}), 404
        except Exception as e:
            logger.error(f"Error parsing stitched HTML table: {e}")
            return jsonify({'error': f'Error parsing table: {str(e)}'}), 500
        
        writer.close()
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"stitched_{file_info['original_name'].rsplit('.', 1)[0]}.xlsx"
        )
    except Exception as e:
        logger.exception('Error generating stitched Excel download')
        return jsonify({'error': str(e)}), 500

@app.route('/admin/cleanup', methods=['POST'])
def admin_cleanup():
    """Manual trigger for cleanup (admin endpoint)"""
    hours = request.json.get('hours', 24) if request.is_json else 24
    try:
        cleaned = cleanup_old_files(hours=hours)
        return jsonify({
            'success': True,
            'message': f'Cleanup completed',
            'cleaned': cleaned
        })
    except Exception as e:
        logger.exception('Error in manual cleanup')
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup-session', methods=['POST'])
def cleanup_session_api():
    """API endpoint for cleaning up current session data"""
    try:
        cleanup_session_files()
        return jsonify({
            'success': True,
            'message': 'Session data cleaned'
        })
    except Exception as e:
        logger.exception('Error in session cleanup')
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup-all', methods=['POST'])
def cleanup_all_api():
    """API endpoint for cleaning all sessions (triggered on page load)"""
    try:
        session_id = session.get('session_id')
        if session_id:
            cleaned = cleanup_other_sessions(session_id)
            return jsonify({
                'success': True,
                'message': 'Other sessions cleaned',
                'cleaned': cleaned
            })
        return jsonify({'success': False, 'message': 'No active session'}), 400
    except Exception as e:
        logger.exception('Error in cleanup all')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run aggressive cleanup on server start (removes ALL old session data)
    try:
        logger.info("Running aggressive cleanup on server start...")
        cleaned = cleanup_all_sessions()
        logger.info(f"Startup cleanup completed: {cleaned}")
    except Exception as e:
        logger.error(f"Error in startup cleanup: {e}")
    
    # Start background cleanup thread (runs every hour as backup)
    cleanup_thread = Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    logger.info("Started periodic cleanup thread (runs every hour, cleans files older than 24h)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
