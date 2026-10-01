FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libgl1/libglib2.0-0: opencv runtime deps. libgomp1: mediapipe/tensorflow.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY manage.py .
COPY music_recommendation ./music_recommendation
COPY music ./music
COPY db ./db
COPY media ./media

RUN mkdir -p staticfiles \
    && useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

RUN python manage.py collectstatic --noinput --settings=music_recommendation.settings || true

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "music_recommendation.wsgi:application"]
