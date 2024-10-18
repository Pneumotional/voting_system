from django.contrib import admin
from django.db.models import Count
from .models import Code, Category, Candidate, Vote

# Admin configuration for the Code model
class CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'is_used', 'expires_at')
    search_fields = ('code',)
    list_filter = ('is_used',)

# Admin configuration for the Category model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Admin configuration for the Candidate model
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

# Admin configuration for the Vote model
class VoteAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'vote_count')  # Show candidate and their vote count

    def get_queryset(self, request):
        # Get the default queryset and annotate it with vote counts
        queryset = super().get_queryset(request)
        return queryset.annotate(vote_count=Count('candidate__vote')).order_by('-vote_count')

    def vote_count(self, obj):
        # Return the vote count for the candidate
        return Vote.objects.filter(candidate=obj.candidate).count()
    
    vote_count.short_description = 'Number of Votes'  # Set a short description for the column

# Register models with the admin site
admin.site.register(Code, CodeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Vote, VoteAdmin)
