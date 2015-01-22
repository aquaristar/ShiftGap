from django.core.management.base import BaseCommand, CommandError

from apps.shifts.tasks import twenty_four_hour_reminder, ninety_minute_reminder


class Command(BaseCommand):
    args = 'None'
    help = 'Sends reminders to users about when they work'

    def handle(self, *args, **options):
        twenty_four_hour_reminder.delay()
        ninety_minute_reminder.delay()
        self.stdout.write('Successfuly processed reminders')