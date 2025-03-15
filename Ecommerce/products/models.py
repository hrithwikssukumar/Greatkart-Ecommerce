from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account



class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug         = models.SlugField(max_length=200,unique=True)
    description  = models.TextField(max_length=200,unique=True)
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    image        = models.ImageField(upload_to="products/")
    stock        = models.IntegerField()
    category     = models.ForeignKey(Category,on_delete = models.CASCADE)
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def _str_(self):
        return self.product_name
    
    def save(self, *args, **kwargs):
        
        if self.stock > 0:
            self.is_available = True
        else:
            self.is_available = False
        super().save(*args, **kwargs)

    class Meta:
       db_table = 'product_table'



variation_category_choice =(

    ('color','color'),
    ('size','size'),
)

class Variation(models.Model):

    product            = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField( max_length=100,choices = variation_category_choice)
    variation_value    = models.CharField( max_length=100)
    is_active          = models.BooleanField(default =True)
    is_created_date    = models.DateTimeField(auto_now=True) 


    def __str__(self):
        return self.product



class Wishlist(models.Model):

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.product_name}"

    class Meta:
        unique_together = ('user', 'product')  
    


 

        

        
       
