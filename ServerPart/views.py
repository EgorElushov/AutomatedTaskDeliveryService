import json

from django.contrib.auth import password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .forms import *
from .models import *
from django.contrib.auth import views as auth_views, login as auth_login
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
from django.utils import timezone


def welcome_page(request):
    return render(request, 'welcome.html')


def register(request):
    context = {'form': RegisterForm}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_ip = UserIp(last_ip=get_client_ip(request), user=user)
            user_ip.save()  # Запись IP-адреса пользователя
            user_inf = UserInfo(info="Новый пользователь", user=user)
            user_inf.save()  # Запись информации пользователя
            user_avatar = Avatar(user_id=user.id)
            user_avatar.save()
            return redirect('/login')
        else:
            context['form'] = form
            context['error'] = form.error_messages
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', context)


class LoginPage(auth_views.LoginView):
    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        try:
            object_with_current_user = UserIp.objects.get(
                user=self.request.user
            )
        except UserIp.DoesNotExist:
            user_ip = UserIp(
                last_ip=get_client_ip(self.request),
                user=form.get_user()
            )
            user_ip.save()
        else:
            """ Получение записи из БД с текущим user'ом """
            object_with_current_user.last_ip = get_client_ip(self.request)
            object_with_current_user.save()  # Запись IP-адреса пользователя
        try:  # Проверка на наличие "информации о пользователе"
            current_user_inf = UserInfo.objects.get(
                user=self.request.user
            )
        except UserInfo.DoesNotExist:
            user_inf = UserInfo(
                info="4to///0_o",
                user=form.get_user()
            )
            user_inf.save()
        return HttpResponseRedirect(self.get_success_url())


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def task_list(request):
    context = {
        "task_list_by_date": Task.objects.order_by("date_created"),
        "user": request.user
    }
    try:
        avatar = Avatar.objects.get(user_id=request.user.id)
    except Avatar.DoesNotExist:
        user_avatar = Avatar(user_id=request.user.id)
        user_avatar.save()
        avatar = Avatar.objects.get(user_id=request.user.id)
    context['avatar'] = avatar
    return render(request, 'task_list.html', context)


@login_required
def show_menu(request):
    avatar = Avatar.objects.get(user_id=request.user.id)
    return render(request, 'menu.html', {'avatar': avatar})


@login_required
def lk(request, user_id):
    context = {}
    avatar = Avatar.objects.get(user_id=request.user.id)
    context['avatar'] = avatar
    us = UserInfo.objects.get(user_id=user_id)
    user = User.objects.get(username=request.user.username)
    context['login'] = request.user.username
    context['info'] = us.info
    if request.method == 'POST':
        f = ChangeInfoForm(request.POST)
        if f.is_valid():
            us.info = f.data['info']
            us.save()
            context['info'] = us.info
            context['form_info'] = f
        else:
            context['form_info'] = f
    else:
        context['form_info'] = ChangeInfoForm
    if request.method == 'POST':
        form = UploadAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            former_avatar = Avatar.objects.get(user_id=request.user.id)
            former_avatar.delete()
            img = request.FILES['image']
            avatar = Avatar(img=img, user_id=user_id)
            avatar.save()
    else:
        pass
    if request.method == 'POST':
        k = ChangePasswordForm(request.POST)
        if k.is_valid():
            old_pass = k.data['old_pass']
            new_pass = k.data['new_pass']
            new_pass_rep = k.data['new_pass_rep']
            if user.check_password(old_pass):
                if new_pass == new_pass_rep:
                    user.set_password(new_pass)
                    user.save()
                    context['message'] = 'Смена пароля прошла успешно!'
                else:
                    context['message'] = 'Введенный пароли не совпадают'
            else:
                context['message'] = 'Старый пароль неверен'
            context['form_pass'] = k
        else:
            context['form_pass'] = k
    else:
        context['form_pass'] = ChangePasswordForm
    context['ImgForm'] = UploadAvatarForm
    if checkout_user(request, user_id):
        return render(request, 'lk.html', context)
    else:
        return HttpResponse(status=403, content="403 ErrOr")


def checkout_user(request, user_id):  # Функция для проверки ID пользователя в запросе
    if request.user.is_authenticated:
        if request.user.id == user_id:
            return True
    else:
        return False


@user_passes_test(lambda u: u.is_superuser)
def create_task(request):
    context = {"menu": show_menu(request)}
    avatar = Avatar.objects.get(user_id=request.user.id)
    context['avatar'] = avatar
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        print(name, description)
        if name == '':
            return HttpResponse(status=400, content="Название не может быть пустым")
        elif "'" in name or '|' in name:
            return HttpResponse(status=400, content="Название не может содержать символы ' и |")
        if description == '':
            return HttpResponse(status=400, content="Описание не может быть пустым")
        elif "'" in description or '|' in description:
            return HttpResponse(status=400, content="Описание не может содержать символы ' и |")
        img_amount = request.POST.get('img_amount')
        if int(img_amount) != 0:
            images = request.FILES.getlist('images')
        author = user
        date_created = timezone.now()
        end_date = request.POST.get('end_date', None)
        end_time = request.POST.get('end_time', None)
        if end_date != 'undefined':
            if end_time == 'undefined':
                end_time = '00:00'
            task = Task(
                name=name,
                author=author,
                date_created=date_created,
                deadline=datetime.strptime(end_date + ' ' + end_time, '%Y-%m-%d %H:%M'),
                description=description,
                img_amount=int(img_amount)
            )
        else:
            task = Task(
                name=name,
                author=author,
                date_created=date_created,
                description=description,
                img_amount=int(img_amount)
            )
        print(task)
        task.save()
        print(Task.objects.all())
        if int(img_amount) != 0:
            for i in images:
                img = Images(img=i, task=task)
                img.save()

    return render(request, 'task_creating.html', context)


def show_task(request, task_id):
    task = Task.objects.get(id=task_id)
    user = User.objects.get(username=request.user.username)
    developers_count = Developer.objects.filter(task=task_id).count()
    avatar = Avatar.objects.get(user_id=request.user.id)
    if Developer.objects.filter(task=task.id, user=request.user).exists():
        exists = 1
    else:
        exists = 0
    if task.deadline is not None:
        deadline_overdue = task.deadline < timezone.now() or task.is_done
    else:
        deadline_overdue = task.is_done
    if request.method == "POST":
        usual_dict = dict(request.POST)
        if 'action' in usual_dict:
            if request.POST.get('action') == 'add':
                developer = Developer(
                    task=task,
                    user=request.user,
                    date_created=datetime.now()
                )
                developer.save()
                exists = 1
            elif request.POST.get('action') == 'delete':
                developer = Developer.objects.get(task=task.id, user=request.user)
                developer.delete()
                exists = 0
            else:
                if exists:
                    task.is_done = True
                    task.save()
        elif 'comment_text' in usual_dict:
            comment_text = request.POST.get("comment_text")
            task_id = task_id

            comment = Comments(
                task_id=task_id,
                comment_text=str(comment_text),
                avatar=Avatar.objects.get(user_id=request.user.id),
                user=user
            )
            comment.save()

            return HttpResponseRedirect(request.path_info)
        elif 'delete_comment' in usual_dict:
            delete_id = request.POST.get("delete_comment")
            Comments.objects.filter(id=delete_id).delete()

    comments_list = Comments.objects.filter(task_id=task_id)
    task_images = Images.objects.filter(task_id=task_id)
    developers = Developer.objects.filter(task=task.id)
    return render(request, 'show.html', {
        'task': task,
        'CommentForm': CommentForm,
        'comments': comments_list,
        'exists': exists,
        'developers_count': developers_count,
        'avatar': avatar,
        'task_images': task_images,
        'deadline_overdue': deadline_overdue,
        'user_id': request.user.id,
        'developers': developers
    }
                  )


@login_required
def history_page(request, user_id):
    context = {"menu": show_menu(request)}
    avatar = Avatar.objects.get(user_id=request.user.id)
    context['avatar'] = avatar
    user = User.objects.get(username=request.user.username)
    tasks = []
    developers_tasks = Developer.objects.filter(user=user)
    for i in developers_tasks:
        tasks.append(i.task)
    if not tasks:
        context['no_task'] = True
    else:
        context['no_task'] = False
    context['history_development'] = tasks

    if checkout_user(request, user_id):
        return render(request, 'history.html', context)
    else:
        return HttpResponse(status=403, content="Это не твоё!!!!")


@login_required
def doing_task_list(request, user_id):
    developed_list = Developer.objects.filter(user=user_id)
    tasks = []
    for i in developed_list:
        if not i.task.is_done:
            tasks.append(i.task)
    context = {
        "tasks_list": tasks,
        "user": request.user,
        "tasks_count": len(tasks)
    }
    avatar = Avatar.objects.get(user_id=request.user.id)
    context['avatar'] = avatar
    return render(request, 'doing_tasks_list.html', context)

