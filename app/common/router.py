from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_home():
    from worker.tasks.email import send_email

    send_email.delay()
    return {"message": "Home Page..."}
