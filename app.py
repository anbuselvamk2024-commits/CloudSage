from flask import Flask, render_template, jsonify
import psutil
import time
from collections import deque

from genai_advisor import get_ai_explanation
from database import init_db, save_history, get_history
from aws_pricing import get_ec2_price

app = Flask(__name__)

# Cache AWS prices once at application startup
nano_price_cache = get_ec2_price("t3.nano")
micro_price_cache = get_ec2_price("t3.micro")
small_price_cache = get_ec2_price("t3.small")

# Initialize database
init_db()

# Store last 5 readings
cpu_history = deque(maxlen=5)
memory_history = deque(maxlen=5)

# Store latest analysis for Gemini
latest_analysis = {
    "avg_cpu": 0,
    "avg_memory": 0,
    "status": "UNKNOWN",
    "recommendation": "No recommendation yet."
}

# Save history every 20 seconds
last_saved_time = 0
SAVE_INTERVAL = 20


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/metrics')
def metrics():

    global last_saved_time

    # -----------------------------
    # LIVE RESOURCE MONITORING
    # -----------------------------

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    cpu_history.append(cpu)
    memory_history.append(memory)

    avg_cpu = sum(cpu_history) / len(cpu_history)
    avg_memory = sum(memory_history) / len(memory_history)

    # -----------------------------
    # NETWORK MONITORING
    # -----------------------------

    net1 = psutil.net_io_counters()

    time.sleep(1)

    net2 = psutil.net_io_counters()

    upload_speed = (
        net2.bytes_sent - net1.bytes_sent
    ) / 1024

    download_speed = (
        net2.bytes_recv - net1.bytes_recv
    ) / 1024

    # -----------------------------
    # RESOURCE STATUS
    # -----------------------------

    if avg_cpu < 30 and avg_memory < 40:
        status = "UNDERUTILIZED"

    elif avg_cpu > 80 or avg_memory > 85:
        status = "OVERUTILIZED"

    else:
        status = "OPTIMAL"

    # -----------------------------
    # REAL AWS PRICES
    # -----------------------------

    nano_price = nano_price_cache
    micro_price = micro_price_cache
    small_price = small_price_cache

    current_instance = "t3.micro"

    if micro_price:
        current_hourly_cost = micro_price["hourly_usd"]
        current_monthly_cost = micro_price["monthly_usd"]
    else:
        current_hourly_cost = 0
        current_monthly_cost = 0

    # -----------------------------
    # RECOMMENDATION ENGINE
    # -----------------------------

    if status == "UNDERUTILIZED":

        suggested_instance = "t3.nano"

        recommendation = (
            "Resource usage is low. "
            "Consider downsizing from t3.micro to t3.nano "
            "to reduce cloud cost."
        )

        if nano_price:
            optimized_monthly_cost = nano_price["monthly_usd"]
        else:
            optimized_monthly_cost = current_monthly_cost

    elif status == "OVERUTILIZED":

        suggested_instance = "t3.small"

        recommendation = (
            "Resource usage is high. "
            "Consider upgrading from t3.micro to t3.small "
            "to improve performance."
        )

        if small_price:
            optimized_monthly_cost = small_price["monthly_usd"]
        else:
            optimized_monthly_cost = current_monthly_cost

    else:

        suggested_instance = "t3.micro"

        recommendation = (
            "Current resource allocation is suitable. "
            "No instance change is required."
        )

        optimized_monthly_cost = current_monthly_cost

    # -----------------------------
    # COST ANALYSIS
    # -----------------------------

    saving = (
        current_monthly_cost
        - optimized_monthly_cost
    )

    if current_monthly_cost > 0:

        saving_percent = (
            saving / current_monthly_cost
        ) * 100

    else:

        saving_percent = 0

    additional_cost = 0

    if saving < 0:
        additional_cost = abs(saving)
        saving = 0
        saving_percent = 0

    # -----------------------------
    # SAVE LATEST DATA FOR GEMINI
    # -----------------------------

    latest_analysis["avg_cpu"] = round(avg_cpu, 2)
    latest_analysis["avg_memory"] = round(avg_memory, 2)
    latest_analysis["status"] = status
    latest_analysis["recommendation"] = recommendation

    # -----------------------------
    # SAVE TO SQLITE EVERY 20 SEC
    # -----------------------------

    current_time = time.time()

    if current_time - last_saved_time >= SAVE_INTERVAL:

        save_history(
            round(avg_cpu, 2),
            round(avg_memory, 2),
            disk,
            status,
            recommendation,
            current_monthly_cost,
            optimized_monthly_cost,
            saving
        )

        last_saved_time = current_time

    # -----------------------------
    # RETURN DATA TO DASHBOARD
    # -----------------------------

    return jsonify({

        # AWS RESOURCE INFORMATION
        "cloud_provider": "AWS",
        "service": "EC2",
        "instance_type": current_instance,
        "suggested_instance": suggested_instance,
        "region": "Asia Pacific (Mumbai)",
        "public_ip": "65.0.221.105",
        "vcpu": 2,

        # LIVE METRICS
        "cpu": cpu,
        "memory": memory,
        "disk": disk,

        "upload": round(
            upload_speed,
            2
        ),

        "download": round(
            download_speed,
            2
        ),

        # AVERAGES
        "avg_cpu": round(
            avg_cpu,
            2
        ),

        "avg_memory": round(
            avg_memory,
            2
        ),

        # ANALYSIS
        "status": status,
        "recommendation": recommendation,

        # REAL AWS COST
        "hourly_cost": round(
            current_hourly_cost,
            4
        ),

        "current_cost": round(
            current_monthly_cost,
            2
        ),

        "optimized_cost": round(
            optimized_monthly_cost,
            2
        ),

        "saving": round(
            saving,
            2
        ),

        "saving_percent": round(
            saving_percent,
            2
        ),

        "additional_cost": round(
            additional_cost,
            2
        )
    })


# -----------------------------
# GEMINI AI EXPLANATION
# -----------------------------

@app.route('/api/explain')
def explain():

    explanation = get_ai_explanation(
        latest_analysis["avg_cpu"],
        latest_analysis["avg_memory"],
        latest_analysis["status"],
        latest_analysis["recommendation"]
    )

    return jsonify({
        "ai_explanation": explanation
    })


# -----------------------------
# OPTIMIZATION HISTORY
# -----------------------------

@app.route('/api/history')
def history():

    rows = get_history()

    history_data = []

    for row in rows:

        history_data.append({

            "id": row[0],
            "cpu": row[1],
            "memory": row[2],
            "disk": row[3],
            "status": row[4],
            "recommendation": row[5],
            "current_cost": row[6],
            "optimized_cost": row[7],
            "saving": row[8],
            "timestamp": row[9]

        })

    return jsonify(history_data)


# -----------------------------
# START FLASK APP
# -----------------------------

if __name__ == '__main__':

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )