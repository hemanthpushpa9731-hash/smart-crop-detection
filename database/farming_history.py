import sqlite3
import os
import pandas as pd
from datetime import datetime
import json

class FarmingHistoryManager:
    def __init__(self, db_path='database/farming_history.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                nitrogen REAL,
                phosphorus REAL,
                potassium REAL,
                temperature REAL,
                humidity REAL,
                ph REAL,
                rainfall REAL,
                recommended_crop TEXT,
                confidence REAL,
                crop_info TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_name TEXT,
                detected_disease TEXT,
                confidence REAL,
                pesticide TEXT,
                is_healthy BOOLEAN,
                all_predictions TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatbot_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT,
                bot_response TEXT,
                chatbot_type TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_crop_recommendation(self, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, 
                                recommended_crop, confidence, crop_info):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crop_recommendations 
            (nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, recommended_crop, confidence, crop_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, 
              recommended_crop, confidence, crop_info))
        
        conn.commit()
        conn.close()
    
    def log_disease_detection(self, image_name, detected_disease, confidence, pesticide, is_healthy, all_predictions):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        all_predictions_json = json.dumps(all_predictions)
        
        cursor.execute('''
            INSERT INTO disease_detections 
            (image_name, detected_disease, confidence, pesticide, is_healthy, all_predictions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (image_name, detected_disease, confidence, pesticide, is_healthy, all_predictions_json))
        
        conn.commit()
        conn.close()
    
    def log_chatbot_query(self, user_query, bot_response, chatbot_type='offline'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chatbot_queries 
            (user_query, bot_response, chatbot_type)
            VALUES (?, ?, ?)
        ''', (user_query, bot_response, chatbot_type))
        
        conn.commit()
        conn.close()
    
    def get_crop_recommendations(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        query = f'''
            SELECT timestamp, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, 
                   recommended_crop, confidence, crop_info
            FROM crop_recommendations
            ORDER BY timestamp DESC
            LIMIT {limit}
        '''
        df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
        conn.close()
        return df
    
    def get_disease_detections(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        query = f'''
            SELECT timestamp, image_name, detected_disease, confidence, pesticide, is_healthy
            FROM disease_detections
            ORDER BY timestamp DESC
            LIMIT {limit}
        '''
        df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
        conn.close()
        return df
    
    def get_chatbot_queries(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        query = f'''
            SELECT timestamp, user_query, bot_response, chatbot_type
            FROM chatbot_queries
            ORDER BY timestamp DESC
            LIMIT {limit}
        '''
        df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
        conn.close()
        return df
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM crop_recommendations')
        total_crops = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM disease_detections')
        total_diseases = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chatbot_queries')
        total_queries = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT recommended_crop, COUNT(*) as count 
            FROM crop_recommendations 
            GROUP BY recommended_crop 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        top_crop_result = cursor.fetchone()
        top_crop = top_crop_result[0] if top_crop_result else 'N/A'
        
        cursor.execute('''
            SELECT detected_disease, COUNT(*) as count 
            FROM disease_detections 
            WHERE detected_disease != 'Healthy'
            GROUP BY detected_disease 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        top_disease_result = cursor.fetchone()
        top_disease = top_disease_result[0] if top_disease_result else 'N/A'
        
        conn.close()
        
        return {
            'total_crop_recommendations': total_crops,
            'total_disease_detections': total_diseases,
            'total_chatbot_queries': total_queries,
            'most_recommended_crop': top_crop,
            'most_common_disease': top_disease
        }
    
    def clear_all_history(self):
        """Clear all history from all tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM crop_recommendations')
            cursor.execute('DELETE FROM disease_detections')
            cursor.execute('DELETE FROM chatbot_queries')
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error clearing history: {e}")
            return False
        finally:
            conn.close()
    
    def export_to_csv(self, table_name, filename):
        conn = sqlite3.connect(self.db_path)
        
        if table_name == 'crop_recommendations':
            query = 'SELECT * FROM crop_recommendations ORDER BY timestamp DESC'
        elif table_name == 'disease_detections':
            query = 'SELECT * FROM disease_detections ORDER BY timestamp DESC'
        elif table_name == 'chatbot_queries':
            query = 'SELECT * FROM chatbot_queries ORDER BY timestamp DESC'
        else:
            conn.close()
            raise ValueError(f"Unknown table name: {table_name}")
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        export_dir = 'database/exports'
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)
        
        df.to_csv(filepath, index=False)
        return filepath
