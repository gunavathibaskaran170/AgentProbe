from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import TestCase as TestCaseModel
from app.schemas import TestCaseCreate, TestCaseOut

router = APIRouter(tags=["tests"])


@router.get("/tests", response_model=list[TestCaseOut])
def list_tests(db: Session = Depends(get_db)) -> list[TestCaseModel]:
    return db.query(TestCaseModel).order_by(TestCaseModel.id).all()


@router.post(
    "/tests",
    response_model=TestCaseOut,
    status_code=status.HTTP_201_CREATED,
)
def create_test(
    payload: TestCaseCreate,
    db: Session = Depends(get_db),
) -> TestCaseModel:
    test_case = TestCaseModel(**payload.model_dump())
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case
