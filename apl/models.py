from django.db import models

# Create your models here.
class Persona(models.Model):

    nombre = models.CharField(verbose_name='Nombre', max_length=150)
    edad = models.IntegerField(verbose_name='Edad')

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        db_table = 'Personas'