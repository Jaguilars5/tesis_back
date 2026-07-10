from apps.core.constants.permissions import students as perms

ACTION_PERMISSIONS = {
    "student": {
        "list": perms.VIEW_STUDENT,
        "get": perms.VIEW_STUDENT,
        "create": perms.CREATE_STUDENT,
        "update": perms.UPDATE_STUDENT,
        "partial_update": perms.UPDATE_STUDENT,
        "destroy": perms.DELETE_STUDENT,
        "by_section": perms.VIEW_STUDENT,
        "search": perms.VIEW_STUDENT,
        "representatives": perms.VIEW_REPRESENTATIVE_RELATIONSHIP,
        "assign_representative": perms.CREATE_REPRESENTATIVE_RELATIONSHIP,
    },
    "student_representative": {
        "list": perms.VIEW_REPRESENTATIVE_RELATIONSHIP,
        "get": perms.VIEW_REPRESENTATIVE_RELATIONSHIP,
        "create": perms.CREATE_REPRESENTATIVE_RELATIONSHIP,
        "update": perms.UPDATE_REPRESENTATIVE_RELATIONSHIP,
        "partial_update": perms.UPDATE_REPRESENTATIVE_RELATIONSHIP,
        "destroy": perms.DELETE_REPRESENTATIVE_RELATIONSHIP,
        "set_primary": perms.UPDATE_REPRESENTATIVE_RELATIONSHIP,
        "unlink": perms.DELETE_REPRESENTATIVE_RELATIONSHIP,
    },
    "enrollment": {
        "list": perms.VIEW_ENROLLMENT,
        "get": perms.VIEW_ENROLLMENT,
        "create": perms.CREATE_ENROLLMENT,
        "update": perms.UPDATE_ENROLLMENT,
        "partial_update": perms.UPDATE_ENROLLMENT,
        "destroy": perms.DELETE_ENROLLMENT,
        "soft_delete": perms.DELETE_ENROLLMENT,
        "withdraw": perms.WITHDRAW_STUDENT,
        "transfer": perms.TRANSFER_STUDENT,
        "by_section": perms.VIEW_ENROLLMENT,
        "by_student": perms.VIEW_ENROLLMENT,
        "by_representative": perms.VIEW_ENROLLMENT,
    },
    "kinship": {
        "list": perms.VIEW_KINSHIP,
        "get": perms.VIEW_KINSHIP,
    },
}
