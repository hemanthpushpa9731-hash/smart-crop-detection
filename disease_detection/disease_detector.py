import os
import numpy as np
from PIL import Image
import cv2
import torch
import torch.nn as nn
from torchvision import transforms

class DiseaseDetector:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Use the PyTorch model file
        model_path = os.path.join('models', 'model.pth')
        self.model_path = model_path
        
        # Class names matching the working project exactly
        # IMPORTANT: Model has exactly 3 classes (no Healthy class in model)
        # Order must match training: ['apple black rot', 'Apple Scab', 'Powdery Mildew']
        self.class_names = ['apple black rot', 'Apple Scab', 'Powdery Mildew']
        self.img_size = (224, 224)
        self.load_model()
        
        # Preprocessing pipeline - matching working code exactly
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),  # Explicit tuple like working code
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # Inline like working code
        ])
        
        self.disease_descriptions = {
            'Apple Black Rot': 'A serious fungal disease caused by Botryosphaeria obtusa that affects apple trees. Causes dark, sunken lesions on fruit, leaves, and branches. Can lead to fruit rot and tree damage.',
            'apple black rot': 'A serious fungal disease caused by Botryosphaeria obtusa that affects apple trees. Causes dark, sunken lesions on fruit, leaves, and branches. Can lead to fruit rot and tree damage.',
            'Apple Scab': 'A serious fungal disease caused by Venturia inaequalis that affects apple trees. Causes dark, scabby lesions on leaves, fruit, and twigs. Most severe in cool, wet spring weather.',
            'Powdery Mildew': 'A fungal disease caused by Podosphaera leucotricha. Appears as white, powdery patches on leaves and shoots. Can stunt growth, cause leaf distortion, and impact fruit quality if left untreated.',
            'Healthy': 'The leaf shows no signs of disease. The plant appears to be in good health with normal coloration and structure.'
        }
        
        self.pesticide_map = {
            'Apple Black Rot': 'Captan',
            'apple black rot': 'Captan',
            'Apple Scab': 'Mancozeb',
            'Powdery Mildew': 'Sulfur',
            'Healthy': 'None'
        }
        
        self.pesticide_details = {
            'Captan': {
                'description': 'Protective fungicide effective against apple black rot',
                'usage': 'Apply 2-3 kg/ha of Captan mixed with water. Spray Captan at 7-10 day intervals, especially during warm, humid weather',
                'precautions': 'Wear protective equipment (gloves, goggles, long-sleeved clothing, and respirator). Do not apply during hot weather (above 30°C). Observe 3-day pre-harvest interval. Store in a cool, dry place away from direct sunlight. Keep containers tightly closed and out of reach of children and pets. Wash hands thoroughly after handling. Avoid contact with eyes and skin. Dispose of empty containers properly according to local regulations.'
            },
            'Mancozeb': {
                'description': 'Broad-spectrum protective fungicide effective against apple scab',
                'usage': 'Apply 2-3 kg/ha of Mancozeb mixed with water. Spray Mancozeb at 10-14 day intervals during wet periods',
                'precautions': 'Wear protective equipment. Do not spray during flowering. Observe 7-day pre-harvest interval'
            },
            'Sulfur': {
                'description': 'Organic fungicide effective against powdery mildew',
                'usage': 'Apply 3-5 kg/ha of Sulfur as dust or wettable powder. Spray Sulfur at 7-10 day intervals',
                'precautions': 'Do not apply when temperature exceeds 32°C. Wear protective mask to avoid inhalation'
            },
            'None': {
                'description': 'No pesticide treatment needed',
                'usage': 'Maintain good agricultural practices and monitor plant health regularly',
                'precautions': 'Continue regular inspection for early disease detection'
            }
        }
    
    def load_model(self):
        """Load the PyTorch model file (model.pth) - matching working code exactly."""
        if not os.path.exists(self.model_path):
            self._safe_print(f"WARNING: Model file not found at {os.path.abspath(self.model_path)}")
            self._safe_print("Using rule-based detection as fallback")
            self.model = None
            return
        
        try:
            # Initialize model architecture exactly like working code
            import torchvision.models as models
            
            # Try loading state_dict first to check number of classes
            state_dict = torch.load(self.model_path, map_location=self.device)
            
            # Check if model has 4 classes (including Healthy) by inspecting fc.weight shape
            if isinstance(state_dict, dict):
                # Check fc layer shape to determine number of classes
                if 'fc.weight' in state_dict:
                    num_classes_in_model = state_dict['fc.weight'].shape[0]
                elif 'model.fc.weight' in state_dict:
                    num_classes_in_model = state_dict['model.fc.weight'].shape[0]
                else:
                    # Try to infer from any weight layer
                    num_classes_in_model = len(self.class_names)
            else:
                num_classes_in_model = len(self.class_names)
            
            # If model has 4 classes, add Healthy to class list
            if num_classes_in_model == 4 and len(self.class_names) == 3:
                self._safe_print("Model has 4 classes (including Healthy). Updating class list...")
                self.class_names = ['apple black rot', 'Apple Scab', 'Healthy', 'Powdery Mildew']
                # Update descriptions and mappings
                if 'Healthy' not in self.disease_descriptions:
                    self.disease_descriptions['Healthy'] = 'The leaf shows no signs of disease. The plant appears to be in good health with normal coloration and structure.'
                if 'Healthy' not in self.pesticide_map:
                    self.pesticide_map['Healthy'] = 'None'
            
            num_classes = len(self.class_names)
            self.model = models.resnet18(weights=None)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
            
            # Load trained weights - matching working code exactly
            self.model.load_state_dict(state_dict)
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self._safe_print(f"PyTorch model loaded successfully from: {os.path.abspath(self.model_path)}")
            self._safe_print(f"Model type: PyTorch ResNet18 (.pth format)")
            self._safe_print(f"Device: {self.device}")
            self._safe_print(f"Number of classes: {num_classes} ({', '.join(self.class_names)})")
                
        except FileNotFoundError:
            self._safe_print(f"ERROR: Model file not found at {self.model_path}")
            self._safe_print("Using rule-based detection as fallback")
            self.model = None
        except Exception as e:
            import traceback
            self._safe_print(f"ERROR: Could not load PyTorch model from {self.model_path}: {e}")
            self._safe_print(f"Error details: {traceback.format_exc()}")
            self._safe_print("Using rule-based detection as fallback")
            self.model = None
    
    def _safe_print(self, message):
        """Print message with UTF-8 encoding to avoid Unicode errors."""
        try:
            print(message)
        except UnicodeEncodeError:
            # Fallback: print without special characters
            import sys
            print(message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    
    def preprocess_image(self, image):
        """Preprocess image for PyTorch model input - matching working code exactly."""
        # Convert to PIL Image RGB - matching working code
        if isinstance(image, Image.Image):
            # Convert to RGB - matching working code: .convert('RGB')
            image = image.convert('RGB')
        else:
            # Convert numpy array to PIL Image
            if isinstance(image, np.ndarray):
                if len(image.shape) == 2:
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                elif image.shape[2] == 4:
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                image = Image.fromarray(image)
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
        
        # Apply PyTorch transforms - matching working code exactly
        img_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        return img_tensor
    
    def detect_disease(self, image):
        """Detect disease using PyTorch model - matching working code exactly."""
        try:
            if self.model is not None and isinstance(self.model, nn.Module):
                # Preprocess image - matching working code
                processed_image = self.preprocess_image(image)
                
                # Run inference - matching working code exactly
                with torch.no_grad():
                    outputs = self.model(processed_image)
                    
                    # Apply softmax - CRITICAL: Use outputs[0] and dim=0 like working code
                    probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                    
                    # Get prediction - matching working code
                    confidence, predicted_idx = torch.max(probabilities, 0)
                    predicted_class = self.class_names[predicted_idx.item()]
                    confidence_percent = confidence.item() * 100
                
                # Convert to numpy for all probabilities
                all_probabilities = probabilities.cpu().numpy()
                
                # Format all predictions
                all_predictions = []
                for i, class_name in enumerate(self.class_names):
                    prob_value = float(all_probabilities[i] * 100)
                    all_predictions.append({
                        'disease': self._format_class_name(class_name),
                        'confidence': prob_value
                    })
                
                # Sort by confidence (descending)
                all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
                
                # Format class name nicely (like working code)
                formatted_class = self._format_class_name(predicted_class)
                is_healthy = (formatted_class == 'Healthy')
                
            else:
                # Fallback to rule-based detection
                result = self._rule_based_detection(image)
                formatted_class = result['disease']
                confidence_percent = result['confidence']
                all_predictions = result['all_predictions']
                is_healthy = (formatted_class == 'Healthy')
            
            pesticide = self.pesticide_map.get(formatted_class, 'Unknown')
            pesticide_info = self.pesticide_details.get(pesticide, None)
            
            return {
                'disease': formatted_class,
                'confidence': confidence_percent,
                'is_healthy': is_healthy,
                'pesticide': pesticide,
                'pesticide_details': pesticide_info,
                'all_predictions': all_predictions
            }
            
        except Exception as e:
            import traceback
            print(f"Error in disease detection: {str(e)}")
            print(traceback.format_exc())
            return {
                'disease': 'Error',
                'confidence': 0.0,
                'is_healthy': False,
                'pesticide': 'N/A',
                'pesticide_details': None,
                'all_predictions': [],
                'error': str(e)
            }
    
    def _format_class_name(self, class_name):
        """Format class name nicely - matching working code logic."""
        formatted = class_name.title()
        if "black rot" in class_name.lower():
            formatted = "Apple Black Rot"
        elif "scab" in class_name.lower():
            formatted = "Apple Scab"
        elif "powdery mildew" in class_name.lower():
            formatted = "Powdery Mildew"
        return formatted
    
    def _rule_based_detection(self, image):
        """Fallback rule-based detection when model is not available."""
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        
        img_hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        green_mask = cv2.inRange(img_hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
        white_mask = cv2.inRange(img_hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))
        brown_mask = cv2.inRange(img_hsv, np.array([10, 100, 20]), np.array([20, 255, 200]))
        dark_brown_mask = cv2.inRange(img_hsv, np.array([0, 50, 0]), np.array([20, 255, 100]))
        
        green_ratio = np.count_nonzero(green_mask) / green_mask.size
        white_ratio = np.count_nonzero(white_mask) / white_mask.size
        brown_ratio = np.count_nonzero(brown_mask) / brown_mask.size
        dark_brown_ratio = np.count_nonzero(dark_brown_mask) / dark_brown_mask.size
        
        scores = {
            'Healthy': 0.0,
            'Apple Scab': 0.0,
            'Apple Black Rot': 0.0,
            'Powdery Mildew': 0.0
        }
        
        if green_ratio > 0.6 and white_ratio < 0.05 and brown_ratio < 0.05 and dark_brown_ratio < 0.05:
            scores['Healthy'] = 85.0
            scores['Powdery Mildew'] = 10.0
            scores['Apple Scab'] = 3.0
            scores['Apple Black Rot'] = 2.0
        elif white_ratio > 0.15:
            scores['Powdery Mildew'] = 75.0
            scores['Apple Scab'] = 15.0
            scores['Healthy'] = 5.0
            scores['Apple Black Rot'] = 5.0
        elif dark_brown_ratio > 0.1:
            scores['Apple Black Rot'] = 75.0
            scores['Apple Scab'] = 15.0
            scores['Healthy'] = 5.0
            scores['Powdery Mildew'] = 5.0
        elif brown_ratio > 0.1:
            scores['Apple Scab'] = 75.0
            scores['Apple Black Rot'] = 10.0
            scores['Healthy'] = 10.0
            scores['Powdery Mildew'] = 5.0
        else:
            scores['Healthy'] = 60.0
            scores['Apple Scab'] = 20.0
            scores['Apple Black Rot'] = 10.0
            scores['Powdery Mildew'] = 10.0
        
        disease_name = max(scores, key=scores.get)
        confidence = scores[disease_name]
        
        all_predictions = []
        for disease, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            all_predictions.append({
                'disease': disease,
                'confidence': score
            })
        
        return {
            'disease': disease_name,
            'confidence': confidence,
            'all_predictions': all_predictions
        }
    
    def get_disease_description(self, disease_name):
        return self.disease_descriptions.get(disease_name, 'No description available.')
