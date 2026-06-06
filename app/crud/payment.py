from sqlalchemy.orm import Session
from app.models.payment import Payment


def create_payment(
    db: Session,
    user_id: int,
    course_id: int,
    amount: int,
    currency: str = "USD",
    payment_method: str | None = None,
    transaction_reference: str | None = None,
    status: str = "pending",
    notes: str | None = None,
) -> Payment:
    payment = Payment(
        user_id=user_id,
        course_id=course_id,
        amount=amount,
        currency=currency,
        payment_method=payment_method,
        transaction_reference=transaction_reference,
        status=status,
        notes=notes,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment(db: Session, payment_id: int) -> Payment | None:
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_completed_payment_for_course(db: Session, user_id: int, course_id: int) -> Payment | None:
    return (
        db.query(Payment)
        .filter(
            Payment.user_id == user_id,
            Payment.course_id == course_id,
            Payment.status == "completed",
        )
        .order_by(Payment.created_at.desc())
        .first()
    )


def list_payments_for_user(db: Session, user_id: int) -> list[Payment]:
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .all()
    )


def complete_payment(db: Session, payment: Payment, transaction_reference: str | None = None) -> Payment:
    payment.status = "completed"
    if transaction_reference:
        payment.transaction_reference = transaction_reference
    db.commit()
    db.refresh(payment)
    return payment
