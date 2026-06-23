# Módulo `institutions` — Estructura

## Árbol de archivos

```
institutions/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py
├── README.md
│
├── api/
│   ├── serializers.py          # 5 serializers (SchoolYear, Section, AcademicLevel, AcademicSublevel, AcademicGrade)
│   ├── views.py                # 5 ViewSets (SchoolYear, AcademicLevel, AcademicSublevel, AcademicGrade, Section)
│   └── urls.py                 # Router: school-year, academic-levels, academic-sublevel, academic-grades, section
│
├── models/
│   ├── __init__.py             # 5 modelos
│   ├── school_year.py          # SchoolYear (TimeStampedModel)
│   ├── academic_level.py       # AcademicLevel (TimeStampedModel)
│   ├── academic_sublevel.py    # AcademicSublevel (TimeStampedModel)
│   ├── academic_grade.py       # AcademicGrade (TimeStampedModel)
│   └── section.py              # Section (TimeStampedModel)
│
├── repositories/
│   ├── __init__.py             # 5 repositorios exportados
│   ├── institution_repo.py     # SchoolYearRepository, AcademicLevelRepository, AcademicSublevelRepository, AcademicGradeRepository
│   └── section_repository.py   # SectionRepository
│
├── services/
│   ├── __init__.py
│   └── institution_service.py  # InstitutionService (validación fechas, solapamiento, ciclo actual)
│
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_repositories.py
    ├── test_services.py
    ├── test_api.py
    ├── test_api_gaps.py
    └── test_api_permissions.py
```
