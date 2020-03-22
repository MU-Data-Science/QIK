from django import forms

RANK_OPTIONS = ['Parse Tree', 'Dependency Tree', 'None']

class TextSearchForm(forms.Form):
	query = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'btn btn-xl btn-outline-light', 'style': 'height:10px; background-color:#E8ECEF; width:100%'}))
	ranking_function = forms.ChoiceField(choices=[(x, x) for x in RANK_OPTIONS])

class ImageSearchForm(forms.Form):
	imageFile = forms.FileField(required=False, label='', widget=forms.FileInput(attrs={'class': 'filestyle', 'data-classButton': 'btn btn-primary'}))
	ranking_function = forms.ChoiceField(choices=[(x, x) for x in RANK_OPTIONS])

class IndexForm(forms.Form):
	image_files = forms.FileField(label='', widget=forms.FileInput(attrs={'class': 'filestyle', 'data-classButton': 'btn btn-primary', 'webkitdirectory': True, 'webkitfile': False}))

