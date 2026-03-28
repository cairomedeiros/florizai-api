"""add RLS policies

Revision ID: 894823f02e0b
Revises: 9f6429ddf41f
Create Date: 2026-03-28 16:25:47.764588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '894823f02e0b'
down_revision: Union[str, Sequence[str], None] = '9f6429ddf41f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # plants table RLS policies
    op.execute("ALTER TABLE public.plants ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY "users select own plants"
        ON public.plants FOR SELECT USING (user_id = auth.uid())
    """)
    op.execute("""
        CREATE POLICY "users insert own plants"
        ON public.plants FOR INSERT WITH CHECK (user_id = auth.uid())
    """)
    op.execute("""
        CREATE POLICY "users update own plants"
        ON public.plants FOR UPDATE USING (user_id = auth.uid())
    """)
    op.execute("""
        CREATE POLICY "users delete own plants"
        ON public.plants FOR DELETE USING (user_id = auth.uid())
    """)
    # profiles table RLS policies
    op.execute("ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY "users select own profiles"
        ON public.profiles FOR SELECT USING (user_id = auth.uid())
    """)
    op.execute("""
        CREATE POLICY "users insert own profiles"
        ON public.profiles FOR INSERT WITH CHECK (user_id = auth.uid())
    """)
    op.execute("""
        CREATE POLICY "users update own profiles"
        ON public.profiles FOR UPDATE USING (user_id = auth.uid())
    """)
    # chats table RLS policies
    op.execute("ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY "users select own chats"
        ON public.chats FOR SELECT USING (user_id = auth.uid())
    """)
    op.execute("""
        CREATE POLICY "users insert own chats"
        ON public.chats FOR INSERT WITH CHECK (user_id = auth.uid())
    """)
    op.execute("""
        CREATE POLICY "users delete own chats"
        ON public.chats FOR DELETE USING (user_id = auth.uid())
    """)
    # messages table RLS policies (no user_id — traverse through chats)
    op.execute("ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY "users select own messages"
        ON public.messages FOR SELECT
        USING (chat_id IN (SELECT id FROM public.chats WHERE user_id = auth.uid()))
    """)
    op.execute("""
        CREATE POLICY "users insert own messages"
        ON public.messages FOR INSERT
        WITH CHECK (chat_id IN (SELECT id FROM public.chats WHERE user_id = auth.uid()))
    """)
    op.execute("""
        CREATE POLICY "users delete own messages"
        ON public.messages FOR DELETE
        USING (chat_id IN (SELECT id FROM public.chats WHERE user_id = auth.uid()))
    """)
    # plant_pictures table RLS policies (no user_id — traverse through plants)
    op.execute("ALTER TABLE public.plant_pictures ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY "users select own plant pictures"
        ON public.plant_pictures FOR SELECT
        USING (plant_id IN (SELECT id FROM public.plants WHERE user_id = auth.uid()))
    """)
    op.execute("""
        CREATE POLICY "users insert own plant pictures"
        ON public.plant_pictures FOR INSERT
        WITH CHECK (plant_id IN (SELECT id FROM public.plants WHERE user_id = auth.uid()))
    """)
    op.execute("""
        CREATE POLICY "users delete own plant pictures"
        ON public.plant_pictures FOR DELETE
        USING (plant_id IN (SELECT id FROM public.plants WHERE user_id = auth.uid()))
    """)
    # watering_events table RLS policies (no user_id — traverse through plants)
    op.execute("ALTER TABLE public.watering_events ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY "users select own watering events"
        ON public.watering_events FOR SELECT
        USING (plant_id IN (SELECT id FROM public.plants WHERE user_id = auth.uid()))
    """)
    op.execute("""
        CREATE POLICY "users insert own watering events"
        ON public.watering_events FOR INSERT
        WITH CHECK (plant_id IN (SELECT id FROM public.plants WHERE user_id = auth.uid()))
    """)
    op.execute("""
        CREATE POLICY "users delete own watering events"
        ON public.watering_events FOR DELETE
        USING (plant_id IN (SELECT id FROM public.plants WHERE user_id = auth.uid()))
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # plants table RLS policies
    op.execute('DROP POLICY IF EXISTS "users select own plants" ON public.plants')
    op.execute('DROP POLICY IF EXISTS "users insert own plants" ON public.plants')
    op.execute('DROP POLICY IF EXISTS "users update own plants" ON public.plants')
    op.execute('DROP POLICY IF EXISTS "users delete own plants" ON public.plants')
    op.execute("ALTER TABLE public.plants DISABLE ROW LEVEL SECURITY")
    # profiles table RLS policies
    op.execute('DROP POLICY IF EXISTS "users select own profiles" ON public.profiles')
    op.execute('DROP POLICY IF EXISTS "users insert own profiles" ON public.profiles')
    op.execute('DROP POLICY IF EXISTS "users update own profiles" ON public.profiles')
    op.execute("ALTER TABLE public.profiles DISABLE ROW LEVEL SECURITY")
    # chats table RLS policies
    op.execute('DROP POLICY IF EXISTS "users select own chats" ON public.chats')
    op.execute('DROP POLICY IF EXISTS "users insert own chats" ON public.chats')
    op.execute('DROP POLICY IF EXISTS "users delete own chats" ON public.chats')
    op.execute("ALTER TABLE public.chats DISABLE ROW LEVEL SECURITY")
    # messages table RLS policies
    op.execute('DROP POLICY IF EXISTS "users select own messages" ON public.messages')
    op.execute('DROP POLICY IF EXISTS "users insert own messages" ON public.messages')
    op.execute('DROP POLICY IF EXISTS "users delete own messages" ON public.messages')
    op.execute("ALTER TABLE public.messages DISABLE ROW LEVEL SECURITY")
    # plant_pictures table RLS policies
    op.execute('DROP POLICY IF EXISTS "users select own plant pictures" ON public.plant_pictures')
    op.execute('DROP POLICY IF EXISTS "users insert own plant pictures" ON public.plant_pictures')
    op.execute('DROP POLICY IF EXISTS "users delete own plant pictures" ON public.plant_pictures')
    op.execute("ALTER TABLE public.plant_pictures DISABLE ROW LEVEL SECURITY")
    # watering_events table RLS policies
    op.execute('DROP POLICY IF EXISTS "users select own watering events" ON public.watering_events')
    op.execute('DROP POLICY IF EXISTS "users insert own watering events" ON public.watering_events')
    op.execute('DROP POLICY IF EXISTS "users delete own watering events" ON public.watering_events')
    op.execute("ALTER TABLE public.watering_events DISABLE ROW LEVEL SECURITY")
