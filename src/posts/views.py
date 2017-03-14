from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

# Create your views here.
from .forms import PostForm
from .models import Post

def post_create(request):
    #Added basic user permissions
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        instance.user = request.user
        # message success
        messages.success(request, "Successfully Created")
        #Redirect to detale page
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "post_form.html", context)

def post_detail(request, slug=None):
#def post_detail(request, id=None):
    #Get Item or 404 Query
    #instance = get_object_or_404(Post, id=id)
    instance = get_object_or_404(Post, slug=slug)

    #Handling Drafts.
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    context = {
        "title": instance.title,
        "instance": instance
    }
    return render(request, "post_detail.html", context)

def post_update(request, slug=None):
    #Added basic user permissions
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    #Get Item or 404 Query
    #instance = get_object_or_404(Post, id=id)
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, "post_form.html", context)

def post_list(request):
    #Get Post object.
    #queryset = Post.objects.all()
    #queryset_list = Post.objects.all()  # .order_by("-timestamp")
    # Handling Drafts.
    today = timezone.now().date()
    queryset_list = Post.objects.active()  # .order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()

    #Search Posts
    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query)
        ).distinct()

    #Added pagination.
    paginator = Paginator(queryset_list,  2) # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)

    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        #If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        #If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        "object_list": queryset,
        "title": "List",
        "page_request_var": page_request_var,
        "today": today,
    }
    return render(request, "post_list.html", context)

def post_delete(request):
    #Added basic user permissions
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    #instance = get_object_or_404(Post, id=id)
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Successfully deleted")
    return redirect("posts:list")