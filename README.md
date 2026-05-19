# project-folder/

- **app/**: Main application package containing all FastAPI app components

  - **\_\_init\_\_.py**: Initializes the Python package for app

  - **main.py**: sets up routes, middleware, and monitoring

  - **models/**

    - **model.pkl**: Serialized ML model used for prediction

  - **api/**: Contains route definitions for API endpoints

    - **\_\_init\_\_.py**

    - **routes_predict.py**: Defines the /predict route for price predictions

    - **routes_auth.py**: Defines the /login route for user authentication via JWT

  - **core/**: logic for config, security, dependencies, and exception handling

    - **config.py**: Loads environment variables and app-wide settings

    - **security.py**: Handles JWT creation and verification logic

    - **dependencies.py**: Dependency injection logic for API key and JWT token validation

    - **exceptions.py**: Custom exception handlers for consistent error responses

  - **services/**

    - **model_service.py**: Loads the ML model and performs predictions (with Redis caching)

  - **middleware/**

    - **logging_middleware.py**: Logs all incoming requests and outgoing responses

  - **cache/**

    - **redis_cache.py**

  - **utils/**: Utility modules for common functionality

    - **logger.py**: Custom logger configuration (optional)

- **notebooks/**: Jupyter notebooks for experimentation

- **data/**

- **training/**

  - **\_\_init\_\_.py**:

  - **train_utils.py**: common functions to support model training

  - **train_model.py**: model training script

- **requirements.txt**: List of Python dependencies required for the app

- **Dockerfile**: Docker image definition to containerize the FastAPI app

- **docker-compose.yml**: Orchestrates FastAPI, Redis, Prometheus, and Grafana services

- **prometheus.yml**: Monitor FastAPI app using the Prometheus FastAPI Instrumentator

- **render.yaml**: Automates deployment settings of web services over Render

- **.env**: Environment variables used by the application

- **README.md**: Project overview, setup instructions, and usage guide
