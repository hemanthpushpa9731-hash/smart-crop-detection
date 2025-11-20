import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class CropPredictor:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join('models', 'RandomForest.pkl')
        self.load_model()
        
        self.crop_info = {
            'rice': 'Rice grows best in warm, humid climates with temperatures between 20-35°C. Requires flooded fields or heavy rainfall (150-300 cm annually). Suitable for clayey or loamy soil with pH 5.5-7.0. Growing season: 3-6 months.',
            'maize': 'Maize thrives in moderate temperatures (18-27°C) with well-distributed rainfall (50-75 cm). Prefers well-drained loamy soil with pH 5.5-7.5. Rich in nitrogen and phosphorus requirements. Growing season: 3-5 months.',
            'chickpea': 'Chickpea is a cool-season crop preferring temperatures 20-30°C. Requires low to moderate rainfall (40-60 cm). Grows well in sandy loam to clayey loam soil with pH 6.0-7.5. Drought-tolerant. Growing season: 3-5 months.',
            'kidneybeans': 'Kidney beans prefer warm temperatures (18-24°C) and moderate rainfall (60-120 cm). Thrives in well-drained loamy soil with pH 6.0-7.0. Requires good nitrogen fixation. Growing season: 2-4 months.',
            'pigeonpeas': 'Pigeon peas are drought-resistant, growing in temperatures 20-35°C. Requires low rainfall (60-100 cm). Adapts to various soils but prefers well-drained sandy loam with pH 5.5-7.5. Growing season: 4-5 months.',
            'mothbeans': 'Moth beans are extremely drought-resistant, suitable for arid climates with temperatures 25-35°C. Minimal rainfall required (30-60 cm). Grows in sandy to sandy loam soil with pH 7.0-8.5. Growing season: 2-3 months.',
            'mungbean': 'Mung beans prefer warm temperatures (25-35°C) with moderate rainfall (60-100 cm). Requires well-drained loamy soil with pH 6.2-7.2. Short-duration crop. Growing season: 2-3 months.',
            'blackgram': 'Black gram grows best in warm temperatures (25-35°C) with moderate rainfall (60-100 cm). Prefers loamy to clayey soil with pH 6.5-7.5. Good nitrogen fixer. Growing season: 2-3 months.',
            'lentil': 'Lentil is a cool-season crop preferring temperatures 18-25°C. Requires low to moderate rainfall (40-60 cm). Grows in well-drained loamy soil with pH 6.0-7.5. Drought-tolerant. Growing season: 3-5 months.',
            'pomegranate': 'Pomegranate thrives in hot, dry climates with temperatures 30-40°C. Drought-resistant, requires low rainfall (50-75 cm). Adapts to various soils but prefers deep loamy soil with pH 6.5-7.5. Perennial crop.',
            'banana': 'Banana requires warm, humid tropical climate with temperatures 25-35°C. Needs heavy rainfall (200-250 cm annually). Thrives in deep, well-drained loamy soil rich in organic matter with pH 6.0-7.5. Year-round production.',
            'mango': 'Mango grows in tropical and subtropical climates with temperatures 24-30°C. Requires moderate rainfall (75-200 cm) with dry flowering season. Prefers well-drained sandy loam to clay loam with pH 5.5-7.5. Perennial fruit tree.',
            'grapes': 'Grapes thrive in warm temperate to subtropical climates with temperatures 15-30°C. Requires moderate rainfall (50-100 cm) with dry harvest season. Prefers well-drained sandy loam soil with pH 6.0-7.0. Perennial vine crop.',
            'watermelon': 'Watermelon grows best in warm temperatures (24-30°C) with moderate rainfall (50-75 cm). Requires well-drained sandy loam soil rich in organic matter with pH 6.0-7.0. Growing season: 2-3 months.',
            'muskmelon': 'Muskmelon prefers warm temperatures (25-30°C) with moderate rainfall (40-60 cm). Thrives in well-drained sandy loam soil with good organic content and pH 6.0-7.0. Growing season: 2-3 months.',
            'apple': 'Apple requires cool temperate climate with winter chilling (800-1200 hours below 7°C). Prefers temperatures 20-24°C during growing season with moderate rainfall (100-125 cm). Best in well-drained loamy soil with pH 5.5-7.0. Perennial tree.',
            'orange': 'Orange thrives in subtropical to tropical climate with temperatures 25-35°C. Requires moderate to high rainfall (100-200 cm). Prefers well-drained sandy loam to clay loam with pH 6.0-7.5. Perennial citrus tree.',
            'papaya': 'Papaya grows in tropical climate with temperatures 25-35°C year-round. Requires well-distributed rainfall (150-250 cm). Prefers well-drained loamy soil rich in organic matter with pH 6.0-7.0. Fast-growing, produces within 6-12 months.',
            'coconut': 'Coconut palm thrives in tropical coastal regions with temperatures 27-32°C. Requires high rainfall (150-250 cm) or irrigation. Grows in sandy to loamy soil with pH 5.5-8.0. Very long-lived perennial, salt-tolerant.',
            'cotton': 'Cotton requires warm climate with temperatures 21-30°C and plenty of sunshine. Needs moderate rainfall (50-100 cm) with dry harvest period. Thrives in deep, well-drained clayey loam soil with pH 6.0-7.5. Growing season: 5-6 months.',
            'jute': 'Jute grows in warm, humid climate with temperatures 24-35°C. Requires heavy rainfall (150-250 cm) during growing season. Best in fertile alluvial soil with pH 6.0-7.5. Growing season: 4-5 months.',
            'coffee': 'Coffee grows in tropical highlands with temperatures 15-24°C. Requires well-distributed rainfall (150-250 cm). Prefers well-drained volcanic or loamy soil rich in organic matter with pH 6.0-6.5. Shade-loving perennial shrub.'
        }
    
    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"Crop recommendation model loaded from {self.model_path}")
            except Exception as e:
                print(f"Warning: Could not load model from {self.model_path}: {e}")
                self.model = None
        else:
            print(f"Warning: Model file not found at {self.model_path}")
            print("Please run train_model.py to train a new model")
            self.model = None
    
    def predict(self, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
        # Predict exactly as in Tkinter version: direct numpy array with correct feature order
        # Features order: N, P, K, temperature, humidity, ph, rainfall
        if self.model is not None:
            try:
                # Convert all inputs to float and create array exactly like Tkinter
                input_data = [[float(nitrogen),
                              float(phosphorus),
                              float(potassium),
                              float(temperature),
                              float(humidity),
                              float(ph),
                              float(rainfall)]]
                
                # Get prediction probabilities
                probabilities = self.model.predict_proba(input_data)[0]
                classes = self.model.classes_
                
                # Get top predictions sorted by probability
                top_indices = np.argsort(probabilities)[::-1]
                predictions = []
                for idx in top_indices:
                    crop_name = classes[idx]
                    confidence = probabilities[idx] * 100
                    predictions.append({
                        'crop': crop_name,
                        'confidence': confidence
                    })
                return predictions
            except Exception as e:
                print(f"Error in model prediction: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to rule-based prediction if model fails
        return self._get_rule_based_prediction(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)
    
    def _get_rule_based_prediction(self, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
        scores = {}
        
        for crop in self.crop_info.keys():
            score = 50
            
            if crop in ['rice', 'jute', 'banana']:
                if rainfall > 150: score += 30
                if humidity > 70: score += 20
            elif crop in ['cotton', 'maize', 'mango']:
                if 50 < rainfall < 100: score += 25
                if 20 < temperature < 30: score += 25
            elif crop in ['apple', 'grapes']:
                if temperature < 25: score += 30
                if 50 < rainfall < 125: score += 20
            elif crop in ['chickpea', 'lentil', 'mothbeans']:
                if rainfall < 60: score += 30
                if nitrogen < 50: score += 20
            
            if 6.0 < ph < 7.5: score += 10
            if nitrogen > 40: score += 5
            if phosphorus > 30: score += 5
            if potassium > 30: score += 5
            
            scores[crop] = min(score, 100)
        
        sorted_crops = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        predictions = []
        for crop_name, confidence in sorted_crops:
            predictions.append({
                'crop': crop_name,
                'confidence': float(confidence)
            })
        
        return predictions
    
    def get_top_recommendations(self, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, top_n=3):
        predictions = self.predict(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)
        
        top_predictions = predictions[:top_n]
        
        for pred in top_predictions:
            crop_name = pred['crop']
            pred['info'] = self.crop_info.get(crop_name, 'No information available for this crop.')
        
        return top_predictions
