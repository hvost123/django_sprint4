from django.contrib import admin

from blog.models import Category, Location, Post, Comment


admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'category',
        'location',
        'author',
        'pub_date'
    )
    list_editable = (
        'is_published',
        'pub_date',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'post'
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Comment, CommentAdmin)
