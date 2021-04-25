import pickle
import os

from django.views.generic import FormView
from django.conf import settings

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

from .forms import TextForm


global_model: LinearSVC = pickle.load(open(os.path.join(settings.MODELS_DIR, 'model_global.pickle'), 'rb'))
global_vectorizer: TfidfVectorizer = pickle.load(open(os.path.join(settings.MODELS_DIR, 'vectorizer_global.pickle'), 'rb'))

news_model: LinearSVC = pickle.load(open(os.path.join(settings.MODELS_DIR, 'model_news.pickle'), 'rb'))
news_vectorizer: TfidfVectorizer = pickle.load(open(os.path.join(settings.MODELS_DIR, 'vectorizer_news.pickle'), 'rb'))

poetry_model: LinearSVC = pickle.load(open(os.path.join(settings.MODELS_DIR, 'model_poetry.pickle'), 'rb'))
poetry_vectorizer: TfidfVectorizer = pickle.load(open(os.path.join(settings.MODELS_DIR,
                                                                   'vectorizer_poetry.pickle'), 'rb'))


def get_subcategory_scores(text, category):
    subcategory_scores = None
    if category == 'новини':
        text_transformed = news_vectorizer.transform([text])
        subcategory_scores = list(zip(list(news_model.classes_),
                                      list(news_model.decision_function(text_transformed)[0])))[:5]
    elif category == 'поезія':
        text_transformed = poetry_vectorizer.transform([text])
        subcategory_scores = list(zip(list(poetry_model.classes_),
                                      list(poetry_model.decision_function(text_transformed)[0])))[:5]

    if not subcategory_scores:
        return
    scores = sorted([{
        'category': item[0],
        'score': round(item[1], 3),
    }
        for item in subcategory_scores], key=lambda item: item['score'], reverse=True)
    return scores


class ClassifyFormView(FormView):
    template_name = 'classify.html'
    form_class = TextForm
    success_url = '/'

    def form_valid(self, form):
        text = form.data['text']
        text_transformed = global_vectorizer.transform([text])
        category_scores = list(zip(list(global_model.classes_),
                                   list(global_model.decision_function(text_transformed)[0])))

        extra_context = dict()
        extra_context['text'] = text
        extra_context['scores'] = sorted([{
            'category': item[0],
            'score': round(item[1], 3),
            'subcategory_scores': None
        }
            for item in category_scores], key=lambda item: item['score'], reverse=True)
        extra_context['scores'][0]['subcategory_scores'] = get_subcategory_scores(text,
                                                                                  extra_context['scores'][0]['category'])

        return self.render_to_response(context=extra_context)
