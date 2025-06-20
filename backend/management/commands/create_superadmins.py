from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create super admin users for BueaDelights'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if users exist',
        )

    def handle(self, *args, **options):
        # Define super admin users
        super_admins = [
            {
                'username': 'folefack_caroline',
                'email': 'folefacvivianekokoko@gmail.com',
                'first_name': 'Caroline',
                'last_name': 'Folefack',
                'password': '@caroline2025'
            },
            {
                'username': 'momo_godi_yvan',
                'email': 'yvangodimomo@gmail.com',
                'first_name': 'Yvan',
                'last_name': 'Momo Godi',
                'password': '@momoyvan65'
            },
            {
                'username': 'momo_marlyse',
                'email': 'momomarlyse@gmail.com',
                'first_name': 'Marlyse',
                'last_name': 'Momo',
                'password': '@momoyvan65'
            }
        ]

        created_count = 0
        updated_count = 0

        for admin_data in super_admins:
            username = admin_data['username']
            
            try:
                # Try to get existing user
                user = User.objects.get(username=username)
                
                if options['force']:
                    # Update existing user
                    user.email = admin_data['email']
                    user.first_name = admin_data['first_name']
                    user.last_name = admin_data['last_name']
                    user.set_password(admin_data['password'])
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.save()
                    
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Updated existing super admin: {username}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Super admin {username} already exists. Use --force to update.'
                        )
                    )
                    
            except User.DoesNotExist:
                # Create new user
                try:
                    user = User.objects.create_superuser(
                        username=username,
                        email=admin_data['email'],
                        password=admin_data['password'],
                        first_name=admin_data['first_name'],
                        last_name=admin_data['last_name']
                    )
                    
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created super admin: {username}'
                        )
                    )
                    
                except IntegrityError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error creating super admin {username}: {e}'
                        )
                    )

        # Summary
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully created {created_count} super admin(s)'
                )
            )
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully updated {updated_count} super admin(s)'
                )
            )
        
        if created_count == 0 and updated_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  No super admins were created or updated'
                )
            )
        
        # Display login credentials
        self.stdout.write(
            self.style.SUCCESS(
                '\n📋 Super Admin Login Credentials:\n'
                '=================================='
            )
        )
        
        for admin_data in super_admins:
            self.stdout.write(
                f"\n👤 {admin_data['first_name']} {admin_data['last_name']}"
            )
            self.stdout.write(f"   Username: {admin_data['username']}")
            self.stdout.write(f"   Email: {admin_data['email']}")
            self.stdout.write(f"   Password: {admin_data['password']}")
        
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  IMPORTANT: Please change these default passwords after first login!'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🚀 Super admins are ready to access the admin panel at: /admin/'
            )
        )