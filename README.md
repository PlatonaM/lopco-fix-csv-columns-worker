## lopco-fix-csv-columns-worker

Removes or adds columns, based on a reference header, to a CSV file. Alternatively, an error can be generated to cancel a job.

### Description

    {
        "name": "Fix CSV Columns",
        "image": "platonam/lopco-fix-csv-columns-worker:latest",
        "data_cache_path": "/data_cache",
        "description": "Remove unknown columns or add missing columns.",
        "configs": {
            "delimiter": null,
            "reference_header": null,
            "abort_on_unknown": "0",
            "abort_on_missing": "0"
        },
        "input": {
            "type": "single",
            "fields": [
                {
                    "name": "source_csv",
                    "media_type": "text/csv",
                    "is_file": true
                }
            ]
        },
        "output": {
            "type": "single",
            "fields": [
                {
                    "name": "output_file",
                    "media_type": "text/csv",
                    "is_file": true
                }
            ]
        }
    }