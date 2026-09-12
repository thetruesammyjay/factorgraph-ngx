"""SQLAlchemy models for the versioned, point-in-time research dataset."""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DatasetVersion(Base):
    """A reproducible source-data snapshot used by an experiment."""

    __tablename__ = "dataset_versions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    version: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(200))
    coverage_start: Mapped[date | None] = mapped_column(Date)
    coverage_end: Mapped[date | None] = mapped_column(Date)
    manifest: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    isin: Mapped[str | None] = mapped_column(String(12), unique=True, index=True)
    name: Mapped[str] = mapped_column(Text)
    sector: Mapped[str | None] = mapped_column(String(100), index=True)
    listing_date: Mapped[date | None] = mapped_column(Date)
    delisting_date: Mapped[date | None] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class SecurityIdentifier(Base):
    """Ticker/ISIN history needed for surviving and delisted securities."""

    __tablename__ = "security_identifiers"
    __table_args__ = (
        UniqueConstraint("company_id", "ticker", "valid_from", name="uq_security_identifier_period"),
        Index("ix_security_identifiers_ticker_period", "ticker", "valid_from", "valid_to"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    isin: Mapped[str | None] = mapped_column(String(12), index=True)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)


class PriceObservation(Base):
    """Daily security prices. Nulls represent unavailable observations."""

    __tablename__ = "price_observations"
    __table_args__ = (
        CheckConstraint("close > 0", name="ck_prices_close_positive"),
        CheckConstraint("volume IS NULL OR volume >= 0", name="ck_prices_volume_nonnegative"),
        CheckConstraint(
            "trading_value IS NULL OR trading_value >= 0",
            name="ck_prices_trading_value_nonnegative",
        ),
        Index("ix_price_observations_date_company", "trading_date", "company_id"),
    )

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True
    )
    trading_date: Mapped[date] = mapped_column(Date, primary_key=True)
    open: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    high: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    low: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    close: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    adjusted_close: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    volume: Mapped[Decimal | None] = mapped_column(Numeric(24, 6))
    trading_value: Mapped[Decimal | None] = mapped_column(Numeric(28, 6))
    number_of_transactions: Mapped[int | None] = mapped_column(Integer)
    dataset_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_versions.id"))


class FundamentalObservation(Base):
    """Financial information with an as-of date to prevent look-ahead bias."""

    __tablename__ = "fundamental_observations"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "fiscal_period",
            "publication_date",
            name="uq_fundamentals_company_period_publication",
        ),
        CheckConstraint(
            "shares_outstanding IS NULL OR shares_outstanding > 0",
            name="ck_fundamentals_shares_positive",
        ),
        Index("ix_fundamentals_company_effective_from", "company_id", "effective_from"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    fiscal_period: Mapped[date] = mapped_column(Date)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_from: Mapped[date] = mapped_column(Date, index=True)
    effective_date_source: Mapped[str] = mapped_column(String(50))
    book_equity: Mapped[Decimal | None] = mapped_column(Numeric(28, 6))
    shares_outstanding: Mapped[Decimal | None] = mapped_column(Numeric(28, 6))
    earnings_per_share: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    pe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    dividend_yield: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    revenue: Mapped[Decimal | None] = mapped_column(Numeric(28, 6))
    net_income: Mapped[Decimal | None] = mapped_column(Numeric(28, 6))
    total_assets: Mapped[Decimal | None] = mapped_column(Numeric(28, 6))
    total_liabilities: Mapped[Decimal | None] = mapped_column(Numeric(28, 6))
    source_document: Mapped[str | None] = mapped_column(Text)
    dataset_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_versions.id"))


class CorporateAction(Base):
    __tablename__ = "corporate_actions"
    __table_args__ = (
        CheckConstraint(
            "adjustment_factor IS NULL OR adjustment_factor > 0",
            name="ck_corporate_actions_factor_positive",
        ),
        Index("ix_corporate_actions_company_date", "company_id", "action_date"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    action_date: Mapped[date] = mapped_column(Date)
    action_type: Mapped[str] = mapped_column(String(50))
    adjustment_factor: Mapped[Decimal | None] = mapped_column(Numeric(20, 10))
    cash_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    dataset_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_versions.id"))


class BenchmarkObservation(Base):
    __tablename__ = "benchmark_observations"
    __table_args__ = (
        CheckConstraint("close > 0", name="ck_benchmark_close_positive"),
        Index("ix_benchmark_observations_date", "trading_date"),
    )

    benchmark_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    trading_date: Mapped[date] = mapped_column(Date, primary_key=True)
    close: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    adjusted_close: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    dataset_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_versions.id"))


class RiskFreeObservation(Base):
    __tablename__ = "risk_free_observations"
    __table_args__ = (Index("ix_risk_free_observations_date", "observation_date"),)

    observation_date: Mapped[date] = mapped_column(Date, primary_key=True)
    tenor: Mapped[str] = mapped_column(String(50), primary_key=True)
    annualized_rate: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False)
    dataset_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_versions.id"))


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    dataset_version: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

