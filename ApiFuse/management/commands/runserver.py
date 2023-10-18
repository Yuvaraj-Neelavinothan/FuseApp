from django.core.management.commands.runserver import Command as BaseRunserverCommand

class Command(BaseRunserverCommand):
    def handle(self, *args, **options):
        # Set the desired port number here (e.g., 8080)
        options['addrport'] = "127.0.0.1:8070"
        super().handle(*args, **options)
