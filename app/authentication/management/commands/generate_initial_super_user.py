
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from library.models import Book, Category, Reservation, Bill
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a superuser'

    # def add_arguments(self, parser):
    #     # parser.add_argument('--username', type=str, help='Username for the superuser', required=True)
    #     parser.add_argument('--email', type=str, help='Email for the superuser', required=True)
    #     parser.add_argument('--password', type=str, help='Password for the superuser', required=True)

    def handle(self, *args, **kwargs):
        # username = kwargs['username']
        users_data = [
            {'username': 'user1', 'password': 'pass'},
            {'username': 'user2', 'password': 'pass'},
        ]
            # Add more users as needed

        for data in users_data:
            username = data['username']
            password = data['password']
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=password)
                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username} password: {password}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping...'))



        username = 'admin'
        password = 'pass'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser\n\t email:\t\t {username}\n\t password:\t {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping...'))



        username = 'librarian'
        password = 'pass'

        if not User.objects.filter(username=username).exists():
            librarian_user =User.objects.create_user(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'Librarian\n\t email:\t\t {username}\n\t password:\t {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping...'))
        
        if not Group.objects.filter(name='Librarian').exists():

            group, created = Group.objects.get_or_create(name='Librarian')

            models = [Book, Category, Reservation, Bill]
            
            for model in models:
                content_type = ContentType.objects.get_for_model(model)
                permissions = Permission.objects.filter(content_type=content_type)
                group.permissions.add(*permissions)

            librarian_user.groups.add(group)
            librarian_user.is_staff = True
            librarian_user.save()



