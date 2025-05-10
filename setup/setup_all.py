import sqlite3
import argparse
import os
from pathlib import Path
from integrations.dnd5e.srd_item_loader import main as load_srd_items
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'rpg-shopkeeper.db'
SCHEMA_SQL = BASE_DIR / 'database' / 'schema.sql'
SEED_SQL = BASE_DIR / 'database' / 'seed_data.sql'


def reset_database():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print('🗑️ Old database removed.')
    else:
        print('⚠️ No existing DB found. Proceeding fresh.')


def run_sql_script(path: Path):
    with sqlite3.connect(DB_PATH) as conn:
        with open(path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        print(f'📄 Executed: {path.name}')


def main():
    parser = argparse.ArgumentParser(description='Set up RPG Shopkeeper DB')
    parser.add_argument('--reset', action='store_true', help=
        'Delete and recreate database')
    parser.add_argument('--no-srd', action='store_true', help=
        'Skip SRD item loading')
    parser.add_argument('--no-seed', action='store_true', help=
        'Skip core seed data')
    parser.add_argument('--only-srd', action='store_true', help=
        'Only run SRD item loader')
    args = parser.parse_args()
    if args.only_srd:
        load_srd_items()
        return
    if args.reset:
        reset_database()
    print('📦 Setting up schema...')
    run_sql_script(SCHEMA_SQL)
    if not args.no_srd:
        print('🧙 Loading SRD items...')
        load_srd_items()
    if not args.no_seed:
        print('🌱 Seeding user/shop/party data...')
        run_sql_script(SEED_SQL)
    print('✅ Setup complete.')


if __name__ == '__main__':
    main()
