from django.contrib import admin

# Register your models here.
from .models import Post

#Added fields to posts admin page.
class PostModelAdmin(admin.ModelAdmin):
    list_display = ["title", "updated", "timestamp"]
    list_display_links = ["updated"]
    list_editable = ["title"]
    list_filter = ["updated", "timestamp"]

    search_fields = ["title", "content"]

    class Meta:
        model = Post

#Registers the post model into our admin site.
admin.site.register(Post, PostModelAdmin)


