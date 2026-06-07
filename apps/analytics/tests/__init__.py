from django.test import TestCase

# Compatibilidad Python 3.14: patch Context.__copy__
import django.template.context as _context


def _safe_base_copy(self):
    duplicate = object.__new__(type(self))
    duplicate.dicts = self.dicts[:]
    return duplicate


_context.BaseContext.__copy__ = _safe_base_copy

