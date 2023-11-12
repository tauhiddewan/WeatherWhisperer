FROM python:3.9.0-slim
WORKDIR /app


COPY api/requirements.txt ./api/requirements.txt 
RUN python -m pip install -r ./api/requirements.txt

COPY api/services ./api/services 
COPY api/server.py ./api/server.py 
COPY api/model/xgb_model.pkl ./api/model/xgb_model.pkl

EXPOSE 80
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "80"]
