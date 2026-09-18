from google import genai

client = genai.Client()


def get_ai_explanation(avg_cpu, avg_memory, status, recommendation):

    prompt = f"""
You are CloudSage, a cloud resource optimization advisor.

Current monitoring information:

Average CPU Usage: {avg_cpu}%
Average Memory Usage: {avg_memory}%
Resource Status: {status}
Recommendation: {recommendation}

Explain this recommendation in simple language for a normal user.

Give only 2 to 3 short sentences.

Explain:
- why this status was detected
- why the recommendation is appropriate
- possible performance or cost impact

Do not use complicated technical terms.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("Gemini Error:", e)

        if "429" in str(e):
            return "AI request limit reached. Please wait a while and try again."

        return "AI explanation is currently unavailable."