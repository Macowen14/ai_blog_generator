from django.apps import AppConfig

class BlogGeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_generator'

    def ready(self):
        import blog_generator.signals
