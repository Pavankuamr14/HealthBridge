# Hospital Management System

A FastAPI-based Hospital Management System with PostgreSQL database integration.

## Features

- Full CRUD operations for patient records
- PostgreSQL database integration
- Pydantic models for request/response validation
- OpenAPI documentation with Swagger UI
- Environment variable configuration
- SQLAlchemy ORM

## Prerequisites

- Python 3.8+
- PostgreSQL database (AWS RDS)
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd hospital-management-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
DATABASE_URL=postgresql://admin:your-password@your-db-endpoint.amazonaws.com:5432/hospital
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /patients/`: Create a new patient
- `GET /patients/`: Get all patients
- `GET /patients/{id}`: Get a specific patient
- `PUT /patients/{id}`: Update a patient
- `DELETE /patients/{id}`: Delete a patient

## Security Considerations

1. Never commit the `.env` file to version control
2. Use strong passwords for database access
3. Implement proper authentication and authorization
4. Use HTTPS in production
5. Regularly update dependencies

## Deployment to AWS EC2

1. Create an EC2 instance
2. Install Docker on the EC2 instance
3. Create a Dockerfile:
```dockerfile
FROM python:3.8
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

4. Build and run the Docker container:
```bash
docker build -t hospital-management .
docker run -d -p 8000:8000 hospital-management
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `ALGORITHM`: Algorithm for JWT tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 