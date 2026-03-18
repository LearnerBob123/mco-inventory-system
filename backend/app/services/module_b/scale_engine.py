import math
from sqlalchemy.orm import Session
from app.services.module_b.scale_engine_model import ScaleSnapshot
from app.schemas.logic_calculation_schema import CalculationRequest, CalculationResponse

class ScaleEngine:
    CALCULATION_VERSION = "1.0"

    @classmethod
    def calculate_authorized_quantity(cls, target_guns: int, number_of: int, scale_percent: float) -> int:
        raw_quantity = target_guns * number_of * (scale_percent / 100.0)
        return math.ceil(raw_quantity)

    @classmethod
    def calculate_shortfall(cls, authorized_quantity: int, available_quantity: int) -> int:
        return max(0, authorized_quantity - available_quantity)

    @classmethod
    def process_calculation(cls, db: Session, request: CalculationRequest) -> CalculationResponse:
        if request.request_id:
            existing_snapshot = db.query(ScaleSnapshot).filter(ScaleSnapshot.request_id == request.request_id).first()
            if existing_snapshot:
                shortfall = cls.calculate_shortfall(existing_snapshot.authorized_quantity, request.available_quantity)
                return CalculationResponse(
                    authorized_quantity=existing_snapshot.authorized_quantity,
                    shortfall=shortfall,
                    calculation_ts=existing_snapshot.calculation_ts,
                    calculation_version=existing_snapshot.calculation_version,
                    snapshot_id=existing_snapshot.id,
                    request_id=existing_snapshot.request_id
                )

        authorized_quantity = cls.calculate_authorized_quantity(
            target_guns=request.target_guns,
            number_of=request.number_of,
            scale_percent=request.scale_percent
        )
        shortfall = cls.calculate_shortfall(authorized_quantity, request.available_quantity)

        snapshot = ScaleSnapshot(
            gun_model_id=request.gun_model_id,
            item_id=request.item_id,
            target_guns=request.target_guns,
            number_of=request.number_of,
            scale_percent=request.scale_percent,
            authorized_quantity=authorized_quantity,
            calculation_version=cls.CALCULATION_VERSION,
            created_by=request.created_by,
            reason=request.reason,
            request_id=request.request_id
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        return CalculationResponse(
            authorized_quantity=authorized_quantity,
            shortfall=shortfall,
            calculation_ts=snapshot.calculation_ts,
            calculation_version=snapshot.calculation_version,
            snapshot_id=snapshot.id,
            request_id=snapshot.request_id
        )
        