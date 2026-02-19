"""Add stock_movements table.

Revision ID: 003
Revises: 002
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stock_movements table
    op.create_table(
        'stock_movements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sources.id', ondelete='SET NULL'), nullable=True),
        sa.Column('distribution_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('distribution_centers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for filtering
    op.create_index('ix_stock_movements_product_id', 'stock_movements', ['product_id'])
    op.create_index('ix_stock_movements_operation_type', 'stock_movements', ['operation_type'])
    op.create_index('ix_stock_movements_created_at', 'stock_movements', ['created_at'])
    op.create_index('ix_stock_movements_user_id', 'stock_movements', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_stock_movements_user_id', table_name='stock_movements')
    op.drop_index('ix_stock_movements_created_at', table_name='stock_movements')
    op.drop_index('ix_stock_movements_operation_type', table_name='stock_movements')
    op.drop_index('ix_stock_movements_product_id', table_name='stock_movements')
    
    # Drop table
    op.drop_table('stock_movements')
