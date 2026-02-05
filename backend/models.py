from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    points = models.IntegerField(default=0)
    badges = models.ManyToManyField('Badge', blank=True)

    def __str__(self):
        return self.username


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, related_name='courses')

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    content = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return self.title


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='quizzes', on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=200)

    def __str__(self):
        return self.question


class Point(models.Model):
    user = models.ForeignKey(User, related_name='points', on_delete=models.CASCADE)
    points = models.IntegerField()
    date_awarded = models.DateTimeField(auto_now_add=True)


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
