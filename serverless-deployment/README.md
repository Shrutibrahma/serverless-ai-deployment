# Serverless AI Deployment - EduPredict

AWS Lambda-based ML prediction API with S3-hosted dashboard.

## Architecture

```
User Browser
     ↓
S3 Static Website (Frontend)
     ↓ (AJAX POST)
API Gateway (HTTPS)
     ↓
AWS Lambda (Python Prediction)
     ↓
JSON Response
```

## Quick Deploy Guide

### Step 1: Deploy Lambda Function

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda)
2. Click "Create function"
3. Name: `edupredict-lambda`
4. Runtime: Python 3.9 or 3.11
5. Click "Create function"

6. In the Code tab, paste contents of `backend/app.py`
7. Click "Deploy"

8. Configure Test Event:
   - Click "Test" tab
   - Create new test event
   - Event name: `test-predict`
   - JSON:
   ```json
   {
     "body": "{\"tuition\": 25000, \"duration\": 12, \"location\": 7, \"demand\": 8}"
   }
   ```
   - Click "Test" — should return prediction

### Step 2: Create API Gateway

1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway)
2. Click "Create API" → "HTTP API"
3. Integrations:
   - Choose "Lambda function"
   - Select your `edupredict-lambda` function
4. Methods: Select `POST`
5. Resource path: `/predict`
6. Click "Next" → "Create"
7. Copy the **Invoke URL**
8. Update `frontend/index.html` line 280:
   ```javascript
   const API_URL = 'https://YOUR_URL_HERE/predict';
   ```

### Step 3: Host on S3

1. Go to [S3 Console](https://s3.console.aws.amazon.com)
2. Create bucket:
   - Name: `edupredict-[your-name]` (must be unique)
   - Region: us-east-1
   - Uncheck "Block all public access"
   - Acknowledge warning
3. Upload `index.html` to bucket
4. Enable Static Website Hosting:
   - Properties tab → Static website hosting
   - Enable
   - Index document: `index.html`
5. Set Bucket Policy (Permissions → Bucket Policy):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Sid": "PublicReadGetObject",
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::edupredict-[your-name]/*"
     }]
   }
   ```
6. Visit the S3 website URL (shown in Static website hosting section)

### Step 4: Test End-to-End

1. Open S3 dashboard URL in browser
2. Enter values and click "Get Prediction"
3. Should show prediction result

## Files

| File | Purpose |
|------|---------|
| `backend/app.py` | Lambda handler with ML prediction |
| `frontend/index.html` | S3-hosted dashboard |

## API Format

**Request (POST /predict):**
```json
{
  "tuition": 25000,
  "duration": 12,
  "location": 7,
  "demand": 8
}
```

**Response:**
```json
{
  "prediction": 66.4,
  "enrollment_rate": "66.4%",
  "interpretation": "Moderate enrollment expected",
  "confidence": "Medium",
  "model_version": "1.0.0",
  "inputs": {...}
}
```

## Why Pure Python?

This model uses pure Python (no numpy/scikit-learn) because:
- AWS Lambda has 250MB size limit
- Packaging ML libraries often exceeds limit
- Pure Python deploys instantly, no dependency issues
- Cost: $0 on AWS Free Tier (1M requests/month)

## Cost Comparison

| Architecture | Monthly Cost (low traffic) |
|--------------|---------------------------|
| EC2 (t2.micro 24/7) | $8-15/month |
| AWS Lambda (serverless) | $0 (Free Tier) |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Lambda timeout | Increase timeout to 10s in function config |
| CORS errors | Check API Gateway CORS settings, enable for `*` |
| S3 403 error | Check bucket policy and public access settings |
| API not found | Verify API Gateway stage is deployed |

## Submission Checklist

- [ ] Lambda function deployed
- [ ] API Gateway `/predict` endpoint working
- [ ] S3 static website hosting enabled
- [ ] Frontend updated with correct API URL
- [ ] Prediction works in browser
- [ ] Screenshots captured (Lambda, API Gateway, S3, working prediction)

## Links

- [AWS Lambda Docs](https://docs.aws.amazon.com/lambda/latest/dg/)
- [API Gateway HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [S3 Static Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
