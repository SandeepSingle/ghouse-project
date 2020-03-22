from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404,get_list_or_404  # For displaying in template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import Signup, ReservationForm, CheckInRequestForm
from .models import Room, Reservation, Customer, Staff  # Import Models


def index(request):
    """
    This is the view for homepage.
    This is a function based view.
    """
    page_title = _("GuestHouse Management System")  # For page title as well as heading
    total_num_rooms = Room.objects.all().count()
    available_num_rooms = Room.objects.exclude(reservation__isnull=False).count()
    available_num_rooms_Cat= Room.objects.filter(room_type=2).count()
    print(available_num_rooms_Cat)
    total_num_reservations = Reservation.objects.all().count()
    total_num_staffs = Staff.objects.all().count()
    total_num_customers = Customer.objects.all().count()
    if total_num_reservations == 0:
        last_reserved_by = Reservation.objects.none()
    else:
        last_reserved_by = Reservation.objects.get_queryset().latest('reservation_date_time')

    return render(
        request,
        'index.html',
        # context is whatever sent to the template.
        # the index of the dictionary i.e. title in 'title': page_title
        # is used as variable in templates
        # where as the next one is the variable of this function
        {
            'title': page_title,
            'total_num_rooms': total_num_rooms,
            'available_num_rooms': available_num_rooms,
            'total_num_reservations': total_num_reservations,
            'total_num_staffs': total_num_staffs,
            'total_num_customers': total_num_customers,
            'last_reserved_by': last_reserved_by,
        }
    )


@transaction.atomic
def signup(request):
    title = "Signup"
    if request.user.is_authenticated:
        request.session.flush()
    if request.method == 'POST':
        form = Signup(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # staffs_group = get_object_or_404(Group, name__iexact="Staffs")
                    form.save()
                    print(staff_id)
                    s = get_object_or_404(Staff, staff_id__exact=staff_id)
                    s.user = get_object_or_404(User, username__iexact=username)
                    s.user.set_password(form.cleaned_data['password1'])
                    # s.user.groups.add(staffs_group)
                    s.user.save()
                    s.save()
            except IntegrityError:
                raise Http404
            return redirect('index')
    else:
        form = Signup()

    return render(
        request,
        'signup.html', {
            'form': form, 'title': title},
    )


@permission_required('main.add_reservation', 'login', raise_exception=True)
@transaction.atomic
def reserve(request):
    title = "Add Reservation"
    print("calling reserve")
    reservation = Reservation.objects.none()
    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST)
        print("method post")
        print(reservation_form.error_messages)
        if reservation_form.is_valid():
            print("form valid")
            try:
                with transaction.atomic():
                    customer = Customer()
                    customer.first_name=reservation_form.cleaned_data.get('first_name')
                    customer.middle_name=reservation_form.cleaned_data.get('middle_name')
                    customer.last_name=reservation_form.cleaned_data.get('last_name')
                    customer.email_address=reservation_form.cleaned_data.get('email')
                    customer.contact_no=reservation_form.cleaned_data.get('contact_no')
                    customer.address=reservation_form.cleaned_data.get('address')
                    customer.save()
                    print("customer is saved",customer)
                    staff1 = request.user
                    reservation = Reservation()
                    staff=Staff.objects.get()
                    
                    reservation.staff=staff
                    reservation.customer=customer
                    reservation.no_of_children=reservation_form.cleaned_data.get('no_of_children')
                    reservation.no_of_adults=reservation_form.cleaned_data.get('no_of_adults')
                    reservation.expected_arrival_date_time=reservation_form.cleaned_data.get('expected_arrival_date_time')
                    reservation.expected_departure_date_time=reservation_form.cleaned_data.get('expected_departure_date_time')
                    reservation.reservation_date_time=timezone.now()
        
                    staff1.save()
                    reservation.save()

                    for room in reservation_form.cleaned_data.get('rooms'):
                        room.reservation = reservation
                        room.save()
            except IntegrityError:
                raise Http404
            return render(
                request,
                'reserve_success.html', {
                    'reservation': reservation,
                }
            )
        else:
            print("Form invalid")
    else:
       
        reservation_form = ReservationForm()

    return render(
        request,
        'reserve.html', {
            'title': title,
            'reservation_form': reservation_form,
        }
    )


def reserve_success(request):
    pass


# For generic ListView or DetailView, the default templates should be stored in templates/{{app_name}}/{{template_name}}
# By default template_name = modelName_list || modelName_detail.
# eg room_list, room_detail
# @permission_required('main.can_view_staff')
class RoomListView(PermissionRequiredMixin, generic.ListView):
    """
    View for list of rooms.
    Implements generic ListView.
    """
    model = Room  # Chooses the model for listing objects
    paginate_by = 5  # By how many objects this has to be paginated
    title = _("Room List")  # This is used for title and heading
    permission_required = 'main.can_view_room'

    # By default only objects of the model are sent as context
    # However extra context can be passed using field extra_context
    # Here title is passed.

    extra_context = {'title': title}

    # By default:
    # template_name = room_list
    # if you want to change it, use field template_name
    # here don't do this, since it is already done as default.
    # for own views, it can be done.

    def get_queryset(self):
        filter_value = self.request.GET.get('filter', 'all')
        if filter_value == 'all':
            filter_value = 0
        elif filter_value == 'avail':
            filter_value = 1
        try:
            new_context = Room.objects.filter(availability__in=[filter_value, 1])
        except ValidationError:
            raise Http404(_("Wrong filter argument given."))
        return new_context

    def get_context_data(self, **kwargs):
        context = super(RoomListView, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        return context


class RoomDetailView(PermissionRequiredMixin, generic.DetailView):
    """
    View for detail of room
    Implements generic DetailView
    """
    # The remaining are same as previous.
    model = Room
    title = _("Room Information")
    permission_required = 'main.can_view_room'
    extra_context = {'title': title}


class ReservationListView(PermissionRequiredMixin, generic.ListView, generic.FormView):
    """
        View for list of reservations.
        Implements generic ListView.
        """
    model = Reservation
    # queryset field selects the objects to be displayed by the query.
    # Here, the objects are displayed by reservation date time in descending order
    queryset = Reservation.objects.all().order_by('-reservation_date_time')
    title = _("Reservation List")
    paginate_by = 5
    allow_empty = True
    form_class = CheckInRequestForm
    success_url = reverse_lazy('check_in-list')
    permission_required = 'main.can_view_reservation'
    extra_context = {'title': title}

    @transaction.atomic
    def form_valid(self, form):
        try:
            with transaction.atomic():
                checkin = form.save(commit=False)
                checkin.user = self.request.user
                checkin.save()
        except IntegrityError:
            raise Http404
        return super().form_valid(form)


class ReservationDetailView(PermissionRequiredMixin, generic.DetailView):
    """
    View for detail of reservation
    Implements generic DetailView
    """
    model = Reservation
    title = _("Reservation Information")
    permission_required = 'main.can_view_reservation'
    raise_exception = True
    extra_context = {'title': title}


class CustomerDetailView(PermissionRequiredMixin, generic.DetailView):
    """
    View for detail of customer
    Implements generic DetailView
    """
    model = Customer
    title = _("Customer Information")
    permission_required = 'main.can_view_customer'
    raise_exception = True
    extra_context = {'title': title}


class StaffDetailView(PermissionRequiredMixin, generic.DetailView):
    """
    View for detail of staff
    Implements generic DetailView
    """
    model = Staff
    title = _("Staff Information")
    permission_required = 'main.can_view_staff_detail'
    extra_context = {'title': title}


class ProfileView(generic.TemplateView):
    template_name = 'profile.html'
    title = "Profile"
    extra_context = {'title': title}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            staff=Staff.objects.get()
            context['information'] = staff
            context['user_information'] = self.request.user
        else:
            raise Http404("Your are not logged in.")
        return context


class GuestListView(PermissionRequiredMixin, generic.ListView):
    """
    View for list of guests present in hotel.
    """
    model = Customer
    paginate_by = 5
    allow_empty = True
    queryset = Customer.objects.all().filter(Q(reservation__checkin__isnull=False),
                                             Q(reservation__checkin__checkout__isnull=True))
    permission_required = 'main.can_view_customer'
    template_name = 'main/guest_list.html'
    title = 'Guest List View'
    context_object_name = 'guest_list'
    extra_context = {'title': title}
