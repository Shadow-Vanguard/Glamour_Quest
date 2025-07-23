""" # from django.core.management.base import BaseCommand
# from myapp.models import ServiceCategory, ServiceSubcategory, Service

# class Command(BaseCommand):
#     help = 'Add existing services to the database'

#     def handle(self, *args, **kwargs):
#         # Example data - replace with your existing services
#         services_data = [
#             {
#                 'service_name': 'Feather Cut',
#                 'description': 'A trendy feather cut style.',
#                 'rate': 500,
#                 'subcategory_name': 'Hair Cut',
#                 'category_name': 'Hair Care'
#             },
#             {
#                 'service_name': 'Deep Conditioning',
#                 'description': 'A nourishing deep conditioning treatment.',
#                 'rate': 700,
#                 'subcategory_name': 'Hair Spa',
#                 'category_name': 'Hair Care'
#             },
#             # Add more services here
#         ]

#         for service_data in services_data:
#             category, created = ServiceCategory.objects.get_or_create(name=service_data['category_name'])
#             subcategory, created = ServiceSubcategory.objects.get_or_create(
#                 name=service_data['subcategory_name'],
#                 category=category
#             )
#             service, created = Service.objects.get_or_create(
#                 service_name=service_data['service_name'],
#                 description=service_data['description'],
#                 rate=service_data['rate'],
#                 subcategory=subcategory
#             )

#             if created:
#                 self.stdout.write(self.style.SUCCESS(f'Successfully added {service.service_name}'))
#             else:
#                 self.stdout.write(self.style.WARNING(f'{service.service_name} already exists'))
 """