from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class TrainingOption(models.Model):
    # خيارات التدريب: OnDemand, Live, Workshop, Bootcamp, Mentorship
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    options = models.ManyToManyField(TrainingOption, related_name='courses', blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    duration_seconds = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        unique_together = ('module', 'order')
        indexes = [
            models.Index(fields=['module', 'order']),
        ]

class Resource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=255)
    file_url = models.URLField()

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('user', 'course')
        indexes = [models.Index(fields=['course', 'user'])]

class Session(models.Model):
    # live session (for Live/Workshop option)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    start = models.DateTimeField()
    end = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=100)

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    max_score = models.IntegerField(default=100)
