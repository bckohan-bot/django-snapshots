from django.apps import AppConfig


class {{cookiecutter.project_slug.title().replace('-', '').replace('_', '')}}Config(AppConfig):
    name = "{{cookiecutter.package_name}}"
    verbose_name = "{{cookiecutter.project_slug.replace('-', ' ').replace('_', ' ').title()}}"
