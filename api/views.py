from django.shortcuts import render 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Course ,Category, Instructor, Lesson, Module
from .serializers import CourseSerializer, LessonSerializer, CourseCurriculumSerializer
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404


class ListCourses(APIView):

    def get(self, request):
        queryset = Course.objects.select_related(
        'category', 'instructor', 'instructor__user'
        ).annotate(
            number_of_modules=Count('modules', distinct=True),
            number_of_lessons=Count('modules__lessons', distinct=True),
            total_video_duration=Count('modules__lessons__resources', distinct=True),
            number_of_students=Count('enrollments', distinct=True)
        )  
        serializer = CourseSerializer(queryset, many=True)
        return Response(serializer.data)

class CoursesDetails(APIView):

    def get(self, request, slug):
        queryset = Course.objects.filter(id=slug).select_related(
        'category', 'instructor', 'instructor__user'
        ).annotate(
            number_of_modules=Count('modules', distinct=True),
            number_of_lessons=Count('modules__lessons', distinct=True),
            total_video_duration=Count('modules__lessons__resources', distinct=True),
            number_of_students=Count('enrollments', distinct=True)
        )  
        serializer = CourseSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class ListLesson(APIView):
    def get(self, request):
        queryset = Lesson.objects.all().select_related('module', 'module__course')
        serializer = LessonSerializer(
            queryset,
            many=True,
            fields=['id', 'title', 'video_url', 'course_title', 'module_name', 'duration_seconds'],
            )
        return Response(serializer.data)
    
    
class LessonDetails(APIView):
    def get(self, request, id):
        lesson = get_object_or_404(Lesson.objects.select_related('module', 'module__course'), id=id)
        previous_lesson = Lesson.objects.filter(
            module=lesson.module,
            order__lt=lesson.order
        ).order_by('-order').first()

        next_lesson = Lesson.objects.filter(
            module=lesson.module,
            order__gt=lesson.order
        ).order_by('order').first()

        serializer = LessonSerializer(
            lesson,
            context={
                'previous_lesson': previous_lesson,
                'next_lesson': next_lesson
            }
        )
        return Response(serializer.data)
        
        
class CourseCurriculum(APIView):

    def get(self, request, slug):

        lessons_qs = Lesson.objects.annotate(
            resources_count=Count('resources', distinct=True)
        )

        modules_qs = Module.objects.prefetch_related(
            Prefetch('lessons', queryset=lessons_qs)
        )

        course = get_object_or_404(
            Course.objects.prefetch_related(
                Prefetch('modules', queryset=modules_qs)
            ),
            slug=slug
        )

        serializer = CourseCurriculumSerializer(course)
        return Response(serializer.data)
