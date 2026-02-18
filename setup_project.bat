@echo off
setlocal

echo Creation de la structure HR-Pulse dans le dossier courant...

:: ── Root files
type nul > .env
type nul > .env.example
type nul > .gitignore
type nul > README.md
type nul > docker-compose.yml

:: ── GitHub Actions
mkdir .github\workflows
type nul > .github\workflows\ci.yml

:: ── Terraform
mkdir terraform
type nul > terraform\main.tf
type nul > terraform\variables.tf
type nul > terraform\outputs.tf
type nul > terraform\backend.tf
type nul > terraform\providers.tf
type nul > terraform\docker.tf

:: ── Data
mkdir data
type nul > data\jobs.csv

:: ── Backend
mkdir backend\app\api\routes
mkdir backend\app\core
mkdir backend\app\models
mkdir backend\app\services
mkdir backend\app\ml
mkdir backend\tests

type nul > backend\Dockerfile
type nul > backend\pyproject.toml
type nul > backend\.python-version
type nul > backend\app\__init__.py
type nul > backend\app\main.py
type nul > backend\app\core\__init__.py
type nul > backend\app\core\config.py
type nul > backend\app\core\database.py
type nul > backend\app\core\telemetry.py
type nul > backend\app\models\__init__.py
type nul > backend\app\models\job.py
type nul > backend\app\api\__init__.py
type nul > backend\app\api\routes\__init__.py
type nul > backend\app\api\routes\jobs.py
type nul > backend\app\api\routes\predict.py
type nul > backend\app\services\__init__.py
type nul > backend\app\services\ner_service.py
type nul > backend\app\services\ingestion.py
type nul > backend\app\ml\__init__.py
type nul > backend\app\ml\predictor.py
type nul > backend\app\ml\preprocessing.py
type nul > backend\tests\__init__.py
type nul > backend\tests\test_ingestion.py
type nul > backend\tests\test_predictor.py
type nul > backend\tests\test_routes.py

:: ── Frontend
mkdir frontend\app\pages
mkdir frontend\tests

type nul > frontend\Dockerfile
type nul > frontend\pyproject.toml
type nul > frontend\.python-version
type nul > frontend\app\__init__.py
type nul > frontend\app\main.py
type nul > frontend\app\pages\__init__.py
type nul > frontend\app\pages\jobs.py
type nul > frontend\app\pages\predict.py
type nul > frontend\app\pages\upload.py
type nul > frontend\tests\__init__.py
type nul > frontend\tests\test_ui.py

:: ── Scripts
mkdir scripts
type nul > scripts\clean_data.py
type nul > scripts\extract_skills.py
type nul > scripts\load_to_sql.py

echo.
echo Structure creee avec succes !
echo.
echo Prochaines etapes :
echo   1. Remplir .env avec vos credentials Azure
echo   2. cd terraform ^&^& terraform init
echo   3. uv init ^&^& uv sync  (dans backend\ et frontend\)

endlocal
pause