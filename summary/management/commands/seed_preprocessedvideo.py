from django.core.management.base import BaseCommand
from django_seed import Seed
from summary.models import PreprocessedVideo, Video
from faker import Faker
import random

class Command(BaseCommand):
    help = "Seeds the database with PreprocessedVideo data"

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='Number of PreprocessedVideos to seed')

    def handle(self, *args, **options):
        number = options['number']
        seeder = Seed.seeder()
        faker = Faker()

        # Video 모델이 존재하는지 확인하고, 없다면 생성
        if Video.objects.exists():
            video = random.choice(Video.objects.all())
        else:
            video = Video.objects.create(
                video_id=faker.lexify(text='??????????'),
                title=faker.sentence(),
                channel_title=faker.name(),
                published_at=faker.past_date(),
                view_count=faker.random_number(digits=5)
            )

        seeder.add_entity(PreprocessedVideo, number, {
            'originalText': lambda x: ' '.join(faker.paragraphs(nb=random.randint(5, 10))),
            'video': lambda x: video,
        })

        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {number} PreprocessedVideos.'))
