from . import views


from django.urls import path
from .views import ListCourses, CoursesDetails, LessonDetails, ListLesson, CourseCurriculum
urlpatterns = [
    path('courses/',ListCourses.as_view()),
    path('courses/<slug:slug>/curriculum/',CoursesDetails.as_view()),
    path('courses/<slug:slug>/',CourseCurriculum.as_view()),
    path('lessons/',ListLesson.as_view()),
    path('lessons/<int:id>/',LessonDetails.as_view()),
    path('', views.page, name='pages')


]
