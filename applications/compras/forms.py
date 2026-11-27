from django.forms.fields import ChoiceField
from django.forms.models import ModelForm
from django.forms.widgets import NumberInput, TextInput, Select

from applications.epayco.models import Ventas


class VentaForm(ModelForm):
    class Meta:
        ESTADOS = [
            # Estados propios
            ('creada',     'Creada'),       
            ('en_proceso', 'En proceso'),   
            ('expirado',   'Expirado'),     
            ('cancelado_por_usuario', 'Cancelado por el usuario'),
            ('desconocido', 'Desconocido')
        ]
        model = Ventas
        fields = [
            "usuario",
            "metodo_pago",
            "referencia_pago",
            "link_cobro",
            "numero_guia",
            "subtotal",
            "total",
            "descuento",
            "estado_venta",
            
        ]
        estado_venta = ChoiceField(
            choices=ESTADOS,
            label="Estado de Venta",
            widget=Select(attrs={
                'class': "bj-form-select",
                'required': True
            })
        )
        widgets = {
            "usuario": Select(
                attrs={
                    'class': "bj-form-select",
                    'required': True
                }
            ),
            "metodo_pago": TextInput(
                attrs={
                    'class': "bj-form-control",
                    'required': False
                }
            ),
            "referencia_pago": TextInput(
                attrs={
                    'class': "bj-form-control",
                    'required': False
                }
            ),
            "link_cobro": TextInput(
                attrs={
                    'class': "bj-form-control",
                    'required': False
                }
            ),
            "subtotal": NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                    'class': 'bj-form-control',
                    'placeholder': '0.00'
                }
            ),
            "total": NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                    'class': 'bj-form-control',
                    'placeholder': '0.00'
                }
            ),
            "descuento": NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                    'class': 'bj-form-control',
                    'placeholder': '0.00'
                }
            ),
            "numero_guia": TextInput(
                attrs={
                    'class': "bj-form-control",
                }
            ),
            "estado_venta": Select(
                attrs={
                    'class': "bj-form-select",
                    'required': True
                },
                choices=ESTADOS
            ),
        }

        labels = {
            "usuario": "Usuario",
            "metodo_pago": "Metodo de Pago",
            "referencia_pago": "Referencia de Pago",
            "link_cobro": "Link de Cobro",
            "subtotal": "Subtotal",
            "total": "Total",
            "descuento": "Descuento",
            "estado_venta": "Estado de Venta",
            "numero_guia": "Numero de Guía"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['link_cobro'].required = False
        self.fields['numero_guia'].required = False
        self.fields['referencia_pago'].required = False

    def clean_numero_guia(self):

        # Validacion para cambiar el None como string a un None puro
        numero_guia = self.cleaned_data.get('numero_guia')
        if self.instance and self.instance.pk:
            if numero_guia == "None":
                return None

        return numero_guia

        
