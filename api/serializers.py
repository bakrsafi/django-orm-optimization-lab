from .models import Course, Instructor, Category , TrainingOption, Lesson, Module
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


from django.contrib.auth import get_user_model

User = get_user_model()


# class UserSerializer(ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username']



class InstructorSerializer(ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Instructor
        fields = ['user', 'rating']

class TrainingOptionSerializer(ModelSerializer):
    class Meta:
        model = TrainingOption
        fields = '__all__'

class CourseSerializer(ModelSerializer):
    category = serializers.CharField(source='category.name',read_only=True)
    instructor = InstructorSerializer(read_only=True)
    number_of_modules = serializers.IntegerField(read_only=True)
    number_of_lessons = serializers.IntegerField(read_only=True)
    total_video_duration = serializers.IntegerField(read_only=True)
    number_of_students = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'category', 'instructor', 'number_of_modules', 'number_of_lessons', 'total_video_duration', 'number_of_students']


class LessonSerializer(ModelSerializer):
    module_name = serializers.CharField(source='module.title')
    course_title = serializers.CharField(source='module.course.title')
    resources_count = serializers.IntegerField(read_only=True)
    previous_lesson = serializers.SerializerMethodField()
    next_lesson = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url', 'duration_seconds',
                  'module_name',
                  'course_title',
                  'resources_count',
                  'next_lesson', 'previous_lesson'
                  ]
    def __init__(self, *args, **kwargs):
        # Pop the optional "fields" argument
        fields = kwargs.pop('fields', None)

        # Instantiate normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def get_previous_lesson(self, obj):
        prev = self.context.get('previous_lesson')
        if not prev:
            return None
        return {"id": prev.id, "title": prev.title}

    def get_next_lesson(self, obj):
        nxt = self.context.get('next_lesson')
        if not nxt:
            return None
        return {"id": nxt.id, "title": nxt.title}
    
    
    
class LessonCurriculumSerializer(serializers.ModelSerializer):
    resources_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'duration_seconds', 'resources_count']


class ModuleCurriculumSerializer(serializers.ModelSerializer):
    lessons = LessonCurriculumSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'lessons']


class CourseCurriculumSerializer(serializers.ModelSerializer):
    modules = ModuleCurriculumSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'modules']
