from django import forms

RANK_OPTIONS = ['Parse Tree', 'Dependency Tree', 'None']
MODEL_OPTIONS = ['Captions Model', 'Objects Model', 'Hybrid Model']

class TextSearchForm(forms.Form):
	query = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'btn btn-xl btn-outline-light', 'style': 'height:10px; background-color:#E8ECEF; width:100%'}))
	ranking_function = forms.ChoiceField(choices=[(x, x) for x in RANK_OPTIONS])

class VideoSearchForm(forms.Form):
	videoFile = forms.FileField()
	ranking_function = forms.ChoiceField(choices=[(x, x) for x in RANK_OPTIONS])
	k_value = forms.IntegerField(initial=8)
	search_models = forms.ChoiceField(choices=[(x, x) for x in MODEL_OPTIONS])

class IndexForm(forms.Form):
	videoFile = forms.FileField()

class ExplainForm(forms.Form):
	query = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'btn btn-xl btn-outline-light', 'style': 'height:10px; background-color:#E8ECEF; width:100%'}))