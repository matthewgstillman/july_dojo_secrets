from django.shortcuts import render, redirect
from .models import User, Secret
from django.contrib import messages
from django.db.models import Count

# Create your views here.
def index(request):
    users = User.objects.all()
    for user in users:
        print user.email
    if 'messages' in request.session:
        context={
        'messages': request.session['messages']
        }
        del request.session['messages']
    else:
        context = {
        'messages': [],
        'users': users
        }
    return render(request, 'july_dojo_secrets/index.html')

def register(request):
    #print request.POST
    if request.method == 'POST':
        messages = User.objects.register(request.POST)
        #Above line might be postData
    if not messages:
        print "No messages! Success!"
        # fetch user id and name via email
        user_list = User.objects.all().filter(email=request.POST['email'])
        request.session['id'] = user_list[0].id
        request.session['name'] = user_list[0].first_name
        return redirect('/secrets')
    else:
        request.session['messages'] = messages
        print messages
    return redirect('/')

def login(request):
    users = User.objects.all()
    postData = {
        'email': request.POST['email'],
        'password': request.POST['password'],
    }
    if request.method == 'POST':
        messages = User.objects.login(request.POST)
    if not messages:
        print "No messages! Success!"
        user_list = User.objects.all().filter(email=request.POST['email'])
        request.session['id'] = user_list[0].id
        request.session['name'] = user_list[0].first_name
        return redirect('/secrets')
    else:
        request.session['messages'] = messages
        return redirect('/')

def process(request):
    if request.method=='GET':
        return redirect('/')
    print "In the process, going to make a secret", request.POST
    result = Secret.objects.validate(request.POST['secret'], request.session['id'])
    if result[0]:
        messages.info(request, result[1])
        return redirect('/secrets')
    messages.error(request, result[1])
    return redirect('/secrets')

def secrets(request):
    # Collect all secrets and send to the template
    allsecrets = Secret.objects.all().order_by('-id')[:5]
    context={
        'secrets' : allsecrets,
        'currentuser' : User.objects.get(id=request.session['id'])
    }
    return render(request, 'july_dojo_secrets/secrets.html', context)

def newlike(request, id, sentby):
    # We are receiving the id of the secret
    print "we are in the new like", id
    result = Secret.objects.newlike(id, request.session['id'])
    if result[0] == False:
        messages.error(request, result[1])
    if sentby == "sec":
        return redirect('/secrets')
    else:
        return redirect('/popular')


def delete(request, id, sentby):
    print "we are in the delete", id
    result = Secret.objects.deleteLike(id, request.session['id'])
    if result[0] == False:
        messages.error(request, result[1])
    if sentby == "sec":
        return redirect('/secrets')
    else:
        return redirect('/popular')


def popular(request):
    allsecrets = Secret.objects.annotate(num_likes=Count('likers')).order_by('-num_likes')[:5]
    context = {
        'secrets': allsecrets,
        'currentuser': User.objects.get(id=request.session['id'])
    }
    return render(request, 'july_dojo_secrets/popular.html', context)
