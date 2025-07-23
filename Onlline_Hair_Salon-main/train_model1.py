# train_model.py
import os
import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# Set parameters
img_width, img_height = 150, 150
batch_size = 16
epochs = 10

# Load images
# Updated load_data function
def load_data(data_dir):
    images = []
    labels = []
    label_map = {}  # To map labels to indices
    label_index = 0

    for img_file in os.listdir(data_dir):
        img_path = os.path.join(data_dir, img_file)
        if os.path.isfile(img_path):  # Check if it's a file
            img = cv2.imread(img_path)
            img = cv2.resize(img, (img_width, img_height))
            images.append(img)
            # Assign a label based on the filename or some other logic
            label = img_file.split('_')[0]  # Example: use part of the filename as label
            if label not in label_map:
                label_map[label] = label_index
                label_index += 1
            labels.append(label_map[label])  # Use the mapped label

    return np.array(images), np.array(labels)

# Load dataset
data_dir = 'hairstyles'
X, y = load_data(data_dir)

# Normalize images
X = X.astype('float32') / 255.0

# Create a simple CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(img_width, img_height, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(len(set(y)), activation='softmax')  # Number of classes
])

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
model.fit(X, y, batch_size=batch_size, epochs=epochs)

# Save the model
model.save('hairstyle_model.keras')