from django.forms import TextInput, NumberInput, ModelForm
from apl.views.persona.views import Persona

class PersonaForm(ModelForm):

    class Meta():

        model = Persona
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre'
                }
            ),
            'edad': NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Edad'
                }
            )
        }