from sqlalchemy import Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Edge(Base):
    __tablename__ = "edges"
    __table_args__ = (UniqueConstraint("source_id", "destination_id", name="uq_edge_source_destination"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), nullable=False)
    destination_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), nullable=False)
    latency: Mapped[float] = mapped_column(Float, nullable=False)

    source_node: Mapped["Node"] = relationship("Node", foreign_keys=[source_id], back_populates="outgoing_edges")
    destination_node: Mapped["Node"] = relationship("Node", foreign_keys=[destination_id], back_populates="incoming_edges")
