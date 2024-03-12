from django.conf import settings
from django.db import transaction
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from library.forms import RatingForm
from library.models import Book, Reservation, Bill, Rating, RATING_CHOICE, Category

def get_navbar_context(context):
    context['cats'] = Category.objects.all()
    return context


# @login_required()f
def dashboard(request):

    books = Book.objects.all()

    
    category_name = request.GET.get('category')
    search_query = request.GET.get('search')
    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            books = Book.objects.filter(category=category)
        except Category.DoesNotExist:
            books = []
    elif search_query:
        books = books.filter(Q(author__icontains=search_query) | 
                     Q(name__icontains=search_query))


    paginator = Paginator(books, 9)  # Show 9 books per page

    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        books = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        books = paginator.page(paginator.num_pages)

    context = {
        'books': books,
    }
    context = get_navbar_context(context)
    return render(request, 'dashboard.html', context)

@login_required()
def book_details(request, book_id):
    user = get_object_or_404(User, username=request.user)
    book = get_object_or_404(Book, id=book_id)
    reservation = Reservation.objects.filter(book=book, user=user, status='PENDING')
    context = {
        'book':  book,
        'reservation' : None,
        'rating' : Rating.objects.filter(book = book).aggregate(Avg('rating'))['rating__avg'],
    }
    if (len(reservation) == 1) :
        context['reservation'] = reservation[0]
    context = get_navbar_context(context)
    return render(request, 'users/book_detail.html', context)

@login_required()
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user = get_object_or_404(User, username=request.user)

    if request.method == 'POST':
        if (book.availability == False):
            messages.error(request, f"{book} is not currently available")
        elif len(Reservation.objects.filter(
             user = user, 
             isActive = True, 
             book = book)
        ) == 1:
             messages.error(request, f"You already have requested this Book")
        elif len(Reservation.objects.filter(user = user, isActive = True )) >=settings.USER_BOOK_ACTIVE_COUNT:
             messages.error(request, f"Can't Request books. You already have {settings.USER_BOOK_ACTIVE_COUNT} active request")
        else:
            with transaction.atomic():
                try:
                    book.available_copy -=1
                    if (book.available_copy == 0):
                        book.availability = False
                    book.save()
                    Reservation.objects.create(user=user, book=book)
                    messages.success(request, f"Reservation for '{book.name}' has been successfully made.")
                except Exception as e:
                    transaction.set_rollback(True)
                    messages.error(request, e)
        return redirect('book_detail', book_id=book_id)
    else:
        return redirect('book_detail', book_id=book_id)

@login_required()
def myrequests(request):
    user = get_object_or_404(User, username=request.user)
    context = {
        'reservations': Reservation.objects.filter(user=user).order_by('-requested_at')
    }
    return render(request, 'users/myrequest.html', context)

@login_required()
def cancel_reservation(request, reservation_id):
    user = get_object_or_404(User, username=request.user)
    with transaction.atomic():
        try:
            reservation = get_object_or_404(Reservation, id=reservation_id)
            if not (reservation.status == 'PENDING'):
                raise Exception('Cannot Cancel Request when status is {reservation.status}')
            reservation.status = "CANCELLED"
            reservation.save()
            messages.success(request, f"Successfully Cancelled your request for {reservation.book.name}")
        except Exception as e:
            transaction.set_rollback(True)
            messages.error(request, e)
    return redirect('myrequests')

@login_required()
def lost_book(request, reservation_id):
    user = get_object_or_404(User, username=request.user)
    with transaction.atomic():
        try:
            reservation = get_object_or_404(Reservation, id=reservation_id)
            if not (reservation.status == 'APPROVED'):
                raise Exception('Cannot Cancel Request when status is {reservation.status}')
            reservation.status = "CANCELLED"
            reservation.save()
            messages.success(request, f"Successfully Cancelled your request for {reservation.book.name}. Please pay your bill")
        except Exception as e:
            transaction.set_rollback(True)
            messages.error(request, e)
    return redirect('myrequests')

@login_required()
def my_bill(request):
    user = get_object_or_404(User, username=request.user)
    context = {
        'bills': Bill.objects.filter(user=user).order_by('-created_at')
    }
    return render(request, 'users/mybill.html', context)

@login_required()
def pay_bill(request, bill_id):
    user = get_object_or_404(User, username=request.user)
    with transaction.atomic():
        try:
            bill = get_object_or_404(Bill, id=bill_id, user=user)
            if not bill.isActive :
                raise Exception('This bill is already paid')
            bill.isActive = False
            bill.save()
            messages.success(request, f"You have successfully paid {bill.amount}")
        except Exception as e:
            transaction.set_rollback(True)
            messages.error(request, e)
    return redirect('my_bill')

@login_required()
def give_rating(request, book_id):
    user = get_object_or_404(User, username=request.user)
    book = get_object_or_404(Book, id = book_id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            try:
                rating = Rating.objects.get(user = user, book = book)
                rating.rating = form.data['rating']
                rating.review = form.data['review']
                rating.save()
            except:
                rating = Rating.objects.create(
                    user = user, 
                    book = book, 
                    rating = form.data['rating'],
                    review = form.data['review']
                )

            # print(form.data)
            # form.save()
            return redirect('book_detail',book_id = book_id)  # Redirect to a success page
    else:
        try:
            rating = Rating.objects.get(user=user, book = book)
            initial_values = {
                'rating': rating.rating,  # Initial value for rating field
                'review': rating.review,  # Initial value for review field
            }
            form = RatingForm(initial=initial_values)
        except:
            form = RatingForm()
    books = Book.objects.all()  # Assuming you have a Book model
    rating_choices = RATING_CHOICE  # Assuming you have defined choices in your Review model
    
    return render(request, 'users/rating.html', {'form': form, 'books': books, 'rating_choices': rating_choices})