import random
import re
from crop_prediction import CropPredictor
from disease_detection import DiseaseDetector

class EnhancedFarmingChatbot:
    def __init__(self):
        self.conversation_history = []
        self.crop_predictor = CropPredictor()
        
        # Try to load disease detector, but don't fail if it errors
        try:
            self.disease_detector = DiseaseDetector()
        except Exception as e:
            print(f"Warning: Could not initialize DiseaseDetector: {e}")
            self.disease_detector = None
        
        # Extract crop names and info from predictor
        self.crop_info = self.crop_predictor.crop_info
        self.available_crops = list(self.crop_info.keys())
        
        # Nutrient ranges for different crops (for context-aware answers)
        self.crop_nutrient_preferences = {
            'rice': {'n': (50, 120), 'p': (20, 60), 'k': (30, 100), 'ph': (5.5, 7.0), 'rainfall': (150, 300), 'temp': (20, 35)},
            'maize': {'n': (60, 120), 'p': (25, 70), 'k': (40, 120), 'ph': (5.5, 7.5), 'rainfall': (50, 75), 'temp': (18, 27)},
            'wheat': {'n': (40, 100), 'p': (20, 60), 'k': (30, 80), 'ph': (6.0, 7.5), 'rainfall': (40, 80), 'temp': (15, 25)},
            'apple': {'n': (50, 100), 'p': (30, 70), 'k': (50, 120), 'ph': (5.5, 7.0), 'rainfall': (100, 125), 'temp': (20, 24)},
            'banana': {'n': (80, 150), 'p': (30, 80), 'k': (100, 200), 'ph': (6.0, 7.5), 'rainfall': (200, 250), 'temp': (25, 35)},
            'mango': {'n': (50, 100), 'p': (20, 60), 'k': (50, 120), 'ph': (5.5, 7.5), 'rainfall': (75, 200), 'temp': (24, 30)},
            'grapes': {'n': (40, 80), 'p': (25, 60), 'k': (60, 150), 'ph': (6.0, 7.0), 'rainfall': (50, 100), 'temp': (15, 30)},
            'cotton': {'n': (60, 120), 'p': (25, 70), 'k': (40, 100), 'ph': (6.0, 7.5), 'rainfall': (50, 100), 'temp': (21, 30)},
            'jute': {'n': (40, 100), 'p': (20, 60), 'k': (30, 80), 'ph': (6.0, 7.5), 'rainfall': (150, 250), 'temp': (24, 35)},
            'coffee': {'n': (40, 80), 'p': (20, 50), 'k': (50, 120), 'ph': (6.0, 6.5), 'rainfall': (150, 250), 'temp': (15, 24)},
            'chickpea': {'n': (20, 50), 'p': (15, 40), 'k': (20, 60), 'ph': (6.0, 7.5), 'rainfall': (40, 60), 'temp': (20, 30)},
            'lentil': {'n': (20, 50), 'p': (15, 40), 'k': (20, 60), 'ph': (6.0, 7.5), 'rainfall': (40, 60), 'temp': (18, 25)},
        }
        
        # Fertilizer recommendations by crop
        self.fertilizer_recommendations = {
            'rice': 'Apply 120-150 kg N/ha, 60-80 kg P2O5/ha, 60-80 kg K2O/ha. Use split application: 50% basal, 25% at tillering, 25% at panicle initiation. Urea (46% N) is commonly used.',
            'maize': 'Apply 120-180 kg N/ha, 60-80 kg P2O5/ha, 80-120 kg K2O/ha. Use balanced NPK (10-26-26) as basal, urea top-dressing at knee-high stage.',
            'wheat': 'Apply 100-120 kg N/ha, 60-80 kg P2O5/ha, 40-60 kg K2O/ha. Use DAP (18-46-0) for basal, urea for top-dressing.',
            'apple': 'Apply 80-120 kg N/ha, 40-60 kg P2O5/ha, 100-150 kg K2O/ha annually. Split into 3 applications: spring (40%), after harvest (30%), pre-winter (30%).',
            'banana': 'Apply 200-250 kg N/ha, 60-80 kg P2O5/ha, 300-400 kg K2O/ha. High potassium requirement. Apply monthly during active growth.',
            'mango': 'Apply 100-150 kg N/ha, 50-75 kg P2O5/ha, 100-150 kg K2O/ha. Apply in split doses: before flowering, after fruit set, post-harvest.',
            'grapes': 'Apply 60-100 kg N/ha, 40-60 kg P2O5/ha, 150-200 kg K2O/ha. High potassium for fruit quality. Apply pre-bloom and during fruit development.',
            'cotton': 'Apply 80-120 kg N/ha, 40-60 kg P2O5/ha, 40-60 kg K2O/ha. Split application: 50% basal, 25% at squaring, 25% at flowering.',
        }
        
        # Disease information - Updated for new 3-class model
        self.disease_info = {
            'apple black rot': {
                'symptoms': 'Dark, sunken lesions on fruit, leaves, and branches. Fruit may show black rot with concentric rings. Leaves develop brown spots that may lead to premature defoliation.',
                'cause': 'Fungal infection caused by Botryosphaeria obtusa',
                'pesticides': ['Captan', 'Mancozeb', 'Copper fungicides'],
                'prevention': 'Remove infected plant material, prune during dry weather, apply protective fungicides during warm, humid periods'
            },
            'apple scab': {
                'symptoms': 'Dark, olive-green to black spots on leaves and fruit. Leaves may become distorted and drop prematurely.',
                'cause': 'Fungal infection caused by Venturia inaequalis',
                'pesticides': ['Mancozeb', 'Captan', 'Myclobutanil'],
                'prevention': 'Remove fallen leaves, prune for air circulation, apply fungicides at green tip stage'
            },
            'powdery mildew': {
                'symptoms': 'White powdery coating on leaves, shoots, and sometimes fruit. Leaves may curl and become distorted.',
                'cause': 'Fungal infection caused by Podosphaera leucotricha',
                'pesticides': ['Sulfur', 'Myclobutanil', 'Tebuconazole'],
                'prevention': 'Prune infected shoots, ensure good air circulation, apply sulfur fungicide'
            },
            'leaf spot': {
                'symptoms': 'Small circular spots with dark borders on leaves',
                'cause': 'Various fungal pathogens',
                'pesticides': ['Copper fungicides', 'Mancozeb'],
                'prevention': 'Remove infected leaves, avoid overhead irrigation'
            }
        }
        
        # Pesticide information
        self.pesticide_info = {
            'mancozeb': 'Broad-spectrum protective fungicide. Apply 2-3 kg/ha of Mancozeb mixed with water. Spray Mancozeb at 10-14 day intervals for apple scab, rust, and leaf spots. Pre-harvest interval: 7-10 days.',
            'sulfur': 'Organic fungicide for powdery mildew. Apply 3-5 kg/ha of Sulfur as dust or wettable powder. Spray Sulfur at 7-10 day intervals. Do not apply when temperature exceeds 32°C.',
            'myclobutanil': 'Systemic fungicide for severe powdery mildew and scab. Apply 200-300 ml/ha of Myclobutanil mixed with water. Maximum 3 applications/season. PHI: 14 days.',
            'captan': 'Protective fungicide for apple black rot, apple scab, and fruit rots. Apply 2-3 kg/ha of Captan mixed with water. Spray Captan at 7-10 day intervals. Can be combined with other fungicides.',
            'copper': 'Broad-spectrum bactericide and fungicide. Effective for bacterial blight. Apply during dormancy or early spring.',
            'neem oil': 'Organic biopesticide for aphids, mites, and fungal diseases. Apply 3-5 ml/L. Safe for beneficial insects.',
            'pyrethrin': 'Natural insecticide from chrysanthemum. Effective against aphids, whiteflies, caterpillars. Low toxicity.',
        }
        
        # Water requirements by crop (liters/day/plant or mm/season)
        self.water_requirements = {
            'rice': '1200-1500 mm/season. Requires flooded conditions. 150-200 mm/week during active growth.',
            'maize': '500-800 mm/season. Critical periods: germination, tasseling, grain filling. Drip irrigation recommended.',
            'wheat': '450-650 mm/season. Most critical during tillering and flowering. Requires 4-6 irrigations.',
            'apple': '700-1000 mm/year. Requires consistent moisture. Drip irrigation at 40-80 liters/tree/day in summer.',
            'banana': '1500-2500 mm/year. High water requirement. Needs daily irrigation in hot months.',
            'cotton': '700-1300 mm/season. Deep watering preferred. Critical at flowering and boll development.',
        }
        
        # Pest control information
        self.pest_control = {
            'aphids': 'Natural: Neem oil spray, introduce ladybugs. Chemical: Imidacloprid, Thiamethoxam. Spray early morning.',
            'whiteflies': 'Natural: Yellow sticky traps, neem oil. Chemical: Spiromesifen, Pyriproxyfen. Target underside of leaves.',
            'caterpillars': 'Natural: Bt (Bacillus thuringiensis), handpicking. Chemical: Chlorantraniliprole. Apply at egg hatch stage.',
            'fruit flies': 'Natural: Pheromone traps, protein bait. Chemical: Spinosad. Sanitation is key - remove fallen fruit.',
            'termites': 'Natural: Neem cake in soil. Chemical: Chlorpyrifos, Imidacloprid as soil drench. Prevent by avoiding organic mulch near stems.',
        }
        
    def generate_reply(self, user_message):
        """Generate context-aware reply using project data."""
        user_message_lower = user_message.lower()
        
        # Check for greetings (must be standalone or at start of message)
        greeting_words = ['hello', 'hi ', 'hey ', 'greetings']
        if any(user_message_lower.strip().startswith(word) or user_message_lower == word.strip() for word in greeting_words):
            return "Hello! I'm your SmartCropSprayer AI assistant. I can help you with crop recommendations, soil analysis, disease detection, and farming guidance. Ask me about specific crops, soil conditions, or fertilizers!"
        
        # Check for thanks
        if any(word in user_message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! Feel free to ask more questions about farming, crops, or soil management."
        
        # 1. Disease detection questions
        if self._check_keywords(user_message_lower, ['disease', 'apple scab', 'powdery mildew', 'leaf spot', 'fungal', 'infection', 'detect', 'identify']):
            return self._answer_disease_question(user_message_lower)
        
        # 2. Pesticide recommendation questions
        if self._check_keywords(user_message_lower, ['pesticide', 'fungicide', 'insecticide', 'mancozeb', 'sulfur', 'myclobutanil', 'spray', 'chemical']):
            return self._answer_pesticide_question(user_message_lower)
        
        # 3. Water management questions
        if self._check_keywords(user_message_lower, ['water', 'irrigation', 'rainfall', 'drip', 'drought', 'waterlogging']):
            return self._answer_water_question(user_message_lower)
        
        # 4. Pest control questions
        if self._check_keywords(user_message_lower, ['pest', 'aphid', 'whitefly', 'caterpillar', 'termite', 'insect', 'pest control']):
            return self._answer_pest_question(user_message_lower)
        
        # 5. AI/Technology questions
        if self._check_keywords(user_message_lower, ['ai', 'model', 'algorithm', 'machine learning', 'accuracy', 'tensorflow', 'computer vision', 'technology']):
            return self._answer_technology_question(user_message_lower)
        
        # 6. Questions about crop suitability based on nutrient levels
        if self._check_keywords(user_message_lower, ['nitrogen', 'n level', 'low nitrogen', 'high nitrogen', 'nitrogen level']):
            return self._answer_nitrogen_question(user_message_lower)
        
        # 7. Questions about specific crop requirements (rice, wheat, maize, apple, etc.)
        crop_mentioned = self._extract_crop_name(user_message_lower)
        if crop_mentioned:
            return self._answer_crop_specific_question(user_message_lower, crop_mentioned)
        
        # 8. Questions about soil pH management
        if self._check_keywords(user_message_lower, ['ph', 'soil ph', 'ph level', 'manage ph', 'adjust ph']):
            return self._answer_ph_question(user_message_lower)
        
        # 9. Questions about fertilizers
        if self._check_keywords(user_message_lower, ['fertilizer', 'fertiliser', 'fertilization', 'npk', 'nutrient']):
            return self._answer_fertilizer_question(user_message_lower)
        
        # 10. Questions about crop recommendations
        if self._check_keywords(user_message_lower, ['recommend', 'suitable', 'best crop', 'which crop', 'what crop', 'grow']):
            return self._answer_recommendation_question(user_message_lower)
        
        # 11. Climate and season questions
        if self._check_keywords(user_message_lower, ['climate', 'weather', 'temperature', 'humidity', 'season', 'tropical', 'temperate']):
            return self._answer_climate_question(user_message_lower)
        
        # 12. Specific homepage questions
        if 'farming advice' in user_message_lower or 'get farming advice' in user_message_lower:
            return "Farming Advice:\n\nHere's comprehensive farming advice for successful agriculture:\n\n1. Soil Management:\n• Test your soil regularly (every 2-3 years)\n• Maintain optimal pH levels (6.0-7.0 for most crops)\n• Add organic matter (compost, manure) to improve fertility\n• Practice crop rotation to prevent nutrient depletion\n\n2. Crop Selection:\n• Use our Crop Recommendation tool with your soil data\n• Choose disease-resistant varieties when available\n• Consider local climate and growing seasons\n• Diversify crops to reduce risk\n\n3. Disease & Pest Control:\n• Monitor crops regularly for early signs of problems\n• Use our Disease Detection tool for apple plants\n• Practice Integrated Pest Management (IPM)\n• Apply pesticides only when necessary and at recommended dosages\n\n4. Water Management:\n• Use efficient irrigation methods (drip irrigation recommended)\n• Water during cool hours (morning/evening)\n• Mulch to conserve soil moisture\n• Monitor soil moisture levels\n\n5. Best Practices:\n• Follow proper spacing for optimal growth\n• Time operations correctly (planting, weeding, harvesting)\n• Keep records of practices and results\n• Stay updated with local agricultural extension services\n\nFor specific advice, ask about your crop, soil conditions, or farming challenges!"
        
        if 'best practices' in user_message_lower or 'learn best practices' in user_message_lower:
            return "Best Farming Practices:\n\n1. Soil Health:\n• Regular soil testing and balanced fertilization\n• Crop rotation to maintain soil fertility\n• Organic matter addition (compost, green manure)\n• Proper pH management (6.0-7.0 optimal for most crops)\n\n2. Crop Management:\n• Select suitable crops for your soil and climate\n• Use certified seeds from reliable sources\n• Proper spacing and timely planting\n• Weed management (mulching, timely weeding)\n\n3. Disease Prevention:\n• Choose disease-resistant crop varieties\n• Maintain field sanitation (remove infected plant parts)\n• Proper spacing for air circulation\n• Regular monitoring and early intervention\n• Use our AI Disease Detection tool for apple plants\n\n4. Pest Management:\n• Integrated Pest Management (IPM) approach\n• Biological controls (beneficial insects)\n• Organic pesticides when possible\n• Chemical pesticides as last resort with proper safety\n\n5. Water Efficiency:\n• Drip irrigation for water conservation\n• Rainwater harvesting where possible\n• Mulching to reduce evaporation\n• Monitor and adjust irrigation based on crop needs\n\n6. Sustainable Practices:\n• Crop diversification\n• Organic farming methods when feasible\n• Conservation tillage\n• Biodiversity promotion (beneficial insects, birds)\n\n7. Record Keeping:\n• Maintain records of inputs, yields, and practices\n• Track weather patterns and their effects\n• Document disease and pest occurrences\n• Learn from successes and challenges\n\nFor crop-specific practices, ask about your particular crop!"
        
        if 'treatments' in user_message_lower or 'ask about treatments' in user_message_lower:
            return "Disease and Pest Treatments:\n\nOur SmartCropSprayer system provides automated treatment recommendations:\n\n1. Disease Treatments:\n• Apple Black Rot: Apply 2-3 kg/ha of Captan mixed with water. Spray Captan at 7-10 day intervals.\n• Apple Scab: Apply 2-3 kg/ha of Mancozeb mixed with water. Spray Mancozeb at 10-14 day intervals.\n• Powdery Mildew: Apply 3-5 kg/ha of Sulfur (organic) or 200-300 ml/ha of Myclobutanil. Spray at 7-10 day intervals.\n\nHow to Use:\n• Upload images at /disease-detection\n• AI identifies the disease automatically\n• Get instant pesticide recommendations with:\n  - Recommended pesticide name\n  - Dosage and application method (what to spray)\n  - Timing and frequency\n  - Safety precautions\n\n2. Pest Treatments:\n• Aphids: Neem oil or ladybugs (biological control)\n• Whiteflies: Yellow sticky traps + neem oil\n• Caterpillars: Bt (Bacillus thuringiensis)\n• Fruit Flies: Pheromone traps + Spinosad\n• Termites: Neem cake in soil or soil drench\n\n3. General Treatment Guidelines:\n• Always identify the problem first (use our AI tools)\n• Start with preventive measures\n• Use organic/natural treatments when possible\n• Apply chemical treatments at recommended dosages\n• Follow safety precautions (PPE, PHI, storage)\n• Rotate treatments to prevent resistance\n\n4. Treatment Timing:\n• Preventive: Apply before disease/pest appears\n• Curative: Apply at first sign of problem\n• Best time: Early morning or evening\n• Avoid: During flowering (protect pollinators)\n\nFor specific treatments, ask about your disease or pest problem, or use our Disease Detection tool!"
        
        # 13. General farming questions - use enhanced knowledge
        return self._answer_general_farming_question(user_message_lower)
    
    def _check_keywords(self, text, keywords):
        """Check if any keyword is in the text."""
        return any(keyword in text for keyword in keywords)
    
    def _extract_crop_name(self, text):
        """Extract crop name from text."""
        for crop in self.available_crops:
            # Check for crop name and common variations
            crop_variations = [
                crop,
                crop.replace('peas', 'pea'),
                crop.replace('beans', 'bean'),
                crop.replace('grams', 'gram')
            ]
            if any(variation in text for variation in crop_variations):
                return crop
        
        # Check for common crop names that might not be in exact match
        crop_keywords = {
            'rice': 'rice',
            'wheat': None,  # Not in dataset but provide info
            'maize': 'maize',
            'corn': 'maize',
            'apple': 'apple',
            'banana': 'banana',
            'mango': 'mango',
            'cotton': 'cotton',
            'jute': 'jute',
            'coffee': 'coffee',
            'grapes': 'grapes',
            'potato': None,
            'tomato': None,
        }
        
        for keyword, crop_name in crop_keywords.items():
            if keyword in text:
                return crop_name if crop_name else keyword  # Return keyword even if not in dataset
        
        return None
    
    def _answer_nitrogen_question(self, text):
        """Answer questions about nitrogen levels and crop suitability."""
        is_low = any(word in text for word in ['low', 'less', 'deficient', 'lacking'])
        is_high = any(word in text for word in ['high', 'too much', 'excess', 'excessive'])
        
        if is_low:
            # Crops that can tolerate low nitrogen (legumes, some pulses)
            low_n_crops = ['chickpea', 'lentil', 'mothbeans', 'mungbean', 'blackgram', 'pigeonpeas', 'kidneybeans']
            crops_info = '\n'.join([f"• {crop.capitalize()}: {self.crop_info[crop][:80]}..." for crop in low_n_crops if crop in self.crop_info])
            return f"For low nitrogen levels (below 50 kg/ha):\n\nLegumes and pulses are excellent choices as they fix atmospheric nitrogen:\n\n{crops_info}\n\nThese crops have symbiotic relationships with nitrogen-fixing bacteria, reducing fertilizer needs. You can also apply organic nitrogen sources like compost or farmyard manure at 10-15 tons/ha."
        
        elif is_high:
            # Crops that benefit from high nitrogen (cereals, leafy vegetables)
            high_n_crops = ['rice', 'maize', 'jute', 'banana']
            crops_info = '\n'.join([f"• {crop.capitalize()}: {self.crop_info[crop][:80]}..." for crop in high_n_crops if crop in self.crop_info])
            return f"For high nitrogen levels (above 80 kg/ha):\n\nCereals and high-biomass crops benefit from high nitrogen:\n\n{crops_info}\n\nThese crops have high nitrogen requirements. However, ensure balanced NPK application to avoid nutrient imbalances. Excessive nitrogen can delay maturity and reduce quality in some crops."
        
        else:
            return "Nitrogen Level Guidelines:\n\n• Low N (20-50 kg/ha): Suitable for legumes (chickpea, lentil, beans) that fix nitrogen\n• Moderate N (50-80 kg/ha): Good for most crops including maize, cotton\n• High N (80-150 kg/ha): Ideal for rice, banana, jute, and high-yield cereals\n\nWould you like specific recommendations for your nitrogen level? Provide your soil N, P, K, pH, temperature, humidity, and rainfall values!"
    
    def _answer_crop_specific_question(self, text, crop_name):
        """Answer questions about specific crops."""
        # Check what aspect they're asking about
        if self._check_keywords(text, ['grow', 'cultivate', 'plant', 'efficient', 'suitable', 'requirements']):
            if crop_name in self.crop_info:
                info = self.crop_info[crop_name]
                
                # Get nutrient preferences if available
                nutrient_info = ""
                if crop_name in self.crop_nutrient_preferences:
                    prefs = self.crop_nutrient_preferences[crop_name]
                    nutrient_info = f"\n\nOptimal Soil Conditions:\n• Nitrogen: {prefs['n'][0]}-{prefs['n'][1]} kg/ha\n• Phosphorus: {prefs['p'][0]}-{prefs['p'][1]} kg/ha\n• Potassium: {prefs['k'][0]}-{prefs['k'][1]} kg/ha\n• pH: {prefs['ph'][0]}-{prefs['ph'][1]}\n• Rainfall: {prefs['rainfall'][0]}-{prefs['rainfall'][1]} cm/year\n• Temperature: {prefs['temp'][0]}-{prefs['temp'][1]}°C"
                
                return f"{crop_name.capitalize()} Growing Guide:\n\n{info}{nutrient_info}"
            else:
                return f"I don't have detailed information about {crop_name} in my database. However, I can help you with: {', '.join(self.available_crops[:10])}. Would you like information about any of these crops?"
        
        elif self._check_keywords(text, ['fertilizer', 'fertilisation', 'npk', 'nutrient']):
            if crop_name in self.fertilizer_recommendations:
                return f"Fertilizer Recommendations for {crop_name.capitalize()}:\n\n{self.fertilizer_recommendations[crop_name]}\n\nFor precise recommendations, provide your soil test results (N, P, K, pH) and environmental conditions."
            else:
                # Generic fertilizer advice based on crop type
                if crop_name in ['rice', 'maize', 'wheat']:
                    return f"For {crop_name.capitalize()} (Cereal Crop):\n\nApply balanced NPK fertilizer:\n• Nitrogen: 100-150 kg/ha\n• Phosphorus: 60-80 kg/ha\n• Potassium: 60-100 kg/ha\n\nUse split application: 50% basal at planting, 25% at tillering/growth stage, 25% at reproductive stage.\n\nFor specific recommendations, use our Crop Recommendation tool with your soil parameters!"
                elif crop_name in ['apple', 'mango', 'banana']:
                    return f"For {crop_name.capitalize()} (Fruit Tree):\n\nAnnual fertilizer requirements:\n• Nitrogen: 100-150 kg/ha\n• Phosphorus: 50-75 kg/ha\n• Potassium: 100-200 kg/ha (higher for banana)\n\nApply in 3 split doses: before flowering (40%), after fruit set (30%), post-harvest (30%).\n\nFor precise recommendations, provide your soil test results!"
        
        # Default crop info
        if crop_name in self.crop_info:
            return f"{crop_name.capitalize()} Information:\n\n{self.crop_info[crop_name]}\n\nWhat specific aspect of {crop_name} farming would you like to know about?"
        
        return f"I can help you with information about {crop_name}. What specifically would you like to know - growing requirements, fertilizer needs, or soil conditions?"
    
    def _answer_ph_question(self, text):
        """Answer questions about soil pH management."""
        crop_mentioned = self._extract_crop_name(text)
        
        if crop_mentioned and crop_mentioned in self.crop_nutrient_preferences:
            prefs = self.crop_nutrient_preferences[crop_mentioned]
            ph_range = prefs['ph']
            info = self.crop_info.get(crop_mentioned, '')
            
            return f"Soil pH Management for {crop_mentioned.capitalize()}:\n\nOptimal pH Range: {ph_range[0]}-{ph_range[1]}\n\n{info}\n\npH Adjustment:\n• To increase pH (make less acidic): Apply agricultural lime (CaCO3) at 2-4 tons/ha\n• To decrease pH (make more acidic): Apply elemental sulfur or aluminum sulfate\n• Test soil pH annually before planting season\n• pH changes take 3-6 months, so plan ahead!"
        
        return "Soil pH Management:\n\nMost crops prefer pH 6.0-7.0. Here are optimal ranges:\n\n• Acidic (5.5-6.5): Rice, coffee, tea, blueberries\n• Neutral (6.0-7.0): Maize, wheat, most vegetables, apple\n• Slightly Alkaline (7.0-7.5): Cotton, some legumes\n\nTo raise pH: Apply lime (2-4 tons/ha)\nTo lower pH: Apply sulfur (500-1000 kg/ha)\n\nWhich crop are you planning to grow? I can provide specific pH recommendations!"
    
    def _answer_fertilizer_question(self, text):
        """Answer questions about fertilizers."""
        crop_mentioned = self._extract_crop_name(text)
        
        if crop_mentioned and crop_mentioned in self.fertilizer_recommendations:
            return f"Fertilizer Recommendations for {crop_mentioned.capitalize()}:\n\n{self.fertilizer_recommendations[crop_mentioned]}\n\nTip: For precise recommendations, use our Crop Recommendation tool with your actual soil test values (N, P, K, pH, temperature, humidity, rainfall)."
        
        if 'apple' in text:
            return "Fertilizer for Apple Farming:\n\nApply annually:\n• Nitrogen: 80-120 kg/ha (split into 3 applications)\n• Phosphorus: 40-60 kg P2O5/ha (applied pre-winter)\n• Potassium: 100-150 kg K2O/ha (critical for fruit quality)\n\nApplication Schedule:\n1. Spring (40%): Before flowering for growth\n2. Post-harvest (30%): After harvest for tree recovery\n3. Pre-winter (30%): Before dormancy for next season\n\nDisease Prevention: Use our Disease Detection tool to monitor apple leaf diseases and get pesticide recommendations!"
        
        return "Fertilizer Guidelines:\n\n• NPK Balance: Most crops need balanced NPK. The ratio depends on crop type:\n  - Cereals (rice, wheat, maize): Higher N requirement\n  - Fruits (apple, mango): Higher K for quality\n  - Legumes: Lower N (they fix nitrogen)\n\n• Application: Split doses for better efficiency\n• Organic Options: Compost, farmyard manure, green manure\n\nFor specific recommendations, tell me which crop you're growing or use our Crop Recommendation tool!"
    
    def _answer_recommendation_question(self, text):
        """Answer questions about crop recommendations."""
        # Try to extract soil parameters from text
        params = self._extract_soil_parameters(text)
        
        if params and len(params) >= 4:
            # Use actual crop predictor
            recommendations = self.crop_predictor.get_top_recommendations(
                params.get('n', 50),
                params.get('p', 50),
                params.get('k', 50),
                params.get('temp', 25),
                params.get('humidity', 65),
                params.get('ph', 6.5),
                params.get('rainfall', 100),
                top_n=3
            )
            
            result = "Top Crop Recommendations:\n\n"
            for i, rec in enumerate(recommendations, 1):
                result += f"{i}. {rec['crop'].capitalize()} (Match: {rec['confidence']:.1f}%)\n{rec['info']}\n\n"
            result += "Tip: Use our Crop Recommendation tool for detailed analysis!"
            return result
        
        return "Crop Recommendations:\n\nTo get precise crop recommendations, I need your soil and environmental parameters:\n\n• Soil Nutrients: Nitrogen (N), Phosphorus (P), Potassium (K) in kg/ha\n• Soil pH: pH level (typically 5.5-7.5)\n• Temperature: Average temperature in °C\n• Humidity: Relative humidity in %\n• Rainfall: Annual or seasonal rainfall in mm\n\nYou can:\n1. Use our Crop Recommendation page with your soil test results\n2. Ask me: 'Which crop for N=50, P=40, K=60, pH=6.5, temp=25, humidity=70, rainfall=150?'\n\nI'll analyze and recommend the best crops for your conditions!"
    
    def _extract_soil_parameters(self, text):
        """Extract soil parameters from text if mentioned."""
        params = {}
        
        # Try to extract numbers with context
        n_match = re.search(r'n[=:]?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if n_match:
            params['n'] = float(n_match.group(1))
        
        p_match = re.search(r'p[=:]?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if p_match:
            params['p'] = float(p_match.group(1))
        
        k_match = re.search(r'k[=:]?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if k_match:
            params['k'] = float(k_match.group(1))
        
        ph_match = re.search(r'ph[=:]?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if ph_match:
            params['ph'] = float(ph_match.group(1))
        
        temp_match = re.search(r'temp(?:erature)?[=:]?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if temp_match:
            params['temp'] = float(temp_match.group(1))
        
        return params
    
    def _answer_disease_question(self, text):
        """Answer disease detection questions."""
        # Handle comparison questions
        if 'difference between' in text.lower():
            if 'apple black rot' in text.lower() and 'apple scab' in text.lower():
                return "Difference Between Apple Black Rot and Apple Scab:\n\nApple Black Rot:\n• Caused by: Botryosphaeria obtusa\n• Symptoms: Dark, sunken lesions on fruit, leaves, and branches. Fruit shows black rot with concentric rings.\n• Spread: Warm, humid weather\n• Treatment: Captan or Mancozeb fungicides\n\nApple Scab:\n• Caused by: Venturia inaequalis\n• Symptoms: Dark, olive-green to black spots on leaves and fruit. Leaves may become distorted.\n• Spread: Cool, wet spring weather\n• Treatment: Mancozeb or Captan fungicides\n\nKey Difference: Black rot affects fruit more severely with sunken lesions, while scab primarily causes leaf distortion and spots. Both are fungal diseases but require different timing for prevention.\n\nTip: Upload images to /disease-detection for accurate AI-powered identification!"
            
            if ('black rot' in text.lower() and 'powdery mildew' in text.lower()) or ('powdery mildew' in text.lower() and 'black rot' in text.lower()):
                return "Difference Between Apple Black Rot and Powdery Mildew:\n\nApple Black Rot:\n• Symptoms: Dark, sunken lesions on fruit and leaves\n• Appearance: Black/brown spots with concentric rings\n• Cause: Botryosphaeria obtusa fungus\n• Weather: Favors warm, humid conditions\n• Treatment: Captan fungicide\n\nPowdery Mildew:\n• Symptoms: White powdery coating on leaves and shoots\n• Appearance: White, fluffy patches\n• Cause: Podosphaera leucotricha fungus\n• Weather: Can occur in various conditions\n• Treatment: Sulfur (organic) or Myclobutanil\n\nKey Difference: Black rot shows dark sunken lesions while powdery mildew shows white powdery coating. Visual appearance is the easiest way to distinguish them.\n\nTip: Use our AI Disease Detection tool for instant identification!"
        
        # Handle old stage questions - redirect to current model
        if ('stage' in text.lower() or 'stages' in text.lower()) and 'powdery mildew' in text.lower():
            return "Powdery Mildew Disease:\n\nOur AI model detects Powdery Mildew as a single category. The disease appears as a white, powdery coating on leaves, shoots, and sometimes fruit. Leaves may curl and become distorted.\n\nCause: Fungal infection caused by Podosphaera leucotricha\n\nRecommended Pesticides: Sulfur (organic), Myclobutanil, or Tebuconazole\n\nPrevention: Prune infected shoots, ensure good air circulation, apply sulfur fungicide\n\nTip: Upload images at /disease-detection for instant AI-powered diagnosis and automatic pesticide recommendations!"
        
        # Check for specific diseases
        if 'apple black rot' in text or ('black rot' in text and 'apple' in text):
            info = self.disease_info['apple black rot']
            return f"Apple Black Rot Disease:\n\nSymptoms: {info['symptoms']}\n\nCause: {info['cause']}\n\nRecommended Pesticides: {', '.join(info['pesticides'])}\n\nPrevention: {info['prevention']}\n\nTip: Upload images to our Disease Detection page for AI-powered diagnosis and automatic pesticide recommendations!"
        
        if 'apple scab' in text or 'scab' in text:
            info = self.disease_info['apple scab']
            return f"Apple Scab Disease:\n\nSymptoms: {info['symptoms']}\n\nCause: {info['cause']}\n\nRecommended Pesticides: {', '.join(info['pesticides'])}\n\nPrevention: {info['prevention']}\n\nTip: Upload images to our Disease Detection page for AI-powered diagnosis and automatic pesticide recommendations!"
        
        if 'powdery mildew' in text:
            info = self.disease_info['powdery mildew']
            return f"Powdery Mildew Disease:\n\nSymptoms: {info['symptoms']}\n\nCause: {info['cause']}\n\nRecommended Pesticides: {', '.join(info['pesticides'])}\n\nPrevention: {info['prevention']}\n\nTip: Upload images at /disease-detection for instant AI-powered diagnosis!"
        
        if 'leaf spot' in text:
            info = self.disease_info['leaf spot']
            return f"Leaf Spot Disease:\n\nSymptoms: {info['symptoms']}\n\nCause: {info['cause']}\n\nRecommended Pesticides: {', '.join(info['pesticides'])}\n\nPrevention: {info['prevention']}"
        
        # General disease detection info
        if any(word in text for word in ['detect', 'identify', 'camera', 'image', 'upload', 'photo']):
            return "AI Disease Detection:\n\nOur system uses computer vision and deep learning to detect apple leaf diseases:\n\n• Detectable Diseases: Apple Black Rot, Apple Scab, Powdery Mildew\n• Accuracy: 90%+ with clear images\n• Works Offline: No internet required\n• Instant Results: Detection in under 2 seconds\n• Auto Pesticide Recommendation: Suggests treatment based on detected disease\n\nHow to use:\n1. Go to /disease-detection\n2. Upload clear leaf image (JPG/PNG)\n3. Get instant diagnosis + pesticide recommendations\n\nTip: Take photos in good lighting, avoid blurry images!"
        
        return "Disease Management:\n\nOur SmartCropSprayer system can detect and diagnose:\n• Apple Black Rot\n• Apple Scab\n• Powdery Mildew\n• Leaf Spot diseases\n• Healthy vs diseased leaves\n\nFor AI diagnosis: Upload images at /disease-detection\nFor prevention tips: Ask about specific diseases\nFor treatment: Automatic pesticide recommendations provided!"
    
    def _answer_pesticide_question(self, text):
        """Answer pesticide recommendation questions."""
        # Check for specific pesticides
        for pesticide_name, info in self.pesticide_info.items():
            if pesticide_name in text:
                return f"{pesticide_name.capitalize()} Pesticide:\n\n{info}\n\nSafety: Always wear protective equipment, follow label instructions, and observe pre-harvest intervals (PHI)."
        
        # Check for disease-specific pesticide recommendations
        if 'apple black rot' in text or ('black rot' in text and 'apple' in text):
            return "Pesticides for Apple Black Rot:\n\n1. Captan (Protective): Apply 2-3 kg/ha of Captan mixed with water. Spray Captan at 7-10 day intervals, especially during warm, humid periods. Effective against black rot.\n2. Mancozeb (Protective): Apply 2-3 kg/ha of Mancozeb mixed with water. Spray Mancozeb at 10-14 day intervals. Broad-spectrum protection.\n3. Copper fungicides: For organic control, apply copper fungicides during warm, humid weather\n\nApplication: Start before symptoms appear for best results. Apply during warm, humid periods when disease pressure is high.\n\nOur AI automatically recommends pesticides when you upload images!"
        
        if 'apple scab' in text or 'scab' in text:
            return "Pesticides for Apple Scab:\n\n1. Mancozeb (Protective): Apply 2-3 kg/ha of Mancozeb mixed with water. Spray Mancozeb at 10-14 day intervals during wet periods. PHI: 7-10 days.\n2. Captan (Protective): Apply 2-3 kg/ha of Captan mixed with water. Spray Captan at 7-10 day intervals. Good for wet conditions.\n3. Myclobutanil (Systemic): Apply 200-300 ml/ha of Myclobutanil mixed with water. For existing infections.\n\nApplication: Start at green tip stage, repeat every 10-14 days during wet weather.\n\nOur AI automatically recommends pesticides when you upload images!"
        
        if 'powdery mildew' in text:
            return "Pesticides for Powdery Mildew:\n\n1. Sulfur (Organic): Apply 3-5 kg/ha of Sulfur as dust or wettable powder. Spray Sulfur at 7-10 day intervals. Safe for beneficial insects. Do not apply when temperature exceeds 32°C.\n2. Myclobutanil (Systemic): Apply 200-300 ml/ha of Myclobutanil mixed with water. For severe infections.\n3. Tebuconazole: Apply 250 ml/ha of Tebuconazole mixed with water. Similar to Myclobutanil.\n\nApplication: Spray at first sign of white powdery growth.\n\nGet automatic recommendations: Upload images to our Disease Detection tool!"
        
        # Organic alternatives
        if any(word in text for word in ['organic', 'natural', 'eco-friendly', 'biological']):
            return "Organic Pesticide Alternatives:\n\n1. Neem Oil: 3-5 ml/L for aphids, mites, fungal diseases\n2. Sulfur: Organic fungicide for powdery mildew\n3. Copper Fungicides: For bacterial and fungal diseases\n4. Bt (Bacillus thuringiensis): For caterpillars\n5. Pyrethrin: Natural insecticide for various pests\n6. Garlic/Chili Spray: Homemade pest repellent\n\nBenefits: Safe for beneficial insects, no chemical residues, suitable for organic certification.\n\nNote: Organic pesticides may require more frequent applications than synthetic options."
        
        # General pesticide info
        if any(word in text for word in ['dosage', 'application', 'timing', 'how often']):
            return "Pesticide Application Guidelines:\n\nDosage:\n• Follow label instructions exactly\n• Adjust for tree size and disease severity\n• Use calibrated equipment for accuracy\n\nTiming:\n• Preventive: Apply before disease appears (e.g., green tip stage)\n• Curative: Apply at first sign of disease\n• Avoid spraying during flowering (protects pollinators)\n• Best time: Early morning or evening\n\nFrequency:\n• Protective fungicides: Every 7-14 days\n• Systemic fungicides: Every 14-21 days\n• After rainfall: Reapply protective fungicides\n\nSafety:\n• Wear PPE: Gloves, mask, goggles, long sleeves\n• Observe Pre-Harvest Interval (PHI)\n• Keep away from water sources\n• Store in original containers\n\nGet AI-powered recommendations: Use our Disease Detection tool!"
        
        return "Pesticide Recommendations:\n\nOur system provides automatic pesticide suggestions based on detected diseases:\n\nAvailable Options:\n• Captan - Apple black rot, apple scab, fruit rots\n• Mancozeb - Apple scab, leaf spots, black rot\n• Sulfur - Powdery mildew (organic)\n• Myclobutanil - Severe fungal infections\n• Neem Oil - Organic multi-purpose\n\nFor specific recommendations:\n1. Upload images to /disease-detection\n2. AI detects disease automatically\n3. Get pesticide suggestions with dosage and safety info\n\nAsk about specific pesticides for detailed information!"
    
    def _answer_water_question(self, text):
        """Answer water management questions."""
        # Check for specific crop water requirements
        crop_mentioned = self._extract_crop_name(text)
        if crop_mentioned and crop_mentioned in self.water_requirements:
            req = self.water_requirements[crop_mentioned]
            return f"Water Requirements for {crop_mentioned.capitalize()}:\n\n{req}\n\nTips:\n• Use drip irrigation for water efficiency\n• Mulch to reduce evaporation\n• Water deeply but less frequently\n• Monitor soil moisture regularly\n• Critical periods: flowering, fruit development"
        
        # Irrigation methods
        if 'drip' in text or 'sprinkler' in text or 'irrigation method' in text:
            return "Irrigation Methods Comparison:\n\nDrip Irrigation (Recommended):\n• 90% water efficiency\n• Delivers water directly to roots\n• Reduces disease (no wet foliage)\n• Cost: Moderate initial investment\n• Best for: Orchards, vegetables, water-scarce areas\n\nSprinkler Irrigation:\n• 70-80% efficiency\n• Good for large areas\n• Can increase disease risk\n• Best for: Field crops, lawns\n\nFlood Irrigation:\n• 40-60% efficiency\n• Low cost, simple\n• High water wastage\n• Best for: Rice, low-tech farming\n\nOur Crop Recommendation tool considers rainfall patterns for better planning!"
        
        # Drought management
        if 'drought' in text:
            return "Drought Management Strategies:\n\nCrop Selection:\n• Choose drought-resistant crops (millet, sorghum, chickpea)\n• Our AI can recommend crops based on low rainfall conditions\n\nWater Conservation:\n• Mulching reduces evaporation by 50%\n• Drip irrigation saves 40-60% water\n• Deep, infrequent watering encourages deep roots\n• Harvest rainwater in storage tanks\n\nSoil Management:\n• Add organic matter to improve water retention\n• Reduce tillage to preserve soil moisture\n• Use cover crops to prevent evaporation\n\nFor crop recommendations in low-rainfall areas, use our Crop Recommendation tool with your rainfall data!"
        
        # Waterlogging
        if 'waterlog' in text or 'excess water' in text or 'too much water' in text:
            return "Waterlogging Prevention & Management:\n\nCauses:\n• Poor drainage\n• Over-irrigation\n• Heavy rainfall + clay soil\n• Flat terrain\n\nEffects:\n• Root rot and oxygen deprivation\n• Nutrient leaching\n• Increased disease susceptibility\n\nSolutions:\n• Install drainage systems (tile drains, ditches)\n• Raise beds or ridges for planting\n• Improve soil structure with organic matter\n• Select flood-tolerant crops (rice, taro)\n• Avoid over-irrigation\n\nPreventive Measures:\n• Soil testing before planting\n• Proper field grading and leveling\n• Use raised bed cultivation"
        
        return "Water Management:\n\nEfficient water use is critical for sustainable farming:\n\nStrategies:\n• Use drip irrigation (saves 40-60% water)\n• Mulch to reduce evaporation\n• Water during cool hours (morning/evening)\n• Monitor soil moisture with sensors\n• Apply water based on crop stage\n\nCrop Water Requirements:\n• Rice: High (1200-1500 mm/season)\n• Maize: Moderate (500-800 mm)\n• Wheat: Moderate (450-650 mm)\n• Apple: Moderate-High (700-1000 mm/year)\n\nOur Crop Recommendation tool considers rainfall patterns to suggest suitable crops!\n\nAsk about specific crops for detailed water requirements."
    
    def _answer_pest_question(self, text):
        """Answer pest control questions."""
        # Check for specific pests
        for pest_name, control_info in self.pest_control.items():
            if pest_name in text:
                return f"{pest_name.capitalize()} Control:\n\n{control_info}\n\nIPM Approach: Combine cultural (crop rotation, sanitation), biological (natural predators), and chemical controls for best results.\n\nTip: Early detection is key! Monitor crops regularly for pest activity."
        
        # Organic pest control
        if any(word in text for word in ['organic', 'natural', 'biological', 'without chemical']):
            return "Organic Pest Control Methods:\n\nBiological Controls:\n• Ladybugs for aphids (release 1500-3000/acre)\n• Parasitic wasps for caterpillars\n• Bacillus thuringiensis (Bt) for moth larvae\n• Nematodes for soil pests\n\nBotanical Pesticides:\n• Neem oil: 3-5 ml/L for aphids, mites, whiteflies\n• Pyrethrin: From chrysanthemum, for flying insects\n• Garlic spray: Repellent for many pests\n• Chili spray: Effective against caterpillars\n\nCultural Practices:\n• Crop rotation breaks pest cycles\n• Companion planting (marigolds repel aphids)\n• Trap crops attract pests away from main crop\n• Mulching suppresses soil pests\n\nPhysical Methods:\n• Yellow sticky traps for whiteflies\n• Pheromone traps for fruit flies\n• Row covers to exclude insects\n• Handpicking for large pests\n\nThese methods are safer for beneficial insects and the environment!"
        
        # Integrated Pest Management
        if 'ipm' in text or 'integrated pest management' in text:
            return "Integrated Pest Management (IPM):\n\nIPM is a comprehensive approach combining multiple strategies:\n\n1. Prevention:\n• Select pest-resistant varieties\n• Maintain healthy soil and plants\n• Proper spacing for air circulation\n• Crop rotation\n\n2. Monitoring:\n• Regular scouting for pests\n• Use traps and monitoring tools\n• Keep records of pest populations\n• Identify beneficial insects\n\n3. Threshold-based Action:\n• Apply control only when pest levels exceed economic threshold\n• Don't aim for 100% pest elimination\n\n4. Control Methods (in order):\n• Cultural: Sanitation, crop rotation\n• Biological: Natural predators, parasites\n• Physical: Traps, barriers, hand removal\n• Chemical: As last resort, use selective pesticides\n\nBenefits:\n• Reduced pesticide use (40-50%)\n• Lower costs long-term\n• Protects beneficial insects\n• Environmentally sustainable\n• Prevents pest resistance"
        
        return "Pest Control:\n\nOur system supports comprehensive pest management:\n\nCommon Pests:\n• Aphids: Neem oil or ladybugs\n• Whiteflies: Yellow traps + neem oil\n• Caterpillars: Bt (Bacillus thuringiensis)\n• Fruit Flies: Pheromone traps\n• Termites: Neem cake in soil\n\nControl Strategies:\n1. Prevention (best approach)\n2. Early detection (monitor regularly)\n3. Biological control (natural predators)\n4. Organic pesticides (neem, pyrethrin)\n5. Chemical pesticides (last resort)\n\nIntegrated Pest Management (IPM) combines all methods for sustainable, effective control.\n\nAsk about specific pests for targeted control strategies!"
    
    def _answer_technology_question(self, text):
        """Answer AI and technology questions."""
        if any(word in text for word in ['how', 'work', 'predict', 'detect', 'algorithm']):
            if 'crop' in text or 'recommendation' in text:
                return "AI Crop Prediction Technology:\n\nAlgorithm: Random Forest Classifier\n• Trained on 2200+ real farm data samples\n• Considers 7 parameters: N, P, K, pH, temperature, humidity, rainfall\n• Accuracy: 92-95% on test data\n\nHow it works:\n1. You provide soil and climate parameters\n2. AI compares with 22 crop requirement profiles\n3. Ranks crops by suitability score\n4. Returns top 3 recommendations with confidence levels\n\nFeatures:\n• Offline processing (no internet needed)\n• Instant results (<1 second)\n• Scientific crop information for each recommendation\n• Considers regional climate and soil type\n\nTry it at: /crop-prediction"
            
            if 'disease' in text or 'detection' in text or 'image' in text:
                return "AI Disease Detection Technology:\n\nModel: Deep Learning CNN (ResNet18 Architecture)\n• Format: PyTorch (.pth format)\n• Input: 224x224 RGB images\n• Output: 3 classes (Apple Black Rot, Apple Scab, Powdery Mildew)\n• Accuracy: 90%+ with clear images\n\nHow it works:\n1. Upload leaf image (JPG/PNG)\n2. Image preprocessed (resized, normalized with ImageNet stats)\n3. CNN extracts visual features (spots, patterns, colors)\n4. Classifies disease with confidence score\n5. Automatically suggests appropriate pesticide\n\nAdvantages:\n• Computer Vision: Analyzes visual patterns humans might miss\n• Offline Processing: Works without internet\n• Fast: Results in under 2 seconds\n• Precise: Accurately identifies three common apple diseases\n\nTry it at: /disease-detection"
        
        if 'offline' in text:
            return "Offline AI Capabilities:\n\nYes! SmartCropSprayer works completely offline:\n\nCrop Prediction:\n• Uses local Random Forest model (saved as .pkl file)\n• All 22 crop profiles stored locally\n• Instant recommendations without internet\n\nDisease Detection:\n• PyTorch model (ResNet18, .pth format)\n• Processes images on your device\n• No cloud upload required\n\nChatbot:\n• Enhanced offline mode with farming knowledge base\n• Rule-based responses + crop/disease data integration\n• Context-aware answers without API calls\n\nBenefits:\n• Works in remote areas with no connectivity\n• Faster processing (no network latency)\n• Privacy: Your data never leaves your device\n• No data charges\n\nNote: Online mode (with GPT) available if API key configured."
        
        if 'accuracy' in text:
            return "AI Model Accuracy:\n\nCrop Recommendation Model:\n• Overall Accuracy: 92-95%\n• Algorithm: Random Forest (ensemble method)\n• Training Data: 2200+ samples\n• Validation: Cross-validation + test set\n• Continuous improvement with more data\n\nDisease Detection Model:\n• Overall Accuracy: 90%+\n• Best Performance: Clear, well-lit images\n• Classes: 3 (Apple Black Rot, Apple Scab, Powdery Mildew)\n• Technology: Deep CNN ResNet18 (PyTorch)\n\nFactors Affecting Accuracy:\n• Image Quality: Clear, focused images = better results\n• Lighting: Natural daylight preferred\n• Disease Severity: Clear symptoms improve detection\n• Soil Data Quality: Accurate test results = better recommendations\n\nTips for Best Results:\n• Use calibrated soil testing kits\n• Take multiple leaf photos from different angles\n• Provide complete environmental data"
        
        if 'integrate' in text or 'iot' in text or 'sensor' in text:
            return "IoT & Sensor Integration:\n\nCurrent Capabilities:\n• Manual input of soil and climate data\n• Image-based disease detection\n• Offline AI processing\n\nFuture Integration Potential:\n• Soil moisture sensors → Auto irrigation recommendations\n• Weather stations → Dynamic crop planning\n• pH sensors → Real-time soil monitoring\n• Camera traps → Continuous disease monitoring\n• IoT gateways → Multi-field management\n\nBenefits of Integration:\n• Automated data collection\n• Real-time monitoring and alerts\n• Data-driven decision making\n• Reduced manual labor\n• Precision agriculture\n\nThe system is designed to be extensible - sensor data can be fed into the same AI models for automated recommendations!"
        
        return "SmartCropSprayer AI Technology:\n\nOur system uses advanced AI/ML:\n\n1. Crop Prediction:\n• Algorithm: Random Forest (92-95% accuracy)\n• Data: 2200+ farm samples\n• Analyzes: Soil nutrients + climate\n\n2. Disease Detection:\n• Technology: Deep Learning CNN (ResNet18)\n• Model: PyTorch (.pth format)\n• Detects: 3 disease types from images (Apple Black Rot, Apple Scab, Powdery Mildew)\n\n3. Pesticide Recommendation:\n• Rule-based expert system\n• Integrated with disease detection\n• Safety and dosage information\n\n4. Chatbot:\n• Offline: Enhanced rule-based + knowledge integration\n• Online: GPT-powered (if API configured)\n• Context-aware farming guidance\n\nAll models work offline for accessibility in remote areas!\n\nAsk about specific technologies for more details."
    
    def _answer_climate_question(self, text):
        """Answer climate and season questions."""
        if 'tropical' in text:
            return "Crops for Tropical Climate:\n\nCharacteristics: High temperature (25-35°C), high humidity, abundant rainfall\n\nIdeal Crops:\n• Rice: Thrives in warm, humid conditions\n• Banana: High temperature and water requirement\n• Mango: Tropical fruit tree\n• Coconut: Coastal tropical regions\n• Papaya: Fast-growing tropical fruit\n• Coffee: Tropical highlands\n• Cocoa: Shaded tropical regions\n\nTips:\n• Disease pressure is higher (warm + humid)\n• Good drainage essential (high rainfall)\n• Pest management critical\n• Consider windbreaks for storms\n\nUse our Crop Recommendation tool with your specific climate data (temp, humidity, rainfall) for precise suggestions!"
        
        if 'temperate' in text or 'cold' in text:
            return "Crops for Temperate Climate:\n\nCharacteristics: Moderate temperature, distinct seasons, moderate rainfall\n\nIdeal Crops:\n• Wheat: Cool season cereal\n• Apple: Requires winter chill hours\n• Grapes: Temperate fruit crop\n• Potato: Cool season crop\n• Barley: Cold-tolerant cereal\n• Cherry: Needs winter dormancy\n\nSeason Considerations:\n• Spring: Planting season for most crops\n• Summer: Active growth period\n• Fall: Harvest season\n• Winter: Dormancy (orchards) or fallow\n\nTip: Use crop rotation in temperate zones for soil health and pest management."
        
        if any(word in text for word in ['season', 'kharif', 'rabi', 'winter', 'summer', 'monsoon']):
            return "Seasonal Crop Planning:\n\nKharif (Monsoon/Summer) Season:\n• Sowing: June-July\n• Harvesting: September-October\n• Crops: Rice, maize, cotton, jute, millet\n• Rainfall-dependent crops\n\nRabi (Winter) Season:\n• Sowing: October-November\n• Harvesting: March-April\n• Crops: Wheat, barley, chickpea, mustard, peas\n• Irrigation usually required\n\nZaid (Summer) Season:\n• Sowing: March-April\n• Harvesting: June-July\n• Crops: Watermelon, muskmelon, cucumber\n• Short duration crops\n\nPerennial Crops:\n• Apple, mango, banana: Year-round management\n• Harvest seasons vary by crop\n\nOur Crop Recommendation tool considers temperature and rainfall patterns for season-appropriate suggestions!"
        
        return "Climate-Based Farming:\n\nOur AI considers climate factors for crop recommendations:\n\nKey Parameters:\n• Temperature: Optimal range varies by crop (15-35°C)\n• Humidity: Affects disease pressure (40-90%)\n• Rainfall: Critical for water planning (40-300 cm/year)\n\nCrop-Climate Matching:\n• Hot + Humid: Rice, banana, jute\n• Hot + Dry: Cotton, millet, sorghum\n• Cool + Wet: Apple, wheat, potato\n• Moderate: Maize, soybean, most vegetables\n\nClimate Change Adaptation:\n• Select heat/drought-tolerant varieties\n• Adjust planting dates\n• Improve water management\n• Diversify crops\n\nUse our Crop Recommendation tool - input your local climate data for AI-powered crop suggestions!"
    
    def _answer_general_farming_question(self, text):
        """Answer general farming questions with enhanced knowledge."""
        if self._check_keywords(text, ['soil', 'fertility']):
            return "Soil Management:\n\n• Test soil annually for N, P, K, and pH\n• Most crops prefer pH 6.0-7.0\n• NPK ratios vary by crop:\n  - Cereals: High N (100-150 kg/ha)\n  - Fruits: Balanced with high K (100-200 kg/ha)\n  - Legumes: Low N (they fix it)\n\nUse our Crop Recommendation tool for specific advice based on your soil test!"
        
        if self._check_keywords(text, ['organic', 'sustainable', 'eco-friendly']):
            return "Sustainable Farming Practices:\n\n1. Organic Fertilizers:\n• Compost: 10-20 tons/ha\n• Farmyard manure: 15-25 tons/ha\n• Green manure: Legume cover crops\n• Vermicompost: 5-8 tons/ha\n\n2. Pest Control:\n• Biological controls (predators, parasites)\n• Organic pesticides (neem, pyrethrin)\n• Trap crops and companion planting\n\n3. Soil Health:\n• Crop rotation to prevent nutrient depletion\n• Cover crops to prevent erosion\n• Minimal tillage to preserve soil structure\n• Mulching for moisture retention\n\n4. Water Conservation:\n• Drip irrigation\n• Rainwater harvesting\n• Mulching to reduce evaporation\n\nBenefits: Healthier soil, reduced costs, better produce quality, environmental protection."
        
        if self._check_keywords(text, ['yield', 'increase', 'improve', 'productivity']):
            return "Increasing Crop Yield:\n\n1. Soil Management:\n• Test soil and apply balanced fertilizers\n• Maintain optimal pH (6.0-7.0 for most crops)\n• Add organic matter (compost, manure)\n\n2. Crop Selection:\n• Use our AI for crop-soil matching\n• Choose high-yielding varieties\n• Select disease-resistant cultivars\n\n3. Water Management:\n• Provide adequate irrigation\n• Use drip systems for efficiency\n• Water at critical growth stages\n\n4. Pest & Disease Control:\n• Monitor regularly for early detection\n• Use our Disease Detection tool\n• Apply IPM strategies\n\n5. Best Practices:\n• Optimal plant spacing\n• Timely operations (planting, weeding)\n• Proper harvesting at maturity\n• Post-harvest handling\n\nExpected Yield Increase: 20-40% with proper management!"
        
        if self._check_keywords(text, ['cost', 'reduce', 'profit', 'economics']):
            return "Reducing Farming Costs & Increasing Profit:\n\nCost Reduction:\n• Use our AI for precise fertilizer recommendations (saves 15-30%)\n• Drip irrigation reduces water and energy costs (40-60% savings)\n• IPM reduces pesticide expenses (40-50% savings)\n• Crop rotation reduces disease and fertilizer costs\n• Organic amendments reduce chemical fertilizer dependence\n\nProfit Maximization:\n• AI crop selection for optimal crop-soil matching\n• Timely disease detection prevents losses (up to 30%)\n• Improved yields through better management\n• Value addition and direct marketing\n• Diversification reduces risk\n\nTechnology Benefits:\n• SmartCropSprayer AI is free and offline\n• Reduces guesswork and mistakes\n• Prevents over-application of inputs\n• Early problem detection\n\nAverage ROI: 30-50% improvement with smart farming practices!"
        
        return "I'm your SmartCropSprayer AI assistant! I can help with:\n\n• Crop Recommendations: Based on your soil (N, P, K, pH) and environment\n• Disease Detection: Upload apple plant images for diagnosis\n• Pesticide Suggestions: Automatic recommendations for detected diseases\n• Water Management: Irrigation strategies and requirements\n• Pest Control: Organic and chemical options\n• Soil & Fertilizer Management: NPK ratios and application\n• Climate & Season Planning: Best crops for your region\n\nTry asking:\n• 'Which crop for low nitrogen?'\n• 'How to detect powdery mildew?'\n• 'Organic pesticides for apple diseases?'\n• 'Water requirement for maize?'\n• 'Get farming advice'\n• 'Learn best practices'\n• 'Ask about treatments'\n\nOr use our interactive tools:\n• /crop-prediction for AI recommendations\n• /disease-detection for image analysis\n• /history to track your farming data"

