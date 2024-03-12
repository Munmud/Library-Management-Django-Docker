from django.contrib import admin
from django.utils.translation import gettext as _
# Register your models here.
from .models import Book, Category, Reservation, Bill, Rating, Notebook, Note


admin.site.register(Notebook)
admin.site.register(Note)
admin.site.register(Book)
admin.site.register(Bill)
admin.site.register(Rating)
admin.site.register(Category)

# class BillAdmin(admin.ModelAdmin):
#     pass
#     # list_display = ['id','user', 'amount', 'reason', 'isActive' ]
#     # list_editable = ['isActive']
#     # list_filter = ['isActive',]
#     # search_fields = ['user__username']
#     # readonly_fields = [ 'user', 'amount', 'reason', 'reservation']

# admin.site.register(Bill, BillAdmin)


class ReservationAdmin(admin.ModelAdmin):

    list_display = ['id', 'book', 'user', 'status']
    list_editable = ['status']
    list_filter = ['status',]
    search_fields = ['book__name', 'user__username']
    readonly_fields = ['requested_at', 'reserved_at',
                       'expected_return_date', 'isActive']
    fieldsets = (
        (None, {'fields': ('book', 'user')}),
        (_('Other Info'),
            {
                'fields': (
                    'requested_at',
                    'reserved_at',
                    'expected_return_date',
                    'isActive'
                )
        }
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('book', 'user')
        }),
    )


admin.site.register(Reservation, ReservationAdmin)
