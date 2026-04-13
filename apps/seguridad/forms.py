from django import forms
from django.core.validators import RegexValidator
from .models import Usuario, Perfil, Modulo


class LoginForm(forms.Form):
    """Formulario de login"""
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )


class UsuarioForm(forms.ModelForm):
    """Formulario para Usuario"""
    celular_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='El celular debe tener exactamente 10 dígitos numéricos'
    )
    
    celular = forms.CharField(
        max_length=10,
        required=False,
        validators=[celular_validator],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': '3001234567',
            'maxlength': '10'
        })
    )
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': '••••••••'
        })
    )
    
    confirmar_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': '••••••••'
        })
    )
    
    # Campo para decidir si enviar email de verificación
    enviar_verificacion = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-5 h-5 text-blue-600 rounded focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600'
        })
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'celular', 'perfil', 'activo', 'avatar']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Nombre completo'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'correo@ejemplo.com'
            }),
            'perfil': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 rounded focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'accept': 'image/*'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')
        
        # Si es nuevo usuario, password es obligatorio
        if not self.instance.pk and not password:
            raise forms.ValidationError('La contraseña es obligatoria para nuevos usuarios')
        
        # Verificar que las contraseñas coincidan
        if password and password != confirmar_password:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get('password')
    
    # Establecer contraseña si se proporcionó
        if password:
            usuario.set_password(password)
    
    # Si es nuevo usuario
        es_nuevo = not self.instance.pk
    
        if es_nuevo:
        # Marcar email como no verificado
            usuario.email_verificado = False
    
        if commit:
            usuario.save()
    
        return usuario


class PerfilForm(forms.ModelForm):
    """Formulario para Perfil"""
    
    class Meta:
        model = Perfil
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Nombre del perfil'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': 3,
                'placeholder': 'Descripción del perfil'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 rounded focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600'
            }),
        }


class ModuloForm(forms.ModelForm):
    """Formulario para Módulo"""
    
    class Meta:
        model = Modulo
        fields = ['nombre', 'descripcion', 'icono', 'url', 'orden', 'padre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Nombre del módulo'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': 3,
                'placeholder': 'Descripción del módulo'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Nombre del icono (ej: folder, users, settings)'
            }),
            'url': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': '/ruta/del/modulo/'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'min': 0
            }),
            'padre': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 rounded focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar módulos padres como opciones
        self.fields['padre'].queryset = Modulo.objects.filter(padre__isnull=True, activo=True)
        self.fields['padre'].required = False


class MiPerfilForm(forms.ModelForm):
    """Formulario para editar el perfil propio"""
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'celular', 'avatar']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            }),
            'celular': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': '3001234567',
                'maxlength': '10'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'accept': 'image/*'
            }),
        }