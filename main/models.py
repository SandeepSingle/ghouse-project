from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField

# Create your models here.
class Customer(models.Model):
    customer_id=models.AutoField(primary_key=True)
    first_name=models.CharField( max_length=50)
    middle_name=models.CharField( max_length=50,blank=True)
    last_name=models.CharField( max_length=50)
    contact_no=models.CharField(max_length=10)
    email=models.EmailField( max_length=50)
    address=models.CharField( max_length=100)
    country=CountryField()
    GenderChoices=(
        ('M','Male'),
        ('F','Female'),
        ('T','Transgender')
    )
    gender=models.CharField(max_length=1,choices=GenderChoices)
    identity_no=models.CharField(max_length=50)
    id_proof=models.ImageField()

    class Meta:
      ordering = ['first_name', 'middle_name', 'last_name']
    
    def get_absolute_url(self):
        return reverse("customer", args=str([self.customer_id]))
    
    def __str__(self):
        return '{0}{1}{2}'.format(self.customer_id,self.first_name,self.last_name)
    



class Staff(models.Model):
    profile_picture = models.ImageField(upload_to='staff_img/', default='images/staff.png')
    staff_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=False, blank=True)
    last_name = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    email_address = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, editable=False)

    class Meta:
        ordering = ['first_name', 'middle_name', 'last_name']
        permissions = (('can_view_customer', 'Can view customer'),)
       
    def get_absolute_url(self):
        return reverse('Staff-detail', args=str([self.staff_id]))

    def __str__(self):  
        return '({0}) {1} {2}'.format(self.staff_id, self.first_name, self.last_name)



    
    
    
class RoomType(models.Model):
    room_type_id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    price = models.PositiveSmallIntegerField()
    facility = models.ManyToManyField('Facility')
    Max_no_of_guest=models.PositiveSmallIntegerField(default=True)
    No_of_Rooms=models.PositiveSmallIntegerField(default=True)


    def display_facility(self):
        return ', '.join([facility.name for facility in self.facility.all()])

    display_facility.short_description = 'Facilities'

    def __str__(self):
        return "%i - %s - Rs. %i" % (self.No_of_Rooms, self.name, self.price)

    def get_absolute_url(self):
        return reverse('room_type-detail', args=[self.room_type_id])

class Facility(models.Model):
    name = models.CharField(max_length=25)
    price = models.PositiveSmallIntegerField()
    
    class Meta:
        verbose_name_plural = 'Facilities'  
    def __str__(self):
        return self.name


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    no_of_children = models.PositiveSmallIntegerField(default=0)
    no_of_adults = models.PositiveSmallIntegerField(default=1)
    no_of_rooms = models.PositiveSmallIntegerField(default=1)
    reservation_date_time = models.DateTimeField(default=timezone.now)
    expected_arrival_date_time = models.DateTimeField(default=timezone.now)
    expected_departure_date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = (('can_view_reservation', 'Can view reservation'),
                       ('can_view_reservation_detail', 'Can view reservation detail'),)

    def get_absolute_url(self):
        return reverse('reservation-detail', args=str([self.reservation_id]))

    def __str__(self):
        return '({0}) {1} {2}'.format(self.reservation_id, self.customer.first_name, self.customer.last_name)




class Room(models.Model):
    room_no = models.CharField(max_length=10, primary_key=True)
    room_type = models.ForeignKey('RoomType', null=False, blank=True, on_delete=models.CASCADE)
    availability = models.BooleanField(default=0)
    reservation = models.ForeignKey(Reservation, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['room_no', ]
        permissions = (('can_view_room', 'Can view room'),)

    def __str__(self):
        return "%s - %s - Rs. %i" % (self.room_no, self.room_type.name, self.room_type.price)

    
    def get_absolute_url(self):
        return reverse('room-detail', args=[self.room_no])

    def save(self, *args, **kwargs):  # Overriding default behaviour of save
        if self.reservation:  # If it is reserved, than it should not be available
            self.availability = 0
        else:
            self.availability = 1

        super().save(*args, **kwargs)