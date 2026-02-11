import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from faker import Faker
# تأكد من تغيير 'myapp' لاسم التطبيق الفعلي لديك
from api.models import (
    Instructor, Category, TrainingOption, Course, 
    Module, Lesson, Resource, Enrollment, Quiz
)

User = get_user_model()

# إعداد Faker لتوليد بيانات باللغة الإنجليزية (يمكنك تغييرها لـ 'ar_AA' للعربية)
fake = Faker('en_US')

class Command(BaseCommand):
    help = "Generates fake data for the eLearning platform"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Start seeding data...'))
        
        # استخدام Atomic Transaction لضمان سرعة الإدخال وعدم تخزين نصف البيانات في حال الخطأ
        with transaction.atomic():
            self.clear_data()
            self.create_training_options()
            categories = self.create_categories()
            instructors = self.create_users_and_instructors()
            self.create_courses_structure(instructors, categories)
            
        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))

    def clear_data(self):
        """حذف البيانات القديمة لتجنب التكرار عند التجربة"""
        self.stdout.write('Deleting old data...')
        # الترتيب مهم هنا بسبب الـ Foreign Keys
        Enrollment.objects.all().delete()
        Resource.objects.all().delete()
        Lesson.objects.all().delete()
        Module.objects.all().delete()
        Quiz.objects.all().delete()
        Course.objects.all().delete()
        Instructor.objects.all().delete()
        Category.objects.all().delete()
        TrainingOption.objects.all().delete()
        # حذف المستخدمين ما عدا السوبر يوزر
        User.objects.filter(is_superuser=False).delete()

    def create_training_options(self):
        options = ['OnDemand', 'Live', 'Workshop', 'Bootcamp', 'Mentorship']
        for name in options:
            TrainingOption.objects.create(name=name, description=fake.sentence())
        self.stdout.write(f'Created {len(options)} Training Options')

    def create_categories(self):
        cats_names = ['Web Development', 'Data Science', 'Mobile Apps', 'DevOps', 'UI/UX Design']
        categories = []
        for name in cats_names:
            cat = Category.objects.create(name=name, slug=slugify(name))
            categories.append(cat)
        self.stdout.write(f'Created {len(categories)} Categories')
        return categories

    def create_users_and_instructors(self):
        instructors = []
        # إنشاء 10 مدربين
        for _ in range(10):
            # إنشاء User
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,99)}"
            email = f"{username}@example.com"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123', # كلمة سر موحدة للتجربة
                first_name=first_name,
                last_name=last_name
            )
            
            # إنشاء Instructor
            instructor = Instructor.objects.create(
                user=user,
                bio=fake.paragraph(),
                rating=round(random.uniform(3.5, 5.0), 1)
            )
            instructors.append(instructor)
            
        self.stdout.write(f'Created {len(instructors)} Instructors')
        return instructors

    def create_courses_structure(self, instructors, categories):
        # إنشاء 50 طالب
        students = []
        for _ in range(50):
            u = User.objects.create_user(
                username=fake.user_name(), 
                email=fake.email(), 
                password='password123'
            )
            students.append(u)

        training_opts = list(TrainingOption.objects.all())
        
        # إنشاء 20 كورس
        for i in range(20):
            title = fake.catch_phrase()  # عنوان جذاب
            slug = slugify(title) + f"-{i}" # لضمان عدم التكرار
            
            course = Course.objects.create(
                title=title,
                slug=slug,
                instructor=random.choice(instructors),
                category=random.choice(categories),
                published=random.choice([True, True, False]), # فرصة أكبر للنشر
            )
            
            # إضافة خيارات تدريب عشوائية (Many-to-Many)
            course.options.set(random.sample(training_opts, k=random.randint(1, 2)))
            
            # إنشاء Modules (وحدات)
            for m_order in range(1, random.randint(3, 6)): # من 3 لـ 5 وحدات
                module = Module.objects.create(
                    course=course,
                    title=f"Module {m_order}: {fake.bs().title()}",
                    order=m_order
                )
                
                # إنشاء Lessons (دروس)
                for l_order in range(1, random.randint(3, 8)):
                    lesson = Lesson.objects.create(
                        module=module,
                        title=fake.sentence(nb_words=4).replace('.', ''),
                        duration_seconds=random.randint(300, 3600), # 5 دقيقة إلى ساعة
                        order=l_order,
                        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ" # رابط وهمي
                    )
                    
                    # إنشاء Resources (مصادر) أحياناً
                    if random.choice([True, False]):
                        Resource.objects.create(
                            lesson=lesson,
                            name=f"Download: {fake.file_name(extension='pdf')}",
                            file_url="http://example.com/file.pdf"
                        )

            # إنشاء Enrollments (تسجيلات طلاب)
            if course.published:
                # اختر عشوائياً 5 إلى 15 طالب لهذا الكورس
                course_students = random.sample(students, k=random.randint(5, 15))
                for std in course_students:
                    Enrollment.objects.create(
                        user=std,
                        course=course,
                        progress=random.choice([0.0, 10.0, 50.0, 100.0])
                    )

            # إنشاء Quiz (اختبار)
            Quiz.objects.create(
                course=course,
                title=f"Final Quiz for {course.title}",
                max_score=100
            )

        self.stdout.write(f'Created Courses, Modules, Lessons, and Enrollments')