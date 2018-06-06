clean-pyc:
	find . -name "*.pyc" -type f -exec rm -f {} +
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean: clean-pyc
	rm -f examples/Dockerfile
	rm -f examples/Singularity
