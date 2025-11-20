import os
from openai import OpenAI

class FarmingAssistant:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5"
        self.conversation_history = []
        
        self.system_prompt = """You are an expert agricultural advisor with deep knowledge of farming practices, crop management, soil science, pest control, and sustainable agriculture.

Your role is to provide:
- Clear, practical farming advice in simple, non-technical language
- Specific recommendations based on soil conditions, climate, and crop types
- Evidence-based guidance on pest control, disease management, and fertilization
- Sustainable and organic farming practices when appropriate
- Regional considerations for crop selection and management

Guidelines:
- Keep responses concise (2-4 sentences) unless detailed explanations are specifically requested
- Use everyday language that farmers can understand
- Provide actionable advice rather than general information
- Consider cost-effectiveness and accessibility of solutions
- Prioritize safe, sustainable practices

Focus areas: crop recommendation, disease diagnosis, soil management, irrigation, pest control, fertilization, organic farming, and seasonal planning."""
    
    def chat(self, user_message):
        try:
            self.conversation_history.append({"role": "user", "content": user_message})
            
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history[-20:]
            
            # gpt-5 doesn't support temperature parameter, do not use it.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            error_msg = f"I apologize, but I'm having trouble connecting right now. Error: {str(e)}"
            return error_msg
    
    def get_farming_tips(self, topic):
        topic_prompts = {
            'soil_health': 'Provide 3 practical tips for improving soil health and fertility on a small to medium farm.',
            'water_management': 'Give 3 water conservation tips for efficient irrigation and moisture management in farming.',
            'pest_control': 'Share 3 effective integrated pest management strategies that combine organic and chemical methods.',
            'fertilizer': 'Provide 3 tips for proper fertilizer application and nutrient management to maximize crop yield.'
        }
        
        prompt = topic_prompts.get(topic, f'Provide 3 practical farming tips about {topic}.')
        return self.chat(prompt)
    
    def get_crop_guidance(self, crop_recommendation):
        crop_name = crop_recommendation.get('crop', 'unknown')
        crop_info = crop_recommendation.get('info', '')
        
        prompt = f"I'm considering growing {crop_name}. {crop_info[:200]} What are 2-3 key success factors I should focus on?"
        return self.chat(prompt)
    
    def get_disease_guidance(self, disease_result):
        disease = disease_result.get('disease', 'unknown')
        pesticide = disease_result.get('pesticide', 'unknown')
        
        prompt = f"My apple tree has {disease}. The recommended treatment is {pesticide}. What additional management practices should I implement to prevent recurrence?"
        return self.chat(prompt)
    
    def reset_conversation(self):
        self.conversation_history = []
