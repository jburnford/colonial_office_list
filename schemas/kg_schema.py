"""
Pydantic models for Colonial Office List Knowledge Graph schema validation.

These models enforce strict schema compliance and enable automated validation
of extracted JSON files.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums for strict type validation
# ============================================================================

class PlaceType(str, Enum):
    """Types of geographic entities"""
    COLONY = "colony"
    TERRITORY = "territory"
    DEPENDENCY = "dependency"
    CITY = "city"
    TOWN = "town"
    SETTLEMENT = "settlement"
    REGION = "region"
    DISTRICT = "district"
    PARISH = "parish"
    RIVER = "river"
    MOUNTAIN = "mountain"
    HARBOR = "harbor"
    BAY = "bay"
    ISLAND = "island"
    FEATURE = "feature"


class InstitutionType(str, Enum):
    """Types of institutions"""
    EXECUTIVE_COUNCIL = "executive_council"
    LEGISLATIVE_COUNCIL = "legislative_council"
    PRIVY_COUNCIL = "privy_council"
    COURT = "court"
    DEPARTMENT = "department"
    MILITARY_UNIT = "military_unit"
    POLICE_FORCE = "police_force"
    EDUCATIONAL = "educational"
    MEDICAL = "medical"
    RELIGIOUS = "religious"
    BANK = "bank"
    POSTAL = "postal"
    PUBLIC_WORKS = "public_works"


class PositionStatus(str, Enum):
    """Status of a position"""
    PERMANENT = "permanent"
    ACTING = "acting"
    TEMPORARY = "temporary"
    VACANT = "vacant"


class EconomicDataType(str, Enum):
    """Types of economic data"""
    REVENUE = "revenue"
    EXPENDITURE = "expenditure"
    TRADE_EXPORT = "trade_export"
    TRADE_IMPORT = "trade_import"
    SHIPPING = "shipping"
    CURRENCY = "currency"
    BANKING = "banking"
    PRODUCTION = "production"
    LAND_USE = "land_use"


class InfrastructureType(str, Enum):
    """Types of infrastructure"""
    RAILWAY = "railway"
    TELEGRAPH = "telegraph"
    POSTAL_ROUTE = "postal_route"
    DOCK = "dock"
    HARBOR = "harbor"
    ROAD = "road"
    BRIDGE = "bridge"
    PUBLIC_BUILDING = "public_building"
    WATER_WORKS = "water_works"


class EventType(str, Enum):
    """Types of historical events"""
    TREATY = "treaty"
    CESSION = "cession"
    ESTABLISHMENT = "establishment"
    REBELLION = "rebellion"
    CONSTITUTIONAL_CHANGE = "constitutional_change"
    APPOINTMENT = "appointment"
    TRANSFER = "transfer"
    DISASTER = "disaster"
    OTHER = "other"


class RelationshipType(str, Enum):
    """Types of relationships between entities"""
    # Geographic
    PART_OF = "PART_OF"
    DEPENDENCY_OF = "DEPENDENCY_OF"
    DISTANCE_FROM = "DISTANCE_FROM"
    BORDERS = "BORDERS"
    LOCATED_IN = "LOCATED_IN"
    # Administrative
    GOVERNED_BY = "GOVERNED_BY"
    MEMBER_OF = "MEMBER_OF"
    REPORTS_TO = "REPORTS_TO"
    ADMINISTERS = "ADMINISTERS"
    # Economic
    TRADES_WITH = "TRADES_WITH"
    EXPORTS = "EXPORTS"
    IMPORTS = "IMPORTS"
    CONNECTS = "CONNECTS"
    # Temporal
    PRECEDED_BY = "PRECEDED_BY"
    SUCCEEDED_BY = "SUCCEEDED_BY"
    DURING_YEAR = "DURING_YEAR"


# ============================================================================
# Nested Models
# ============================================================================

class Coordinates(BaseModel):
    """Geographic coordinates as written in source"""
    latitude: str = Field(..., description="Latitude as written in source")
    longitude: str = Field(..., description="Longitude as written in source")


class Area(BaseModel):
    """Area measurement"""
    value: float = Field(..., gt=0, description="Area value (must be positive)")
    unit: str = Field(..., description="Unit of measurement (e.g., square miles, acres)")


class Salary(BaseModel):
    """Salary information"""
    amount: float = Field(..., description="Salary amount")
    currency: str = Field(..., description="Currency symbol or code")
    period: str = Field(default="annual", description="Payment period")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate salary amount is reasonable"""
        if v < 0:
            raise ValueError("Salary amount cannot be negative")
        if v > 1000000:  # Sanity check for historical salaries
            raise ValueError(f"Salary amount {v} seems unreasonably high for historical data")
        return v


class Allowance(BaseModel):
    """Allowance information"""
    type: str = Field(..., description="Type of allowance (quarters, table money, horse, etc.)")
    amount: Optional[float] = Field(None, description="Allowance amount if monetary")
    currency: Optional[str] = Field(None, description="Currency symbol or code")
    description: Optional[str] = Field(None, description="Textual description")


class Position(BaseModel):
    """A position held by a person"""
    title: str = Field(..., min_length=1, description="Position title")
    department: Optional[str] = Field(None, description="Department name")
    location: Optional[str] = Field(None, description="Colony or city of posting")
    salary: Optional[Salary] = Field(None, description="Salary information")
    allowances: Optional[List[Allowance]] = Field(default_factory=list, description="List of allowances")
    status: PositionStatus = Field(default=PositionStatus.PERMANENT, description="Position status")
    year: str = Field(..., pattern=r"^\d{4}$", description="Year (YYYY format)")


class Composition(BaseModel):
    """Composition of an institution"""
    description: Optional[str] = Field(None, description="Textual description")
    member_count: Optional[int] = Field(None, ge=0, description="Number of members")
    members: List[str] = Field(default_factory=list, description="Person IDs of members")


class EconomicDataPoint(BaseModel):
    """Economic data point details"""
    category: Optional[str] = Field(None, description="Specific category")
    value: Optional[float] = Field(None, description="Numerical value")
    currency: Optional[str] = Field(None, description="Currency symbol or code")
    unit: Optional[str] = Field(None, description="Unit of measurement if applicable")
    source: Optional[str] = Field(None, description="Source of data")


class TimeSeriesPoint(BaseModel):
    """A point in a time series"""
    year: str = Field(..., pattern=r"^\d{4}$", description="Year (YYYY format)")
    value: float = Field(..., description="Value for this year")


class Route(BaseModel):
    """Route information for infrastructure"""
    from_location: Optional[str] = Field(None, alias="from", description="Starting location")
    to_location: Optional[str] = Field(None, alias="to", description="Ending location")
    via: List[str] = Field(default_factory=list, description="Intermediate locations")


class Length(BaseModel):
    """Length measurement"""
    value: float = Field(..., gt=0, description="Length value")
    unit: str = Field(..., description="Unit (miles, km, etc.)")


class Cost(BaseModel):
    """Cost information"""
    value: float = Field(..., ge=0, description="Cost amount")
    currency: str = Field(..., description="Currency symbol or code")


class Revenue(BaseModel):
    """Revenue information"""
    value: float = Field(..., ge=0, description="Revenue amount")
    currency: str = Field(..., description="Currency symbol or code")
    year: Optional[str] = Field(None, pattern=r"^\d{4}$", description="Year of revenue")


class InfrastructureSpecifications(BaseModel):
    """Infrastructure specifications"""
    length: Optional[Length] = Field(None, description="Length/distance")
    stations: Optional[int] = Field(None, ge=0, description="Number of stations")
    capacity: Optional[str] = Field(None, description="Capacity description")
    construction_cost: Optional[Cost] = Field(None, description="Construction cost")
    annual_revenue: Optional[Revenue] = Field(None, description="Annual revenue")
    annual_expenses: Optional[Revenue] = Field(None, description="Annual expenses")


class DemographicBreakdown(BaseModel):
    """Demographic breakdown category"""
    category: str = Field(..., description="Category as written in source")
    count: float = Field(..., ge=0, description="Population count")
    subcategories: Dict[str, Any] = Field(default_factory=dict, description="Nested subcategories")


# ============================================================================
# Entity Models
# ============================================================================

class Place(BaseModel):
    """Geographic entity"""
    id: str = Field(..., min_length=1, description="Unique identifier")
    name: str = Field(..., min_length=1, description="Historical name (exact spelling from source)")
    modern_name: Optional[str] = Field(None, description="Modern equivalent if identifiable")
    type: PlaceType = Field(..., description="Type of place")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates")
    area: Optional[Area] = Field(None, description="Area measurement")
    description: Optional[str] = Field(None, description="Textual description from source")
    parent_location: Optional[str] = Field(None, description="ID of containing location")
    year: str = Field(..., pattern=r"^\d{4}$", description="Year (YYYY format)")


class Person(BaseModel):
    """Person entity"""
    id: str = Field(..., min_length=1, description="Unique identifier")
    name: str = Field(..., min_length=1, description="Full name as written in source")
    titles: List[str] = Field(default_factory=list, description="Titles (Sir, Rev., Dr., etc.)")
    honors: List[str] = Field(default_factory=list, description="Honors (K.C.M.G., C.B., etc.)")
    positions: List[Position] = Field(default_factory=list, description="Positions held")

    @model_validator(mode='after')
    def validate_positions(self):
        """Ensure at least one position exists for most persons"""
        # Note: Some persons might be mentioned without positions (e.g., in events)
        # so we don't enforce this strictly
        return self


class Institution(BaseModel):
    """Institutional entity"""
    id: str = Field(..., min_length=1, description="Unique identifier")
    name: str = Field(..., min_length=1, description="Official name")
    type: InstitutionType = Field(..., description="Type of institution")
    location: str = Field(..., description="Colony or city")
    composition: Optional[Composition] = Field(None, description="Membership composition")
    function: Optional[str] = Field(None, description="Description of role/function")
    established: Optional[str] = Field(None, description="Establishment date")
    year: str = Field(..., pattern=r"^\d{4}$", description="Year (YYYY format)")


class EconomicData(BaseModel):
    """Economic data entity"""
    id: str = Field(..., min_length=1, description="Unique identifier")
    type: EconomicDataType = Field(..., description="Type of economic data")
    location: str = Field(..., description="Colony or location")
    year: str = Field(..., pattern=r"^\d{4}$", description="Year (YYYY format)")
    data: Optional[EconomicDataPoint] = Field(None, description="Data details")
    time_series: List[TimeSeriesPoint] = Field(default_factory=list, description="Time series data")
    notes: Optional[str] = Field(None, description="Contextual information")


class Infrastructure(BaseModel):
    """Infrastructure entity"""
    id: str = Field(..., min_length=1, description="Unique identifier")
    type: InfrastructureType = Field(..., description="Type of infrastructure")
    name: Optional[str] = Field(None, description="Name or description")
    location: str = Field(..., description="Colony or city")
    route: Optional[Route] = Field(None, description="Route information")
    specifications: Optional[InfrastructureSpecifications] = Field(None, description="Technical specifications")
    connections: List[str] = Field(default_factory=list, description="Connected location IDs")
    year: str = Field(..., pattern=r"^\d{4}$", description="Year (YYYY format)")


class Demographic(BaseModel):
    """Demographic data entity"""
    id: str = Field(..., min_length=1, description="Unique identifier")
    location: str = Field(..., description="Colony or city")
    year: str = Field(..., pattern=r"^\d{4}$", description="Year (YYYY format)")
    census_date: Optional[str] = Field(None, description="Census date if available")
    total_population: Optional[float] = Field(None, ge=0, description="Total population count")
    breakdowns: List[DemographicBreakdown] = Field(default_factory=list, description="Population breakdowns")


class Event(BaseModel):
    """Historical event"""
    id: str = Field(..., min_length=1, description="Unique identifier")
    date: Optional[str] = Field(None, description="Date as written in source")
    type: Optional[EventType] = Field(None, description="Type of event")
    description: str = Field(..., min_length=1, description="Event description")
    locations: List[str] = Field(default_factory=list, description="Location IDs involved")
    people: List[str] = Field(default_factory=list, description="Person IDs involved")
    year_mentioned: str = Field(..., pattern=r"^\d{4}$", description="Year this event was mentioned")


# ============================================================================
# Relationship Model
# ============================================================================

class Relationship(BaseModel):
    """Relationship between entities"""
    source_id: str = Field(..., min_length=1, description="Source entity ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    target_id: str = Field(..., min_length=1, description="Target entity ID")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")


# ============================================================================
# Container Models
# ============================================================================

class Entities(BaseModel):
    """Container for all entities"""
    places: List[Place] = Field(default_factory=list)
    people: List[Person] = Field(default_factory=list)
    institutions: List[Institution] = Field(default_factory=list)
    economic_data: List[EconomicData] = Field(default_factory=list)
    infrastructure: List[Infrastructure] = Field(default_factory=list)
    demographics: List[Demographic] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)


class Metadata(BaseModel):
    """Metadata for the extraction"""
    year: str = Field(..., pattern=r"^\d{4}$", description="Year of colonial office list")
    source_directory: str = Field(..., description="Path to source data directory")
    extraction_date: str = Field(..., description="ISO-8601 timestamp of extraction")
    processing_notes: Optional[str] = Field(None, description="Notes about extraction process")
    colonies_processed: Optional[List[str]] = Field(default_factory=list, description="List of colonies processed")

    @field_validator('extraction_date')
    @classmethod
    def validate_date(cls, v):
        """Validate ISO-8601 format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"extraction_date must be valid ISO-8601 format, got: {v}")
        return v


# ============================================================================
# Root Model
# ============================================================================

class KnowledgeGraphExtract(BaseModel):
    """Root model for a complete knowledge graph extract"""
    metadata: Metadata
    entities: Entities
    relationships: List[Relationship] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_relationships(self):
        """Validate that all relationship IDs reference existing entities"""
        # Collect all entity IDs
        all_entity_ids = set()
        all_entity_ids.update(p.id for p in self.entities.places)
        all_entity_ids.update(p.id for p in self.entities.people)
        all_entity_ids.update(i.id for i in self.entities.institutions)
        all_entity_ids.update(e.id for e in self.entities.economic_data)
        all_entity_ids.update(i.id for i in self.entities.infrastructure)
        all_entity_ids.update(d.id for d in self.entities.demographics)
        all_entity_ids.update(e.id for e in self.entities.events)

        # Validate relationships
        errors = []
        for idx, rel in enumerate(self.relationships):
            if rel.source_id not in all_entity_ids:
                errors.append(f"Relationship {idx}: source_id '{rel.source_id}' not found in entities")
            if rel.target_id not in all_entity_ids:
                errors.append(f"Relationship {idx}: target_id '{rel.target_id}' not found in entities")

        if errors:
            raise ValueError(f"Relationship validation errors:\n" + "\n".join(errors))

        return self

    def get_entity_counts(self) -> Dict[str, int]:
        """Get count of each entity type"""
        return {
            "places": len(self.entities.places),
            "people": len(self.entities.people),
            "institutions": len(self.entities.institutions),
            "economic_data": len(self.entities.economic_data),
            "infrastructure": len(self.entities.infrastructure),
            "demographics": len(self.entities.demographics),
            "events": len(self.entities.events),
            "relationships": len(self.relationships)
        }
