"""add hierarchy and component system

Revision ID: e644fdb89f7b
Revises: 63f11f4c0937
Create Date: 2026-03-20 11:37:27.129128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e644fdb89f7b'
down_revision: Union[str, Sequence[str], None] = '63f11f4c0937'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "hierarchy_node" not in table_names:
        op.create_table(
            "hierarchy_node",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("parent_id", sa.Integer(), nullable=True),
            sa.Column(
                "type",
                sa.Enum("GUN", "MAJOR", "SUB", name="hierarchy_node_type"),
                nullable=False,
            ),
            sa.Column("name", sa.String(), nullable=False),
            sa.CheckConstraint("type IN ('GUN', 'MAJOR', 'SUB')", name="ck_hierarchy_node_type"),
            sa.ForeignKeyConstraint(["parent_id"], ["hierarchy_node.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_hierarchy_node_parent_id", "hierarchy_node", ["parent_id"], unique=False)

    if "component_v2" not in table_names:
        op.create_table(
            "component_v2",
            sa.Column("part_number", sa.String(), nullable=False),
            sa.Column("gun_id", sa.Integer(), nullable=False),
            sa.Column("major_assembly_id", sa.Integer(), nullable=True),
            sa.Column("sub_assembly_id", sa.Integer(), nullable=True),
            sa.Column("nomenclature", sa.String(), nullable=False),
            sa.Column("ved_status", sa.String(), nullable=True),
            sa.Column("change_category", sa.String(), nullable=True),
            sa.Column("item_type", sa.String(), nullable=True),
            sa.Column("source_type", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.CheckConstraint("ved_status IN ('V', 'E', 'D')", name="ck_component_v2_ved_status"),
            sa.CheckConstraint("change_category IN ('MC', 'CC')", name="ck_component_v2_change_category"),
            sa.CheckConstraint(
                "item_type IN ('Expendable', 'Non-Expendable')",
                name="ck_component_v2_item_type",
            ),
            sa.CheckConstraint(
                "source_type IN ('OSS', 'LP', 'IR&D', 'LRC', 'LM', 'Cannibalization', 'Reclamation', 'ERC')",
                name="ck_component_v2_source_type",
            ),
            sa.ForeignKeyConstraint(["gun_id"], ["hierarchy_node.id"]),
            sa.ForeignKeyConstraint(["major_assembly_id"], ["hierarchy_node.id"]),
            sa.ForeignKeyConstraint(["sub_assembly_id"], ["hierarchy_node.id"]),
            sa.PrimaryKeyConstraint("part_number"),
        )

    if "component_usage" not in table_names:
        op.create_table(
            "component_usage",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("node_id", sa.Integer(), nullable=False),
            sa.Column("part_number", sa.String(), nullable=False),
            sa.Column("number_of", sa.Integer(), nullable=False),
            sa.Column("scale_percent", sa.Float(), nullable=False),
            sa.CheckConstraint("number_of > 0", name="ck_component_usage_number_of_positive"),
            sa.CheckConstraint("scale_percent >= 0", name="ck_component_usage_scale_percent_non_negative"),
            sa.ForeignKeyConstraint(["node_id"], ["hierarchy_node.id"]),
            sa.ForeignKeyConstraint(["part_number"], ["component_v2.part_number"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("node_id", "part_number", name="uq_component_usage_node_part"),
        )
        op.create_index("ix_component_usage_node_id", "component_usage", ["node_id"], unique=False)
        op.create_index("ix_component_usage_part_number", "component_usage", ["part_number"], unique=False)

    if "inventory_stock" not in table_names:
        op.create_table(
            "inventory_stock",
            sa.Column("stock_id", sa.Integer(), nullable=False),
            sa.Column("part_number", sa.String(), nullable=False),
            sa.Column("current_stock", sa.Integer(), nullable=False),
            sa.Column("low_stock_threshold", sa.Integer(), nullable=True),
            sa.Column("last_updated", sa.DateTime(), nullable=False),
            sa.CheckConstraint("current_stock >= 0", name="ck_inventory_stock_current_stock_non_negative"),
            sa.ForeignKeyConstraint(["part_number"], ["component_v2.part_number"]),
            sa.PrimaryKeyConstraint("stock_id"),
            sa.UniqueConstraint("part_number"),
        )
        op.create_index("ix_inventory_stock_part_number", "inventory_stock", ["part_number"], unique=False)

    if "stock_transaction" not in table_names:
        op.create_table(
            "stock_transaction",
            sa.Column("transaction_id", sa.Integer(), nullable=False),
            sa.Column("part_number", sa.String(), nullable=False),
            sa.Column("transaction_type", sa.String(), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("transaction_date", sa.DateTime(), nullable=False),
            sa.Column("performed_by", sa.String(), nullable=True),
            sa.Column("remarks", sa.Text(), nullable=True),
            sa.CheckConstraint(
                "transaction_type IN ('Receipt', 'Issue', 'Adjustment')",
                name="ck_stock_transaction_type",
            ),
            sa.CheckConstraint("quantity > 0", name="ck_stock_transaction_quantity_positive"),
            sa.ForeignKeyConstraint(["part_number"], ["component_v2.part_number"]),
            sa.PrimaryKeyConstraint("transaction_id"),
        )
        op.create_index("ix_stock_transaction_part_number", "stock_transaction", ["part_number"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "stock_transaction" in table_names:
        op.drop_index("ix_stock_transaction_part_number", table_name="stock_transaction")
        op.drop_table("stock_transaction")
    if "inventory_stock" in table_names:
        op.drop_index("ix_inventory_stock_part_number", table_name="inventory_stock")
        op.drop_table("inventory_stock")
    if "component_usage" in table_names:
        op.drop_index("ix_component_usage_part_number", table_name="component_usage")
        op.drop_index("ix_component_usage_node_id", table_name="component_usage")
        op.drop_table("component_usage")
    if "component_v2" in table_names:
        op.drop_table("component_v2")
    if "hierarchy_node" in table_names:
        op.drop_index("ix_hierarchy_node_parent_id", table_name="hierarchy_node")
        op.drop_table("hierarchy_node")
