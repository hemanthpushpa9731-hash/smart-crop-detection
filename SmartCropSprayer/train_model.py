import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

os.makedirs('models', exist_ok=True)

print("Loading crop recommendation dataset...")
df = pd.read_csv('data/crop_recommendation.csv')

print(f"Dataset shape: {df.shape}")
print(f"Crop classes: {sorted(df['label'].unique())}")

# Extract features exactly as in Tkinter version
features = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
target = df['label']

# Split exactly as in Tkinter version
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=2)

print("\nTraining RandomForest model...")
# Use exact same parameters as Tkinter version
RF = RandomForestClassifier(n_estimators=20, random_state=0)
RF.fit(X_train, y_train)

y_pred = RF.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel trained successfully!")
print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")
print(f"RF's Accuracy is: {accuracy * 100:.2f}%")

# Save model
model_path = 'models/RandomForest.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(RF, f)

print(f"\nModel saved to {model_path}")
print("Model training complete!")
