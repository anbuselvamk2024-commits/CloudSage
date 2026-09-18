# CloudSage

CloudSage is an explainable cloud resource optimization and cost management advisor.

It monitors cloud resource usage, identifies underutilized or overutilized resources, recommends a better EC2 instance size, estimates the cost impact, and provides an AI-generated explanation for the recommendation.

## Features

- Real-time CPU monitoring
- Real-time memory monitoring
- Disk usage monitoring
- Network upload and download monitoring
- Underutilization detection
- Overutilization detection
- Optimal utilization detection
- EC2 instance recommendation
- Real AWS Pricing API integration
- Monthly cloud cost estimation
- Estimated savings calculation
- Additional cost calculation for upgrades
- Google Gemini AI explanation
- Optimization history using SQLite
- Interactive dashboard
- Light mode and dark mode
- AWS EC2 deployment
- Gunicorn production server
- systemd automatic startup
- Nginx reverse proxy
- Elastic IP for stable public access

## Recommendation Logic

### UNDERUTILIZED

Average CPU < 30%  
AND  
Average Memory < 40%

Recommendation:

t3.micro -> t3.nano

### OVERUTILIZED

Average CPU > 80%  
OR  
Average Memory > 85%

Recommendation:

t3.micro -> t3.small

### OPTIMAL

Otherwise:

t3.micro -> t3.micro

## AWS Pricing

CloudSage uses the AWS Pricing API to retrieve EC2 On-Demand Linux pricing for the Mumbai region.

| Instance Type | Hourly Cost | Monthly Cost |
|---|---:|---:|
| t3.nano | $0.0056 | $4.03 |
| t3.micro | $0.0112 | $8.06 |
| t3.small | $0.0224 | $16.13 |

Monthly cost is estimated using:

Hourly Price x 24 x 30

These values represent EC2 compute cost only.

## Technology Stack

### Backend
- Python
- Flask
- psutil
- boto3
- SQLite

### AI
- Google Gemini API

### Frontend
- HTML
- CSS
- JavaScript
- Chart.js

### Cloud Deployment
- AWS EC2
- AWS IAM
- AWS Pricing API
- Gunicorn
- systemd
- Nginx
- Elastic IP

## Project Structure

CloudSage/
- app.py
- aws_pricing.py
- database.py
- genai_advisor.py
- monitor.py
- requirements.txt
- README.md
- .gitignore
- templates/
  - index.html
- static/
  - style.css

## Main Files

### app.py
Main Flask backend containing monitoring, recommendation logic, cost calculation, API routes, history, and dashboard data.

### aws_pricing.py
Retrieves EC2 pricing using the AWS Pricing API.

### database.py
Handles SQLite database operations and optimization history.

### genai_advisor.py
Connects CloudSage with Google Gemini and generates explanations.

### monitor.py
Contains system resource monitoring functionality.

### templates/index.html
Contains the CloudSage dashboard interface.

### static/style.css
Contains dashboard styling, themes, animations, and responsive design.

## Running Locally

Create virtual environment:

```bash
python -m venv venv
