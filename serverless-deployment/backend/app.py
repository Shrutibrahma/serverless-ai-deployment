"""
AWS Lambda handler for EduPredict enrollment prediction API.
Uses pure Python implementation - no external dependencies for Lambda compatibility.
"""
import json
import math

# Pre-calculated model coefficients (from trained scikit-learn model)
# Model: Enrollment = bias + w1*tuition + w2*duration + w3*location + w4*demand
MODEL_BIAS = 45.0
COEFFICIENTS = {
    'tuition': -0.008,      # Annual Tuition ($) - negative: higher cost = lower enrollment
    'duration': 2.5,        # Program Duration (months) - positive: longer programs = more students
    'location': 3.2,        # Location Score (1-10) - positive: better location = more enrollment
    'demand': 4.5           # Market Demand Score (1-10) - positive: high demand = more enrollment
}

def predict_enrollment(tuition, duration, location_score, demand_score):
    """
    Predict enrollment using linear regression model.
    All parameters are numeric.
    """
    # Convert string inputs to float if needed
    tuition = float(tuition)
    duration = float(duration)
    location_score = float(location_score)
    demand_score = float(demand_score)

    # Calculate prediction
    prediction = MODEL_BIAS + \
                 (COEFFICIENTS['tuition'] * tuition) + \
                 (COEFFICIENTS['duration'] * duration) + \
                 (COEFFICIENTS['location'] * location_score) + \
                 (COEFFICIENTS['demand'] * demand_score)

    # Ensure reasonable bounds (0-100%)
    prediction = max(0, min(100, prediction))

    return round(prediction, 1)

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Handles both API Gateway and direct invocation.
    """
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }

    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'OK'})
        }

    try:
        # Parse input from API Gateway or direct invocation
        if 'body' in event and event['body']:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        # Extract parameters
        tuition = body.get('tuition', body.get('annual_tuition', 0))
        duration = body.get('duration', body.get('program_duration', 12))
        location = body.get('location', body.get('location_score', 5))
        demand = body.get('demand', body.get('market_demand', 5))

        # Validate inputs
        if not all([tuition, duration, location, demand]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing required parameters',
                    'required': ['tuition', 'duration', 'location', 'demand']
                })
            }

        # Make prediction
        prediction = predict_enrollment(tuition, duration, location, demand)

        # Build response with interpretation
        if prediction >= 70:
            interpretation = "High enrollment expected"
            confidence = "Strong"
        elif prediction >= 40:
            interpretation = "Moderate enrollment expected"
            confidence = "Medium"
        else:
            interpretation = "Low enrollment expected"
            confidence = "Low"

        response = {
            'prediction': prediction,
            'enrollment_rate': f"{prediction}%",
            'interpretation': interpretation,
            'confidence': confidence,
            'model_version': '1.0.0',
            'inputs': {
                'annual_tuition': float(tuition),
                'program_duration_months': float(duration),
                'location_score': float(location),
                'market_demand_score': float(demand)
            }
        }

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'message': 'Prediction failed'
            })
        }


# For local testing
if __name__ == '__main__':
    # Test case
    test_event = {
        'body': json.dumps({
            'tuition': 2500,
            'duration': 12,
            'location': 5,
            'demand': 10
        })
    }
    result = lambda_handler(test_event, None)
    print("Test Result:", json.dumps(result, indent=2))
