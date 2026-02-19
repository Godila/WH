"""Add products, stocks, and defect_stocks tables.

Revision ID: 002
Revises: 001
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('barcode', sa.String(100), unique=True, nullable=False),
        sa.Column('gtin', sa.String(14), unique=True, nullable=False),
        sa.Column('seller_sku', sa.String(100), nullable=True),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('brand', sa.String(255), nullable=True),
        sa.Column('color', sa.String(100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_products_barcode', 'products', ['barcode'])
    op.create_index('ix_products_gtin', 'products', ['gtin'])
    op.create_index('ix_products_is_deleted', 'products', ['is_deleted'])

    # Create stocks table (one-to-one with products)
    op.create_table(
        'stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('quantity', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create defect_stocks table (one-to-one with products)
    op.create_table(
        'defect_stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('quantity', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('defect_stocks')
    op.drop_table('stocks')
    op.drop_index('ix_products_is_deleted', table_name='products')
    op.drop_index('ix_products_gtin', table_name='products')
    op.drop_index('ix_products_barcode', table_name='products')
    op.drop_table('products')
