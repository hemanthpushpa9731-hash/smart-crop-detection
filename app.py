from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
from PIL import Image
import io
from datetime import datetime
from disease_detection import DiseaseDetector
from crop_prediction import CropPredictor
from chatbot import FarmingAssistant
from chatbot.offline_chatbot import OfflineFarmingChatbot
from chatbot.enhanced_chatbot import EnhancedFarmingChatbot
from database import FarmingHistoryManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartcropsprayer-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize modules
detector = DiseaseDetector()
crop_predictor = CropPredictor()
history_manager = FarmingHistoryManager()

# Initialize chatbot (online if API key available, enhanced offline otherwise)
try:
    chatbot = FarmingAssistant()
    use_offline_chatbot = False
except ValueError:
    # Use enhanced chatbot with SmartCropSprayer knowledge integration
    chatbot = EnhancedFarmingChatbot()
    use_offline_chatbot = True

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def index():
    """Homepage."""
    return render_template('index.html')

@app.route('/disease-detection')
def disease_detection_page():
    """Disease detection page."""
    return render_template('disease_detection.html')

@app.route('/crop-prediction')
def crop_prediction_page():
    """Crop prediction page."""
    return render_template('crop_prediction.html')

@app.route('/chatbot')
def chatbot_page():
    """AI chatbot page."""
    # Initialize session chat history if needed (inside request context)
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('chatbot.html', use_offline=use_offline_chatbot)

@app.route('/history')
def history_page():
    """History page."""
    stats = history_manager.get_statistics()
    # Map stats keys to match template expectations
    mapped_stats = {
        'total_crops': stats.get('total_crop_recommendations', 0),
        'total_diseases': stats.get('total_disease_detections', 0),
        'total_chats': stats.get('total_chatbot_queries', 0),
        'top_crop': stats.get('most_recommended_crop', 'N/A'),
        'top_disease': stats.get('most_common_disease', 'N/A')
    }
    return render_template('history.html', stats=mapped_stats)

# API Routes
@app.route('/api/predict-disease', methods=['POST'])
def predict_disease():
    """Handle disease detection API request."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, or JPEG'}), 400
    
    try:
        # Read and process image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run disease detection
        result = detector.detect_disease(image)
        
        # Log to history
        image_name = secure_filename(file.filename)
        history_manager.log_disease_detection(
            image_name=image_name,
            detected_disease=result['disease'],
            confidence=result['confidence'],
            pesticide=result['pesticide'],
            is_healthy=result['is_healthy'],
            all_predictions=result.get('all_predictions', [])
        )
        
        # Return prediction result
        return jsonify({
            'success': True,
            'disease': result['disease'],
            'confidence': round(result['confidence'], 2),
            'is_healthy': result['is_healthy'],
            'pesticide': result['pesticide'],
            'pesticide_details': result['pesticide_details'],
            'description': detector.get_disease_description(result['disease']),
            'all_predictions': result.get('all_predictions', [])
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/api/predict-crop', methods=['POST'])
def predict_crop():
    """Handle crop prediction API request."""
    try:
        data = request.get_json()
        
        nitrogen = float(data.get('nitrogen', 0))
        phosphorus = float(data.get('phosphorus', 0))
        potassium = float(data.get('potassium', 0))
        temperature = float(data.get('temperature', 0))
        humidity = float(data.get('humidity', 0))
        ph = float(data.get('ph', 7.0))
        rainfall = float(data.get('rainfall', 0))
        
        # Get top 3 recommendations
        recommendations = crop_predictor.get_top_recommendations(
            nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, top_n=3
        )
        
        # Log to history (top recommendation)
        if recommendations:
            top_crop = recommendations[0]
            history_manager.log_crop_recommendation(
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                temperature=temperature,
                humidity=humidity,
                ph=ph,
                rainfall=rainfall,
                recommended_crop=top_crop['crop'],
                confidence=top_crop['confidence'],
                crop_info=top_crop['info']
            )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'error': f'Error predicting crop: {str(e)}'}), 500

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """Handle chatbot API request."""
    try:
        data = request.get_json()
        user_query = data.get('message', '').strip()
        
        if not user_query:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get response from chatbot - this should be fast
        if use_offline_chatbot:
            # Enhanced chatbot uses generate_reply method with SmartCropSprayer knowledge
            response = chatbot.generate_reply(user_query)
            chatbot_type = 'offline_enhanced'
        else:
            response = chatbot.chat(user_query)
            chatbot_type = 'online'
        
        # Return response immediately for instant display
        result = jsonify({
            'success': True,
            'response': response,
            'type': chatbot_type
        })
        
        # Update session and log to database after response (non-blocking)
        try:
            if 'chat_history' not in session:
                session['chat_history'] = []
            
            session['chat_history'].append({
                'user': user_query,
                'bot': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Log to database (this is fast but happens after response sent)
            history_manager.log_chatbot_query(user_query, response, chatbot_type)
        except Exception as db_error:
            # Don't fail if logging has issues
            print(f"Warning: Could not log chat to database: {db_error}")
        
        return result
    
    except Exception as e:
        return jsonify({'error': f'Error processing chat: {str(e)}'}), 500

@app.route('/api/history/crops', methods=['GET'])
def get_crop_history():
    """Get crop recommendation history."""
    try:
        df = history_manager.get_crop_recommendations()
        return jsonify({
            'success': True,
            'data': df.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/diseases', methods=['GET'])
def get_disease_history():
    """Get disease detection history."""
    try:
        df = history_manager.get_disease_detections()
        return jsonify({
            'success': True,
            'data': df.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/chatbot', methods=['GET'])
def get_chatbot_history():
    """Get chatbot query history."""
    try:
        df = history_manager.get_chatbot_queries()
        return jsonify({
            'success': True,
            'data': df.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/export/<history_type>', methods=['GET'])
def export_history(history_type):
    """Export history data as CSV."""
    try:
        import pandas as pd
        from flask import Response
        
        if history_type == 'crops':
            df = history_manager.get_crop_recommendations(limit=10000)
        elif history_type == 'diseases':
            df = history_manager.get_disease_detections(limit=10000)
        elif history_type == 'chatbot':
            df = history_manager.get_chatbot_queries(limit=10000)
        else:
            return jsonify({'error': 'Invalid history type'}), 400
        
        csv = df.to_csv(index=False)
        return Response(
            csv,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={history_type}_history.csv'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/clear', methods=['POST'])
def clear_all_history():
    """Clear all history from database."""
    try:
        success = history_manager.clear_all_history()
        if success:
            return jsonify({
                'success': True,
                'message': 'All history has been cleared successfully.'
            })
        else:
            return jsonify({'error': 'Failed to clear history'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def safe_print(message):
    """Print message safely, handling Unicode errors."""
    try:
        print(message)
    except UnicodeEncodeError:
        import sys
        print(message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))

if __name__ == '__main__':
    # Find available port starting from 5000
    import socket
    port = 5000
    for port in range(5000, 5100):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result != 0:  # Port is available
            break
    else:
        port = 5000  # Fallback
    
    safe_print(f"SmartCropSprayer Flask App")
    safe_print(f"Starting server on http://127.0.0.1:{port}")
    if hasattr(detector, 'model') and detector.model is not None:
        safe_print(f"Disease Detection Model: Loaded (PyTorch)")
        safe_print(f"Model Path: {os.path.abspath(detector.model_path)}")
        safe_print(f"Model Format: PyTorch (.pth)")
        safe_print(f"Device: {detector.device}")
    else:
        safe_print(f"Disease Detection Model: Using rule-based fallback")
        safe_print(f"Tip: Place model.pth in the models/ directory for AI detection")
    safe_print(f"Chatbot Mode: {'Online (GPT-5)' if not use_offline_chatbot else 'Offline (Local)'}")
    safe_print(f"\nServer is ready! Open http://127.0.0.1:{port} in your browser\n")
    
    app.run(host='127.0.0.1', port=port, debug=True, use_reloader=False)
