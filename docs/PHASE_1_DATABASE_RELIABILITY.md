# Phase 1 Database Reliability

The application no longer mutates a configured database at startup. Migrations, curriculum synchronization, and administrator setup are explicit operational actions. Test fixtures use a disposable SQLite file, enable foreign keys, and compare the canonical database before and after the test session. The canonical SHA-256 remained `B02122C54FB680C7B7AA7F5141543BBCB57B258EAB9FB64D333A15322E5D687C`.
