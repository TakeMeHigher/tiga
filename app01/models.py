from django.db import models

# Create your models here.

# Create your models here.


class Userinfo(models.Model):
    name=models.CharField(max_length=32,verbose_name='用户名')
    addr=models.CharField(max_length=64,verbose_name='地址')
    pwd=models.CharField(max_length=32,verbose_name='密码')
    email=models.EmailField(max_length=32,verbose_name='邮箱')
    ut=models.ForeignKey(to='UserType',null=True,blank=True,verbose_name='用户类型')
    def __str__(self):
        return  self.name


class Role(models.Model):
    caption=models.CharField(max_length=32,verbose_name='角色名')

    def __str__(self):
        return  self.caption

class UserType(models.Model):
    name=models.CharField(max_length=32,verbose_name='类型名称')
    roles=models.ManyToManyField(to='Role',verbose_name='角色表',null=True,blank=True)
    def __str__(self):
        return  self.name



class Host(models.Model):
    hostname=models.CharField(max_length=32,verbose_name='主机名')
    ip=models.GenericIPAddressField(protocol='both',verbose_name='IP')
    port=models.IntegerField(verbose_name='端口')