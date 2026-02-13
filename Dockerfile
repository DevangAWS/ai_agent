FROM python:3.11-slim

# Prevent Python from writing .pyc files or buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (cron for auto-updates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install the dependencies required for the Intelligence Layer
# Added 'requests' for the universal API calls
RUN pip install --no-cache-dir \
    google-genai \
    groq \
    rich \
    requests

# Copy the application code
COPY ai_agent.py .

# Setup silent auto-updates for libraries every 5 minutes
RUN echo "*/5 * * * * root pip install --upgrade google-genai groq rich requests > /dev/null 2>&1" >> /etc/cron.d/ai-updates
RUN chmod 0644 /etc/cron.d/ai-updates
RUN crontab /etc/cron.d/ai-updates

# Create the global 'ai' command securely
RUN printf '#!/bin/bash\npython /app/ai_agent.py "$@"' > /usr/local/bin/ai \
    && chmod +x /usr/local/bin/ai

# Start Cron (background) and Bash (foreground)
CMD cron && /bin/bash
