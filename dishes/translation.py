from modeltranslation.translator import TranslationOptions, register

from categories.models import Category

from .models import Recipe


@register(Recipe)
class RecipeTranslationOptions(TranslationOptions):
    fields = ("title", "description", "ingredients", "instructions")


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name", "description")
