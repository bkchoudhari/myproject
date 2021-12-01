from django.db import models
from django.utils import timezone
# Create your models here.
class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	address=models.TextField()
	usertype=models.CharField(max_length=100,default="user")

	def __str__(self):
		return self.fname+" - "+self.usertype

class Cloth(models.Model):
	CHOICES=(
		('killer','killer'),
		('cambridge','cambridge'),
		('disel','disel'),
		
		)
	cloth_seller=models.ForeignKey(User,on_delete=models.CASCADE,default="2")
	cloth_brand=models.CharField(max_length=100,choices=CHOICES)
	cloth_price=models.IntegerField()
	cloth_image=models.ImageField(upload_to='images/')
	cloth_desc=models.TextField()

	def __str__(self):
		return self.cloth_brand

class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	message=models.TextField()

	def __str__(self):
		return self.name


class Wishlist(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	cloth=models.ForeignKey(Cloth,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.cloth.cloth_brand	


class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	cloth=models.ForeignKey(Cloth,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	price=models.IntegerField()
	qty=models.IntegerField(default=1)
	total_price=models.IntegerField()
	payment_status=models.CharField(max_length=100,default="pending")

	def __str__(self):
		return self.user.fname+" - "+self.cloth.cloth_brand				


class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
    							on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
