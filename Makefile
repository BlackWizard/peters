freeze:
	uv pip freeze | uv pip compile - -o requirements.txt

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

head:
	alembic upgrade head

auto:
	alembic revision --autogenerate -m "Auto"
