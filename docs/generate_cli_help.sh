#! /bin/bash

# quick and dirty way to make sure the CLI help is up to date

echo "Generating CLI help for Neurodocker and its subcommands..."

neurodocker --help > user_guide/cli_help.txt
neurodocker generate --help > user_guide/generate_cli_help.txt
neurodocker generate docker --help > user_guide/generate_docker_cli_help.txt
neurodocker generate singularity --help > user_guide/generate_singularity_cli_help.txt
neurodocker minify --help > user_guide/minify_cli_help.txt
