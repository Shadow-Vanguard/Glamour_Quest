import pandas as pd
from django.db.models import Avg
from .models import Booking, Service, Feedback  # Adjust the import based on your project structure
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

def prepare_data():
    bookings = Booking.objects.select_related('client', 'service').all()
    data = {
        'client_id': [],
        'service_id': [],
        'rating': []
    }
    
    for booking in bookings:
        data['client_id'].append(booking.client.id)
        data['service_id'].append(booking.service.id)
        data['rating'].append(1)  # You can modify this to reflect actual ratings if available

    df = pd.DataFrame(data)
    return df

def get_recommendations(client_id):
    # Get all feedback ratings
    feedbacks = Feedback.objects.all()
    
    # Create a dictionary to hold service ratings
    service_ratings = {}
    
    for feedback in feedbacks:
        service_id = feedback.booking.service.id
        rating = feedback.rating
        
        if service_id not in service_ratings:
            service_ratings[service_id] = []
        service_ratings[service_id].append(rating)
    
    # Calculate average ratings
    average_ratings = {service_id: sum(ratings) / len(ratings) for service_id, ratings in service_ratings.items()}
    
    # Sort services by average rating
    recommended_services = sorted(average_ratings.items(), key=lambda x: x[1], reverse=True)
    
    # Get the top 5 recommended services
    top_recommendations = [Service.objects.get(id=service_id) for service_id, _ in recommended_services[:5]]
    
    return top_recommendations

def train_recommendation_model():
    # Load feedback data
    feedbacks = Feedback.objects.all()
    data = [(feedback.booking.client.id, feedback.booking.service.id, feedback.rating) for feedback in feedbacks]

    # Create a DataFrame
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data, reader)

    # Split the dataset into training and testing sets
    trainset, testset = train_test_split(dataset, test_size=0.2)

    # Train the SVD model
    model = SVD()
    model.fit(trainset)

    # Test the model
    predictions = model.test(testset)
    rmse = accuracy.rmse(predictions)

    return model, rmse

def get_ml_recommendations(model, client_id, n_recommendations=5):
    # Get all service IDs
    service_ids = [service.id for service in Service.objects.all()]

    # Predict ratings for all services for the given client
    predictions = [model.predict(client_id, service_id) for service_id in service_ids]

    # Sort predictions by estimated rating
    top_recommendations = sorted(predictions, key=lambda x: x.est, reverse=True)[:n_recommendations]

    # Return recommended services
    recommended_services = [Service.objects.get(id=pred.iid) for pred in top_recommendations]
    return recommended_services
