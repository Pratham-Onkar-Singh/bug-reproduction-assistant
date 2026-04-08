TASKS = {
    "easy": {
        "id": "BUG-EASY-001",
        "description": "App crashes when uploading file larger than 50MB",
        "correct_steps": ["open_upload_page", "upload_file"],
        "parameter": {"file_size": "100MB"},
        "crash_step": "upload_file"
    },

    "medium": {
        "id": "BUG-MED-001",
        "description": "App crashes when uploading large CSV file",
        "correct_steps": ["login", "open_upload_page", "upload_file"],
        "parameter": {"file_type": "csv", "file_size": "100MB"},
        "crash_step": "upload_file"
    },

    "hard": {
        "id": "BUG-HARD-001",
        "description": "Crash occurs when uploading CSV after login with admin role",
        "correct_steps": ["login", "set_role_admin", "open_upload_page", "upload_file"],
        "parameter": {
            "file_type": "csv",
            "file_size": "100MB",
            "role": "admin"
        },
        "crash_step": "upload_file"
    }
}