import random
import re

class OfflineFarmingChatbot:
    def __init__(self):
        self.conversation_history = []
        
        self.knowledge_base = {
            'soil': {
                'keywords': ['soil', 'ph', 'fertility', 'nutrient', 'nitrogen', 'phosphorus', 'potassium', 'npk', 'compost', 'manure', 'organic matter'],
                'responses': [
                    "Healthy soil is the foundation of successful farming. Test your soil pH regularly - most crops prefer pH 6.0-7.0. Add lime to increase pH or sulfur to decrease it.",
                    "The three essential nutrients are NPK (Nitrogen, Phosphorus, Potassium). Nitrogen promotes leafy growth, phosphorus supports root development and flowering, and potassium improves overall plant health and disease resistance.",
                    "Improve soil fertility by adding organic matter like compost, well-rotted manure, or green manure crops. This improves soil structure, water retention, and provides slow-release nutrients.",
                    "For soil testing, collect samples from multiple spots in your field at 6-inch depth. Mix them together and test for pH, NPK levels, and organic matter content. Test annually before planting season.",
                    "Clay soil retains water but drains poorly. Sandy soil drains quickly but doesn't hold nutrients. Loamy soil (mixture of sand, silt, clay) is ideal for most crops. Amend soil type with organic matter to improve texture."
                ]
            },
            'water': {
                'keywords': ['water', 'irrigation', 'rainfall', 'drought', 'flood', 'moisture', 'drip', 'spray', 'watering'],
                'responses': [
                    "Drip irrigation is highly efficient, delivering water directly to plant roots while reducing evaporation losses by up to 50%. It's ideal for water-scarce regions and reduces weed growth.",
                    "Most vegetables need 1-2 inches of water per week. Water deeply 2-3 times per week rather than shallow daily watering. This encourages deeper root growth and more drought-resistant plants.",
                    "Mulching around plants with straw, leaves, or wood chips helps retain soil moisture, reduces evaporation, suppresses weeds, and moderates soil temperature. Apply 2-3 inch layer.",
                    "Signs of overwatering: yellowing leaves, wilting despite wet soil, mold growth, root rot. Signs of underwatering: dry, crispy leaves, slow growth, wilting in afternoon sun.",
                    "Rainwater harvesting is excellent for irrigation. Collect rainwater in tanks or ponds during monsoon season. Rainwater is free of chemicals and has balanced pH, making it ideal for plants."
                ]
            },
            'pest': {
                'keywords': ['pest', 'insect', 'bug', 'aphid', 'caterpillar', 'beetle', 'worm', 'infestation', 'damage', 'control'],
                'responses': [
                    "Integrated Pest Management (IPM) combines cultural, biological, and chemical methods. Use chemical pesticides only as last resort. Start with prevention: crop rotation, resistant varieties, proper spacing.",
                    "Neem oil is an effective organic pesticide against aphids, whiteflies, and mites. Mix 2 tablespoons neem oil with 1 gallon water and spray on affected plants every 7-14 days.",
                    "Encourage beneficial insects like ladybugs, lacewings, and parasitic wasps. Plant flowers like marigolds, daisies, and alyssum to attract them. They naturally control pest populations.",
                    "For caterpillar control, use Bacillus thuringiensis (Bt), an organic bacterial insecticide. It's safe for humans and beneficial insects but deadly to caterpillars. Apply when caterpillars are young.",
                    "Physical barriers work well: row covers protect from flying insects, copper tape deters slugs, sticky traps catch flying pests. Hand-picking is effective for large pests like beetles and hornworms."
                ]
            },
            'fertilizer': {
                'keywords': ['fertilizer', 'fertiliser', 'urea', 'dap', 'feed', 'nutrition', 'supplement'],
                'responses': [
                    "Organic fertilizers (compost, manure, bone meal) release nutrients slowly and improve soil structure. Chemical fertilizers provide quick nutrients but don't improve soil health. Best approach: use both strategically.",
                    "NPK ratio on fertilizer bags indicates percentage of Nitrogen-Phosphorus-Potassium. For leafy vegetables, use high-N fertilizer (10-5-5). For fruiting crops, use balanced or high-P fertilizer (5-10-10).",
                    "Apply nitrogen fertilizers in split doses - half at planting, half during active growth. This prevents nutrient loss through leaching and matches plant uptake patterns.",
                    "Green manure crops (legumes like clover, vetch) fix atmospheric nitrogen in soil. Plant them in off-season, then till into soil before main crop. Provides free nitrogen and organic matter.",
                    "Avoid over-fertilization - it causes nutrient runoff, burns plants, and attracts pests. Follow recommended application rates. More fertilizer doesn't always mean better yield."
                ]
            },
            'crop': {
                'keywords': ['crop', 'plant', 'grow', 'cultivate', 'farming', 'agriculture', 'harvest', 'yield', 'season', 'planting'],
                'responses': [
                    "Crop rotation prevents soil depletion and breaks pest/disease cycles. Rotate crops from different families. Example: follow tomatoes (nightshade) with beans (legume), then cabbage (brassica), then corn (grass).",
                    "Companion planting improves growth and pest control. Plant tomatoes with basil (repels flies), corn with beans (nitrogen fixation), and marigolds anywhere (pest deterrent).",
                    "Planting time depends on crop and climate. Cool-season crops (lettuce, peas, spinach) grow in spring/fall. Warm-season crops (tomatoes, peppers, melons) need summer heat. Check frost dates for your region.",
                    "Proper spacing prevents disease and competition. Overcrowding reduces air circulation (promotes fungal diseases) and limits light/nutrient access. Follow seed packet spacing recommendations.",
                    "For maximum yield, provide: adequate sunlight (6-8 hours for most vegetables), consistent moisture, balanced nutrition, pest/disease management, and timely harvesting when crops reach maturity."
                ]
            },
            'disease': {
                'keywords': ['disease', 'fungus', 'mold', 'rot', 'blight', 'wilt', 'virus', 'infection', 'sick', 'unhealthy'],
                'responses': [
                    "Most plant diseases are caused by fungi and spread in wet, humid conditions. Prevent by: watering at base (not leaves), ensuring good air circulation, removing infected plant parts, and using disease-resistant varieties.",
                    "Powdery mildew appears as white powder on leaves. Treat with sulfur spray or mix 1 tablespoon baking soda + 1 teaspoon dish soap in 1 gallon water. Spray weekly until controlled.",
                    "Blight (early and late) affects tomatoes and potatoes. Remove affected leaves immediately. Apply copper-based fungicide preventively. Don't compost infected material - burn or trash it.",
                    "Root rot is caused by overwatering and poor drainage. Prevention is key: improve soil drainage, don't overwater, raise beds if needed. Once established, it's difficult to cure - may need to remove plants.",
                    "Crop sanitation prevents disease spread: remove plant debris after harvest, clean tools with bleach solution between plants, don't work in garden when plants are wet, and practice crop rotation."
                ]
            },
            'weather': {
                'keywords': ['weather', 'rain', 'temperature', 'climate', 'season', 'frost', 'heat', 'cold', 'wind'],
                'responses': [
                    "Protect plants from frost by covering with row covers, blankets, or cloches when frost is forecasted. Water soil before frost - moist soil retains heat better than dry soil.",
                    "During heat waves, provide shade cloth (30-50% shade) for cool-season crops. Mulch heavily to keep soil cool. Water early morning or evening to reduce evaporation.",
                    "Heavy rain can leach nutrients and compact soil. After heavy rains, apply light nitrogen fertilizer and gently loosen soil surface without disturbing roots.",
                    "Strong winds can damage plants and increase evaporation. Plant windbreaks (trees, shrubs, fences) on windward side. Stake tall plants before wind events.",
                    "Climate change affects planting dates and crop selection. Keep records of frost dates, rainfall patterns, and temperature extremes. Adapt by choosing heat-tolerant or drought-resistant varieties as needed."
                ]
            },
            'organic': {
                'keywords': ['organic', 'natural', 'chemical-free', 'sustainable', 'eco-friendly', 'biological'],
                'responses': [
                    "Organic farming avoids synthetic chemicals, focusing on natural fertilizers, biological pest control, and soil health. Benefits: healthier soil, safer food, better for environment, but may have lower initial yields.",
                    "Make compost from kitchen scraps, yard waste, and manure. Layer green materials (nitrogen-rich) with brown materials (carbon-rich). Keep moist and turn weekly. Ready in 2-3 months.",
                    "Natural pest control: neem oil for insects, diatomaceous earth for crawling pests, garlic spray for aphids, hand-picking for large pests, and beneficial insects for biological control.",
                    "Organic certification requires 3 years of chemical-free farming, detailed record-keeping, and annual inspections. Start transitioning by eliminating synthetic inputs gradually.",
                    "Cover crops protect and enrich soil organically. Plant clover, vetch, or rye in off-season. They prevent erosion, suppress weeds, add organic matter, and some fix nitrogen."
                ]
            },
            'apple': {
                'keywords': ['apple', 'apple tree', 'orchard'],
                'responses': [
                    "Apple trees need 800-1200 chill hours (below 7°C) for proper fruit development. They prefer well-drained loamy soil with pH 6.0-6.5 and require cross-pollination from another variety.",
                    "Common apple diseases: Apple Scab (dark lesions), Powdery Mildew (white powder), Fire Blight (blackened shoots). Prevent with proper spacing, pruning for air circulation, and fungicide sprays in spring.",
                    "Prune apple trees in late winter when dormant. Remove dead/diseased wood, crossing branches, and water sprouts. Open center allows light and air circulation, reducing disease and improving fruit quality.",
                    "Thin apple fruits in early summer to 1 fruit per cluster, spacing 6-8 inches apart. This improves fruit size, prevents branch breakage, and ensures consistent annual bearing.",
                    "Apple harvest timing: fruits should be firm, full-colored, and easily separate from tree with upward twist. Early varieties ripen July-August, mid-season August-September, late varieties September-October."
                ]
            },
            'general': {
                'keywords': [],
                'responses': [
                    "I'm an offline farming assistant with knowledge about soil management, irrigation, pest control, crop cultivation, and organic farming. What specific farming topic would you like to learn about?",
                    "For the best farming advice, please ask about specific topics like soil health, pest control, irrigation, fertilizers, crop diseases, or weather management.",
                    "I can help with practical farming questions about crop cultivation, plant nutrition, pest management, disease control, and sustainable agriculture practices."
                ]
            }
        }
        
        self.greetings = {
            'keywords': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
            'responses': [
                "Hello! I'm your offline farming assistant. How can I help you with your farming questions today?",
                "Hi there! Ask me anything about crops, soil, pests, diseases, or farming practices.",
                "Welcome! I'm here to provide farming advice on soil management, irrigation, pest control, and crop cultivation. What would you like to know?"
            ]
        }
        
        self.thanks = {
            'keywords': ['thank', 'thanks', 'appreciate', 'helpful'],
            'responses': [
                "You're welcome! Feel free to ask if you have more farming questions.",
                "Happy to help! Good luck with your farming!",
                "Glad I could assist! Don't hesitate to ask more questions about farming."
            ]
        }
    
    def generate_reply(self, user_message):
        user_message_lower = user_message.lower()
        
        if any(keyword in user_message_lower for keyword in self.greetings['keywords']):
            return random.choice(self.greetings['responses'])
        
        if any(keyword in user_message_lower for keyword in self.thanks['keywords']):
            return random.choice(self.thanks['responses'])
        
        best_category = None
        max_matches = 0
        
        for category, data in self.knowledge_base.items():
            if category == 'general':
                continue
            
            matches = sum(1 for keyword in data['keywords'] if keyword in user_message_lower)
            
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        if best_category and max_matches > 0:
            response = random.choice(self.knowledge_base[best_category]['responses'])
        else:
            response = random.choice(self.knowledge_base['general']['responses'])
        
        self.conversation_history.append({'user': user_message, 'bot': response})
        return response
    
    def get_farming_tip(self, topic):
        topic_lower = topic.lower()
        
        for category, data in self.knowledge_base.items():
            if topic_lower in category or topic_lower in data['keywords']:
                return random.choice(data['responses'])
        
        return random.choice(self.knowledge_base['general']['responses'])
    
    def reset_conversation(self):
        self.conversation_history = []
