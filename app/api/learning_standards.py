from fastapi import APIRouter

router = APIRouter(prefix="/standards", tags=["learning-standards"])


@router.get("/capabilities")
def learning_standard_capabilities():
    return {
        "supported_standards": ["SCORM 1.2", "SCORM 2004", "xAPI (Tin Can API)"],
        "scorm_integration": {
            "enabled": False,
            "note": "SCORM launch and manifest parsing are supported via future integration hooks.",
        },
        "xapi_integration": {
            "enabled": False,
            "note": "xAPI statement endpoints can be added to capture learner activity.",
        },
    }
